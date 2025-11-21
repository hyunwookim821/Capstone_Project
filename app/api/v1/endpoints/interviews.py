from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, UploadFile, File
from typing import List, Any, Dict
import os
import base64
import uuid
import re
import io
import json
import asyncio
import google.generativeai as genai
import google.cloud.texttospeech as tts
import whisper
import anthropic
import httpx
from pydub import AudioSegment
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app import crud, models
from app.api import deps
from app.schemas.interview import InterviewCreate, QuestionCreate, AnswerCreate, InterviewSession, VideoAnalysisRequest
from app.schemas.analysis import Analysis, AnalysisCreate
from app.schemas.video_analysis import VideoAnalysisCreate
from app.utils.audio_analysis import analyze_whisper_result
from app.utils.video_analysis import analyze_video_landmarks
from app.prompts import get_question_generation_prompt, get_interview_analysis_prompt

load_dotenv()

if os.path.exists("ffmpeg.exe"):
    AudioSegment.converter = os.path.abspath("ffmpeg.exe")

router = APIRouter()

# Module-level Whisper model cache (better than using globals())
_whisper_model = None

def get_whisper_model():
    """Lazy-load and cache the Whisper model."""
    global _whisper_model
    if _whisper_model is None:
        print("Loading Whisper model for the first time...")
        _whisper_model = whisper.load_model("small")
        print("Whisper model loaded successfully.")
    return _whisper_model

def clean_text_for_tts(text: str) -> str:
    """
    TTS 음성 생성을 위해 텍스트를 정제합니다.
    이모티콘, 태그, 특수 기호 등을 제거합니다.

    Args:
        text: 원본 질문 텍스트

    Returns:
        정제된 텍스트
    """
    if not text:
        return text

    # 1. [공통], [압박] 같은 대괄호 태그와 뒤의 공백 제거
    text = re.sub(r'\[.*?\]\s*', '', text)

    # 2. 🌶️ 같은 특정 이모티콘 제거 (더 안전한 방법)
    # 일반적인 이모티콘만 제거
    emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001F9FF"  # 대부분의 이모티콘
        "\U00002600-\U000027BF"  # 기타 기호
        "]+",
        flags=re.UNICODE
    )
    text = emoji_pattern.sub('', text)

    # 3. 연속된 공백을 하나로 축소
    text = re.sub(r'\s+', ' ', text)

    # 4. 앞뒤 공백 제거
    text = text.strip()

    # 5. 안전장치: 텍스트가 비어있으면 경고
    if not text:
        print(f"WARNING: clean_text_for_tts resulted in empty string!")
        return "질문을 준비 중입니다"  # 폴백 텍스트

    return text

async def cleanup_audio_files_after_delay(interview_id: int, delay_minutes: int = 5):
    """
    면접 종료 후 일정 시간(기본 5분) 후 해당 면접의 오디오 파일들을 자동으로 삭제합니다.

    Args:
        interview_id: 면접 ID
        delay_minutes: 삭제 전 대기 시간 (분)
    """
    await asyncio.sleep(delay_minutes * 60)  # 분을 초로 변환

    print(f"Starting audio file cleanup for interview {interview_id} after {delay_minutes} minute(s) delay...")

    db = SessionLocal()
    try:
        # 해당 면접의 모든 답변 조회
        answers = crud.interview.get_answers_by_interview(db, interview_id=interview_id)

        deleted_count = 0
        error_count = 0

        for answer in answers:
            if answer.audio_path:
                try:
                    if os.path.exists(answer.audio_path):
                        os.remove(answer.audio_path)
                        deleted_count += 1
                        print(f"Deleted audio file: {answer.audio_path}")
                    else:
                        print(f"Audio file not found (already deleted?): {answer.audio_path}")
                except Exception as e:
                    error_count += 1
                    print(f"Error deleting audio file {answer.audio_path}: {e}")

        print(f"Audio cleanup completed for interview {interview_id}: {deleted_count} files deleted, {error_count} errors")
    except Exception as e:
        print(f"Error during audio cleanup for interview {interview_id}: {e}")
    finally:
        db.close()

