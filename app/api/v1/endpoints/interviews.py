from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from typing import List
import os
import base64
import uuid
import re
import google.generativeai as genai
import google.cloud.texttospeech as tts
import whisper
import anthropic
from pydub import AudioSegment
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app import crud, models
from app.api import deps
from app.schemas.interview import InterviewCreate, QuestionCreate, AnswerCreate, InterviewSession
from app.schemas.analysis import Analysis, AnalysisCreate

load_dotenv()

if os.path.exists("ffmpeg.exe"):
    AudioSegment.converter = os.path.abspath("ffmpeg.exe")

router = APIRouter()

@router.post("/", response_model=InterviewSession)
def create_interview_session(
    *,
    db: Session = Depends(deps.get_db),
    resume_id: int,
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Create a new interview session.
    - Generates questions based on the resume.
    - Creates an interview record in the database.
    - Saves the generated questions to the database.
    """
    resume = crud.resume.get(db, resume_id=resume_id)
    if not resume or resume.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")

    content = resume.content or ""
    if not content:
        raise HTTPException(status_code=400, detail="Resume content is empty")

    try:
        google_api_key = os.getenv("GOOGLE_API_KEY")
        gemini_model_name = os.getenv("GEMINI_MODEL")
        if not google_api_key or not gemini_model_name:
            raise HTTPException(status_code=500, detail="AI model configuration missing")

        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel(gemini_model_name)
        prompt = f"""당신은 지원자의 역량을 깊이 있게 파악하려는 날카로운 면접관입니다. 당신의 임무는 지원자의 자기소개서와 일반적인 면접 질문을 조합하여, 핵심 역량과 경험의 진위, 그리고 문제 해결 능력을 종합적으로 검증할 수 있는 면접 질문 목록을 생성하는 것입니다. 반드시 아래 규칙과 출력 형식을 엄격하게 준수하여 답변해야 합니다.\n\n$$규칙$$\n\n질문 유형 조합: 질문 목록은 아래 두 가지 유형을 반드시 조합하여 생성해야 합니다.\n\n자기소개서 기반 질문: 지원자의 자기소개서에 명시된 경험, 역량, 성과, 장단점 등을 깊이 있게 파고드는 질문입니다.\n\n공통 질문: 모든 지원자에게 물어볼 수 있는 직무/회사 관련 질문이나 인성/가치관 질문입니다. (예: 입사 후 포부, 지원 동기, 마지막으로 하고 싶은 말 등)\n\n질문 개수: 자기소개서 내용의 분량과 깊이를 고려하여, 두 유형을 합쳐 최소 5개에서 최대 15개의 질문을 유동적으로 생성합니다.\n\n압박 질문 포함: 전체 질문 중 1~2개는 지원자의 논리력, 위기 대처 능력 등을 확인하기 위한 압박 질문(꼬리 질문, 반대 상황 가정 등)을 포함해야 합니다. 압박 질문은 🌶️ 아이콘으로 명확히 표시하세요.\n\n형식 준수: 아래에 제시된 **$$출력 형식$$**의 구조와 순서를 반드시 지켜야 합니다. 공통 질문 앞에는 [공통] 말머리를 붙여주세요.\n\n$$출력 형식$$\n\n예상 면접 질문 리스트\n\n(자기소개서 내용에 기반한 일반 질문 1)\n\n$$공통$$\n\n (모든 지원자에게 할 수 있는 직무/회사 관련 공통 질문)\n\n🌶️ (자기소개서 내용에 기반한 압박 질문)\n\n(이하 질문들을 규칙에 맞게 생성...)\n\n$$공통$$\n\n (모든 지원자에게 할 수 있는 인성/가치관 관련 공통 질문)\n\n이제 이 지침에 따라 아래 자기소개서를 분석하고 예상 면접 질문을 생성해 주세요.\n\n$$지원자 자기소개서$$\n\n\n{content}\n"""
        response = model.generate_content(prompt)
        
        raw_questions = response.text.split('\n')
        questions_text = []
        for q in raw_questions:
            q = q.strip()
            
            # Skip separators, titles, and empty lines
            if not q or "예상 면접 질문 리스트" in q or q == "$$공통$$":
                continue
                
            # Clean the question text
            q = re.sub(r'^\d+\.\s*', '', q)  # Remove leading numbers like "1. "
            q = q.replace('🌶️', '').strip()    # Remove chili pepper and strip
            
            # Add to the list if it's a valid question
            if q:
                questions_text.append(q)

        if not questions_text:
            raise HTTPException(status_code=500, detail="Failed to generate questions.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI question generation failed: {str(e)}")

    # Create interview session in DB
    interview_create = InterviewCreate(user_id=current_user.user_id, resume_id=resume_id)
    interview = crud.interview.create_interview(db=db, obj_in=interview_create)

    # Save questions to DB
    for q_text in questions_text:
        question_create = QuestionCreate(interview_id=interview.interview_id, question_text=q_text)
        crud.interview.create_question(db=db, obj_in=question_create)

    return InterviewSession(interview_id=interview.interview_id, questions=questions_text)


@router.get("/{interview_id}/results", response_model=Analysis)
def get_interview_results(
    interview_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Get the comprehensive analysis results for a finished interview.
    """
    interview = crud.interview.get_interview(db, interview_id=interview_id)
    if not interview or interview.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Interview not found or access denied")

    # Check if analysis already exists
    analysis = crud.analysis.get_analysis_by_interview(db, interview_id=interview_id)
    if analysis:
        return analysis

    # Reconstruct the conversation
    questions = crud.interview.get_questions_by_interview(db, interview_id=interview_id)
    conversation_history = ""
    for q in questions:
        conversation_history += f"Q: {q.question_text}\n"
        if q.answers:
            conversation_history += f"A: {q.answers[0].answer_text}\n\n"

    if not conversation_history:
        raise HTTPException(status_code=400, detail="No questions or answers found for this interview.")

    # Get feedback from Claude
    api_key = os.getenv("CLAUDE_API_KEY")
    claude_model = os.getenv("CLAUDE_MODEL")
    if not api_key or not claude_model:
        raise HTTPException(status_code=500, detail="Claude API configuration missing.")

    # Clean the key just in case
    api_key = api_key.strip().strip('"').strip("'")

import httpx

# ... (other imports)

# ... (other functions)

@router.get("/{interview_id}/results", response_model=Analysis)
async def get_interview_results(
    # ... (function signature)
):
    # ... (code to get conversation history)

    api_key = os.getenv("CLAUDE_API_KEY")
    claude_model = os.getenv("CLAUDE_MODEL")
    if not api_key or not claude_model:
        raise HTTPException(status_code=500, detail="Claude API configuration missing.")
    api_key = api_key.strip().strip('"').strip("'")

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    payload = {
        "model": claude_model,
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": f"""... (your full prompt here) ..."""
            }
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=120.0
            )
            response.raise_for_status()
            
            response_data = response.json()
            feedback_text = response_data['content'][0]['text']

        # Save analysis to DB
        analysis_create = AnalysisCreate(interview_id=interview_id, feedback_text=feedback_text)
        new_analysis = crud.analysis.create_analysis(db=db, obj_in=analysis_create)
        return new_analysis

    except httpx.HTTPStatusError as e:
        print(f"Claude API request failed with status {e.response.status_code} and response: {e.response.text}")
        raise HTTPException(status_code=500, detail=f"Error calling Claude API: {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@router.websocket("/ws/{interview_id}")
async def websocket_interview(
    websocket: WebSocket,
    interview_id: int,
    token: str,
):
    await websocket.accept()
    db: Session = SessionLocal()
    try:
        # Authenticate user from token
        try:
            user = deps.get_user_from_token(db=db, token=token)
        except HTTPException as e:
            await websocket.send_json({"type": "error", "message": f"Authentication failed: {e.detail}"})
            await websocket.close(code=1008)
            return

        # Authorize: Check if the user owns the interview
        interview = crud.interview.get_interview(db, interview_id=interview_id)
        if not interview or interview.user_id != user.user_id:
            await websocket.send_json({"type": "error", "message": "Interview not found or access denied."})
            await websocket.close(code=1008)
            return

        questions = crud.interview.get_questions_by_interview(db, interview_id=interview_id)
        if not questions:
            await websocket.send_json({"type": "error", "message": "Interview questions not found."})
            await websocket.close(code=1008)
            return

        await websocket.send_json({"type": "system", "message": f"Interview session started. {len(questions)} questions will be asked.", "status": "connected"})
        
        for index, question in enumerate(questions):
            await websocket.send_json({"type": "question", "text": question.question_text, "question_number": index + 1, "total_questions": len(questions)})
            
            try:
                tts_model_name = os.getenv("TTS_MODEL_NAME", "gemini-2.5-flash-tts")
                tts_voice_name = os.getenv("TTS_VOICE_NAME", "ko-KR-Neural2-C")
                
                tts_client = tts.TextToSpeechClient()
                synthesis_input = tts.SynthesisInput(text=question.question_text)
                voice = tts.VoiceSelectionParams(
                    language_code="ko-KR",
                    name=tts_voice_name,
                    model_name=tts_model_name
                )
                audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)
                response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
                await websocket.send_bytes(response.audio_content)
            except Exception as tts_error:
                print(f"TTS Error: {tts_error}")
                await websocket.send_json({"type": "error", "message": "Could not generate audio for the question."})

            print("Waiting to receive audio data as base64 text...")
            base64_audio_data = await websocket.receive_text()
            print("Base64 text received. Decoding...")
            audio_bytes = base64.b64decode(base64_audio_data)
            print(f"Decoded {len(audio_bytes)} bytes. Proceeding to transcription.")

            temp_file_path = f"temp_{uuid.uuid4()}.wav"
            try:
                if 'whisper_model' not in globals():
                    globals()['whisper_model'] = whisper.load_model("small")
                with open(temp_file_path, "wb") as f:
                    f.write(audio_bytes)
                result = globals()['whisper_model'].transcribe(temp_file_path, language="ko")
                print(f"Whisper transcription result: {result}")  # For debugging
                answer_text = result.get("text", "")
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            
            # Save the answer to the database
            answer_create = AnswerCreate(question_id=question.question_id, answer_text=answer_text)
            crud.interview.create_answer(db=db, obj_in=answer_create)
            
            await websocket.send_json({"type": "system", "message": f"Answer for question {index + 1} received.", "status": "processing"})

        await websocket.send_json({"type": "system", "message": "Interview finished. Thank you.", "status": "finished"})

    except WebSocketDisconnect:
        print(f"Client for interview {interview_id} disconnected.")
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        db.close()
        await websocket.close()