@router.post("/", response_model=InterviewSession)
def create_interview_session(
    *,
    db: Session = Depends(deps.get_db),
    resume_id: int,
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Creates an interview session.
    It uses questions already associated with the resume.
    If no questions exist, it generates them on the fly and saves them to the resume.
    """
    resume = crud.resume.get(db, resume_id=resume_id)
    if not resume or resume.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")

    questions_text = []
    if resume.generated_questions:
        print(f"Found {len(resume.generated_questions)} existing questions for resume {resume_id}.")
        questions_text = [q.question_text for q in resume.generated_questions]
    else:
        print(f"No questions found for resume {resume_id}. Generating new ones.")
        content = resume.content or ""
        if not content:
            raise HTTPException(status_code=400, detail="Resume content is empty, cannot generate questions.")

        try:
            google_api_key = os.getenv("GOOGLE_API_KEY")
            gemini_model_name = os.getenv("GEMINI_MODEL")
            if not google_api_key or not gemini_model_name:
                raise HTTPException(status_code=500, detail="AI model configuration missing")

            genai.configure(api_key=google_api_key)
            model = genai.GenerativeModel(gemini_model_name)

            # 개선된 프롬프트 모듈 사용
            prompt = get_question_generation_prompt(content)
            response = model.generate_content(prompt)

            # JSON 형식으로 파싱 시도
            temp_questions = []
            try:
                # 응답에서 JSON 부분 추출
                response_text = response.text.strip()
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                else:
                    json_str = response_text

                parsed_response = json.loads(json_str)
                # 태그와 이모티콘 유지 (프론트엔드에서 질문 유형 구분용)
                temp_questions = [q["text"] for q in parsed_response.get("questions", [])]
            except (json.JSONDecodeError, KeyError) as json_error:
                # JSON 파싱 실패 시 기존 방식으로 폴백
                print(f"JSON parsing failed, falling back to text split: {json_error}")
                raw_questions = response.text.split('\n')
                for q in raw_questions:
                    q = q.strip()
                    if not q or "예상 면접 질문 리스트" in q:
                        continue
                    # 번호만 제거, 태그와 이모티콘은 유지
                    q = re.sub(r'^\d+\.\s*', '', q).strip()
                    if q:
                        temp_questions.append(q)
            
            if not temp_questions:
                raise HTTPException(status_code=500, detail="Failed to generate questions.")
            
            # Save the newly generated questions to the resume
            for q_text in temp_questions:
                q_in = {"resume_id": resume.resume_id, "question_text": q_text}
                crud.generated_question.create(db=db, obj_in=q_in)
            
            questions_text = temp_questions
            print(f"Generated and saved {len(questions_text)} new questions for resume {resume_id}.")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI question generation failed: {str(e)}")

    interview_create = InterviewCreate(user_id=current_user.user_id, resume_id=resume_id)
    interview = crud.interview.create_interview(db=db, obj_in=interview_create)

    for q_text in questions_text:
        question_create = QuestionCreate(interview_id=interview.interview_id, question_text=q_text)
        crud.interview.create_question(db=db, obj_in=question_create)

    return InterviewSession(interview_id=interview.interview_id, questions=questions_text)


@router.get("/{interview_id}/results", response_model=Analysis)
async def get_interview_results(
    interview_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Get the comprehensive analysis results for a finished interview.
    This is the single trigger for generating the final report.
    """
    interview = crud.interview.get_interview(db, interview_id=interview_id)
    if not interview or interview.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Interview not found or access denied")

    # If a full analysis already exists, return it to prevent re-generation.
    analysis = crud.analysis.get_analysis_by_interview(db, interview_id=interview_id)
    if analysis:
        return analysis

    # --- Gather All Data ---
    resume = crud.resume.get(db, resume_id=interview.resume_id)
    resume_content = resume.content if resume else ""

    questions = crud.interview.get_questions_by_interview(db, interview_id=interview_id)
    conversation_history = ""
    for q in questions:
        conversation_history += f"Q: {q.question_text}\n"
        if q.answers:
            conversation_history += f"A: {q.answers[0].answer_text}\n\n"

    if not conversation_history:
        raise HTTPException(status_code=400, detail="No questions or answers found for this interview.")

    # --- Audio Analysis ---
    audio_analysis_summary = ""
    total_speech_rate = 0
    total_silence_ratio = 0
    num_answers_with_audio = 0
    avg_speech_rate = None
    avg_silence_ratio = None

    for q in questions:
        if q.answers and q.answers[0].whisper_result:
            answer = q.answers[0]
            speech_rate, silence_ratio = analyze_whisper_result(answer.whisper_result)
            total_speech_rate += speech_rate
            total_silence_ratio += silence_ratio
            num_answers_with_audio += 1
    
    if num_answers_with_audio > 0:
        avg_speech_rate = total_speech_rate / num_answers_with_audio
        avg_silence_ratio = total_silence_ratio / num_answers_with_audio
        audio_analysis_summary = f"""
---
### **음성 분석 (말하기 습관)**
*   **평균 말하기 속도:** {avg_speech_rate:.2f} WPM (Words Per Minute)
*   **머뭇거림 (침묵) 비율:** {avg_silence_ratio:.2f}%

(참고: 이상적인 말하기 속도는 분당 130-160 단어(WPM)이며, 침묵 비율이 높을수록 생각이 길어지거나 자신감이 부족해 보일 수 있습니다.)
"""

    # --- Video Analysis ---
    video_analysis_summary = ""
    video_analysis_data = crud.video_analysis.get_by_interview_id(db, interview_id=interview_id)
    gaze_stability = None
    expression_stability = None
    posture_stability = None

    if video_analysis_data:
        gaze_stability = video_analysis_data.gaze_stability
        expression_stability = video_analysis_data.expression_stability
        posture_stability = video_analysis_data.posture_stability
        video_analysis_summary = f"""
---
### **영상 분석 (시각적 태도)**
*   **시선 안정성:** {gaze_stability:.4f} (낮을수록 안정적)
*   **표정 안정성:** {expression_stability:.4f} (낮을수록 안정적)
*   **자세 안정성:** {posture_stability:.4f} (낮을수록 안정적)

(참고: 이 지표들은 신체의 미세한 움직임의 표준편차를 나타내며, 수치가 낮을수록 시선, 표정, 자세가 안정적이고 자신감 있어 보임을 의미합니다.)
"""

    # --- AI Feedback Generation ---
    print(f"Starting AI feedback generation for interview {interview_id}")
    print(f"- Resume content length: {len(resume_content)}")
    print(f"- Conversation history length: {len(conversation_history)}")
    print(f"- Audio data: speech_rate={avg_speech_rate}, silence_ratio={avg_silence_ratio}")
    print(f"- Video data: gaze={gaze_stability}, expression={expression_stability}, posture={posture_stability}")

    api_key = os.getenv("CLAUDE_API_KEY")
    claude_model = os.getenv("CLAUDE_MODEL")
    if not api_key or not claude_model:
        raise HTTPException(status_code=500, detail="Claude API configuration missing.")
    api_key = api_key.strip().strip('"').strip("'")

    # 개선된 프롬프트 모듈 사용
    prompt = get_interview_analysis_prompt(
        resume_content=resume_content,
        conversation_history=conversation_history,
        audio_analysis_summary=audio_analysis_summary,
        video_analysis_summary=video_analysis_summary,
        avg_speech_rate=avg_speech_rate,
        avg_silence_ratio=avg_silence_ratio,
        gaze_stability=gaze_stability,
        expression_stability=expression_stability,
        posture_stability=posture_stability
    )

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    payload = {
        "model": claude_model,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        print(f"Calling Claude API for interview {interview_id}...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=240.0  # 180초 → 240초(4분)로 연장
            )
            print(f"Claude API responded with status {response.status_code}")
            response.raise_for_status()

            response_data = response.json()
            feedback_text = response_data['content'][0]['text']
            print(f"Successfully received feedback ({len(feedback_text)} characters)")

        analysis_create = AnalysisCreate(
            interview_id=interview_id,
            feedback_text=feedback_text,
            speech_rate=avg_speech_rate,
            silence_ratio=avg_silence_ratio,
            gaze_stability=gaze_stability,
            expression_stability=expression_stability,
            posture_stability=posture_stability
        )

        try:
            new_analysis = crud.analysis.create_analysis(db=db, obj_in=analysis_create)
            return new_analysis
        except IntegrityError:
            # Another request already created the analysis (race condition)
            # Rollback and fetch the existing analysis
            db.rollback()
            print(f"Analysis for interview {interview_id} already exists (race condition detected). Fetching existing analysis.")
            existing_analysis = crud.analysis.get_analysis_by_interview(db, interview_id=interview_id)
            if existing_analysis:
                return existing_analysis
            else:
                # This should rarely happen
                raise HTTPException(status_code=500, detail="Failed to create or retrieve analysis")

    except httpx.HTTPStatusError as e:
        error_message = f"Claude API request failed with status {e.response.status_code} and response: {e.response.text}"
        print(error_message)
        raise HTTPException(status_code=500, detail=error_message)
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        print(error_message)
        raise HTTPException(status_code=500, detail=error_message)


@router.websocket("/ws/{interview_id}")
async def websocket_interview(
    websocket: WebSocket,
    interview_id: int,
    token: str,
):
    db: Session = SessionLocal()
    try:
        # Authenticate user BEFORE accepting the WebSocket connection
        try:
            user = deps.get_user_from_token(db=db, token=token)
        except HTTPException as e:
            print(f"WebSocket authentication failed for interview {interview_id}: {e.detail}")
            await websocket.close(code=1008, reason=f"Authentication failed: {e.detail}")
            return

        interview = crud.interview.get_interview(db, interview_id=interview_id)
        if not interview or interview.user_id != user.user_id:
            print(f"WebSocket access denied for interview {interview_id}, user {user.user_id}")
            await websocket.close(code=1008, reason="Interview not found or access denied")
            return

        # Accept connection only after successful authentication and authorization
        await websocket.accept()

        questions = crud.interview.get_questions_by_interview(db, interview_id=interview_id)
        if not questions:
            await websocket.send_json({"type": "error", "message": "Interview questions not found."})
            await websocket.close(code=1008)
            return

        await websocket.send_json({"type": "system", "message": f"Interview session started. {len(questions)} questions will be asked.", "status": "connected"})

        # 생성된 오디오 파일 경로를 추적 (에러 발생 시 정리용)
        created_audio_files = []

        for index, question in enumerate(questions):
            await websocket.send_json({"type": "question", "text": question.question_text, "question_number": index + 1, "total_questions": len(questions)})
            
            try:
                tts_model_name = os.getenv("TTS_MODEL_NAME", "gemini-2.5-flash-tts")
                tts_voice_name = os.getenv("TTS_VOICE_NAME", "Charon")  # Gemini TTS voice

                # TTS용 텍스트 정제 (이모티콘, 태그 제거)
                cleaned_text = clean_text_for_tts(question.question_text)
                print(f"Original question: {question.question_text}")
                print(f"Cleaned for TTS: {cleaned_text}")

                tts_client = tts.TextToSpeechClient()

                # Gemini TTS 모델 체크
                is_gemini_tts = "gemini" in tts_model_name.lower()

                # synthesis_input 생성
                if is_gemini_tts:
                    # Gemini TTS: prompt 사용 시도
                    try:
                        style_prompt = os.getenv(
                            "TTS_STYLE_PROMPT",
                            "당신은 경험이 풍부한 전문 면접관입니다. 친절하면서도 전문적인 톤으로, "
                            "명확하고 또렷하게 질문을 전달합니다. 아주 살짝 빠른 속도로 말하며, "
                            "지원자가 편안하게 답변할 수 있도록 격려적인 분위기를 조성합니다."
                        )
                        synthesis_input = tts.SynthesisInput(
                            text=cleaned_text,
                            prompt=style_prompt
                        )
                        print(f"Attempting Gemini TTS with style prompt")
                    except:
                        # Fallback: prompt 없이
                        synthesis_input = tts.SynthesisInput(text=cleaned_text)
                        print(f"Gemini TTS fallback: using text only")
                else:
                    # Standard TTS: text만 사용
                    synthesis_input = tts.SynthesisInput(text=cleaned_text)
                    print(f"Using Standard TTS")

                # Voice 설정
                if is_gemini_tts:
                    # Gemini TTS 음성은 model_name 필수
                    voice = tts.VoiceSelectionParams(
                        language_code="ko-KR",
                        name=tts_voice_name,
                        model_name=tts_model_name
                    )
                else:
                    # Standard TTS는 model_name 불필요
                    voice = tts.VoiceSelectionParams(
                        language_code="ko-KR",
                        name=tts_voice_name
                    )

                audio_config = tts.AudioConfig(
                    audio_encoding=tts.AudioEncoding.MP3
                )

                response = tts_client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )

                await websocket.send_bytes(response.audio_content)
                print(f"TTS audio sent successfully using {tts_model_name} with voice {tts_voice_name}")
            except Exception as tts_error:
                print(f"TTS Error: {tts_error}")
                print(f"TTS Error details: {type(tts_error).__name__}: {str(tts_error)}")
                await websocket.send_json({"type": "error", "message": "Could not generate audio for the question."})

            print("Waiting to receive audio data as base64 text...")
            base64_audio_data = await websocket.receive_text()
            print("Base64 text received. Decoding...")
            audio_bytes = base64.b64decode(base64_audio_data)
            print(f"Decoded {len(audio_bytes)} bytes. Proceeding to conversion and transcription.")

            audio_dir = "audio_files"
            os.makedirs(audio_dir, exist_ok=True)

            audio_filename = f"{uuid.uuid4()}.wav"
            audio_path = os.path.join(audio_dir, audio_filename)
            audio_file_created = False
            result = None  # Initialize to avoid NameError

            try:
                # Load audio from bytes and export as WAV
                audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
                audio_segment.export(audio_path, format="wav")
                audio_file_created = True
                created_audio_files.append(audio_path)  # 추적 리스트에 추가
                print(f"Successfully converted and saved audio to {audio_path}")

                # Use the cached Whisper model
                model = get_whisper_model()
                result = model.transcribe(audio_path, language="ko")
                print(f"Whisper transcription result: {result}")
                answer_text = result.get("text", "")
            except Exception as e:
                print(f"Error during audio processing or transcription: {e}")
                answer_text = ""
                # 에러 발생 시 생성된 파일 즉시 삭제
                if audio_file_created and os.path.exists(audio_path):
                    try:
                        os.remove(audio_path)
                        created_audio_files.remove(audio_path)
                        print(f"Cleaned up audio file after error: {audio_path}")
                    except Exception as cleanup_error:
                        print(f"Failed to cleanup audio file {audio_path}: {cleanup_error}")

            # DB 저장
            try:
                answer_create = AnswerCreate(
                    question_id=question.question_id,
                    answer_text=answer_text,
                    audio_path=audio_path if audio_file_created else None,
                    whisper_result=result  # Save the full result (None if error occurred)
                )
                crud.interview.create_answer(db=db, obj_in=answer_create)
            except Exception as db_error:
                print(f"Error saving answer to database: {db_error}")
                # DB 저장 실패 시 오디오 파일 정리
                if audio_file_created and os.path.exists(audio_path):
                    try:
                        os.remove(audio_path)
                        if audio_path in created_audio_files:
                            created_audio_files.remove(audio_path)
                        print(f"Cleaned up audio file after DB error: {audio_path}")
                    except Exception as cleanup_error:
                        print(f"Failed to cleanup audio file {audio_path}: {cleanup_error}")
                raise  # Re-raise to trigger WebSocket error handling
            
            await websocket.send_json({"type": "system", "message": f"Answer for question {index + 1} received.", "status": "processing"})

        await websocket.send_json({"type": "system", "message": "Interview finished. Thank you.", "status": "finished"})

    except WebSocketDisconnect:
        print(f"Client for interview {interview_id} disconnected.")
        # 연결 중단 시 추적 중인 파일들 즉시 정리
        if 'created_audio_files' in locals():
            for audio_file in created_audio_files:
                try:
                    if os.path.exists(audio_file):
                        os.remove(audio_file)
                        print(f"Cleaned up audio file after disconnect: {audio_file}")
                except Exception as cleanup_error:
                    print(f"Failed to cleanup audio file {audio_file}: {cleanup_error}")
    except Exception as e:
        print(f"Unexpected error in WebSocket for interview {interview_id}: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass  # WebSocket might be closed already
        # 에러 발생 시에도 추적 중인 파일들 즉시 정리
        if 'created_audio_files' in locals():
            for audio_file in created_audio_files:
                try:
                    if os.path.exists(audio_file):
                        os.remove(audio_file)
                        print(f"Cleaned up audio file after error: {audio_file}")
                except Exception as cleanup_error:
                    print(f"Failed to cleanup audio file {audio_file}: {cleanup_error}")
    finally:
        # 정상 종료된 경우에만 5분 후 자동 삭제 예약
        # (중단/에러 시에는 이미 위에서 정리됨)
        interview_completed = 'created_audio_files' in locals() and len(created_audio_files) > 0

        if interview_completed:
            asyncio.create_task(cleanup_audio_files_after_delay(interview_id, delay_minutes=5))
            print(f"Interview {interview_id} completed. Scheduled audio cleanup in 5 minutes")
        else:
            print(f"Interview {interview_id} did not complete normally. Files already cleaned up if any.")

        db.close()
        try:
            await websocket.close()
        except:
            pass  # WebSocket might be closed already


@router.post("/{interview_id}/video-analysis", status_code=200)
def handle_video_analysis(
    interview_id: int,
    request_data: VideoAnalysisRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Receive video landmark data, analyze it, and save the results to the
    video_analysis table.
    """
    print(f"Received video-analysis request for interview {interview_id}")
    print(f"- Number of landmark frames: {len(request_data.landmarks) if request_data.landmarks else 0}")

    interview = crud.interview.get_interview(db, interview_id=interview_id)
    if not interview or interview.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Interview not found or access denied")

    landmark_data = request_data.landmarks
    video_metrics = analyze_video_landmarks(landmark_data)
    print(f"- Calculated metrics: gaze={video_metrics.get('gaze_stability')}, expression={video_metrics.get('expression_stability')}, posture={video_metrics.get('posture_stability')}")

    # Check if video analysis for this interview already exists
    existing_video_analysis = crud.video_analysis.get_by_interview_id(db, interview_id=interview_id)
    if existing_video_analysis:
        # Optionally, you could update it, but for now, we'll just return a message.
        return {"message": "Video analysis data for this interview already exists."}

    video_analysis_create = VideoAnalysisCreate(
        interview_id=interview_id,
        **video_metrics
    )
    crud.video_analysis.create(db=db, obj_in=video_analysis_create)

    return {"message": "Video analysis data saved successfully."}
