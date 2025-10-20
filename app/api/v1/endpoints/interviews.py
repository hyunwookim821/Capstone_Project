from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Any
from datetime import datetime
import os
import io
import uuid
import base64
import google.generativeai as genai
from gtts import gTTS
import whisper
from pydub import AudioSegment

# Explicitly set the path to ffmpeg
AudioSegment.converter = os.path.abspath("ffmpeg.exe")
from dotenv import load_dotenv

from app.schemas.interview import Interview, InterviewCreate, InterviewUpdate, QuestionList
from app.api.v1.endpoints.resumes import DUMMY_RESUMES # For now, get resume content from resumes endpoint

load_dotenv()

router = APIRouter()

# Dummy database for REST API (can be removed later)
DUMMY_INTERVIEWS = {
    1: {
        "id": 1,
        "owner_id": 1,
        "resume_id": 1,
        "job_id": 1,
        "status": "completed",
        "created_at": datetime(2023, 1, 10),
        "updated_at": datetime(2023, 1, 11),
    },
}

# --- WebSocket Endpoint for Real-time Interview ---

@router.websocket("/ws/{resume_id}")
async def websocket_interview(websocket: WebSocket, resume_id: int):
    await websocket.accept()
    
    # --- 1. Generate questions --- 
    try:
        if resume_id not in DUMMY_RESUMES:
            await websocket.close(code=1008, reason="Resume not found")
            return

        content = DUMMY_RESUMES[resume_id].get("content", "")
        if not content:
            await websocket.close(code=1008, reason="Resume content is empty.")
            return

        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise Exception("GOOGLE_API_KEY not set.")

        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""당신은 지원자의 역량을 깊이 있게 파악하려는 날카로운 면접관입니다. 당신의 임무는 지원자의 자기소개서와 일반적인 면접 질문을 조합하여, 핵심 역량과 경험의 진위, 그리고 문제 해결 능력을 종합적으로 검증할 수 있는 면접 질문 목록을 생성하는 것입니다. 반드시 아래 규칙과 출력 형식을 엄격하게 준수하여 답변해야 합니다.

[규칙]

질문 유형 조합: 질문 목록은 아래 두 가지 유형을 반드시 조합하여 생성해야 합니다.

- 자기소개서 기반 질문: 지원자의 자기소개서에 명시된 경험, 역량, 성과, 장단점 등을 깊이 있게 파고드는 질문입니다.
- 공통 질문: 모든 지원자에게 물어볼 수 있는 직무/회사 관련 질문이나 인성/가치관 질문입니다. (예: 입사 후 포부, 지원 동기, 마지막으로 하고 싶은 말 등)

질문 개수: 자기소개서 내용의 분량과 깊이를 고려하여, 두 유형을 합쳐 최소 5개에서 최대 15개의 질문을 유동적으로 생성합니다.

압박 질문 포함: 전체 질문 중 1~2개는 지원자의 논리력, 위기 대처 능력 등을 확인하기 위한 압박 질문(꼬리 질문, 반대 상황 가정 등)을 포함해야 합니다. 압박 질문은 🌶️ 아이콘으로 명확히 표시하세요.

형식 준수: 아래에 제시된 **[출력 형식]**의 구조와 순서를 반드시 지켜야 합니다. 공통 질문 앞에는 [공통] 말머리를 붙여주세요.

[출력 형식]

예상 면접 질문 리스트

(자기소개서 내용에 기반한 일반 질문 1)

[공통] (모든 지원자에게 할 수 있는 직무/회사 관련 공통 질문)

🌶️ (자기소개서 내용에 기반한 압박 질문)

(이하 질문들을 규칙에 맞게 생성...)

[공통] (모든 지원자에게 할 수 있는 인성/가치관 관련 공통 질문)

이제 이 지침에 따라 아래 자기소개서를 분석하고 예상 면접 질문을 생성해 주세요.

[지원자 자기소개서]
{content}
"""
        
        response = model.generate_content(prompt)
        questions = [q.strip() for q in response.text.split('\n') if q.strip() and "예상 면접 질문 리스트" not in q]
        
        if not questions:
            raise Exception("Failed to generate questions.")

    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
        await websocket.close(code=1011)
        return

    # --- 2. Conduct the interview --- 
    await websocket.send_json({"type": "system", "message": f"Interview session started. {len(questions)} questions will be asked.", "status": "connected"})
    
    question_index = 0
    try:
        while question_index < len(questions):
            question = questions[question_index]
            # Send question text
            await websocket.send_json({"type": "question", "text": question, "question_number": question_index + 1, "total_questions": len(questions), "time_limit": 60})
            
            # Generate and send TTS audio
            try:
                mp3_fp = io.BytesIO()
                tts = gTTS(text=question, lang='ko')
                tts.write_to_fp(mp3_fp)
                mp3_fp.seek(0)
                await websocket.send_bytes(mp3_fp.read())
            except Exception as tts_error:
                print(f"TTS Error: {tts_error}")
                # If TTS fails, send a system message so the client can proceed
                await websocket.send_json({"type": "error", "message": "Could not generate audio for the question."})

            # Wait for the user's Base64 encoded audio answer
            base64_audio_data = await websocket.receive_text()
            
            # Decode Base64 to get raw audio bytes
            audio_bytes = base64.b64decode(base64_audio_data)

            # Transcribe audio to text using Whisper
            temp_file_path = None
            try:
                # Load model on first use
                if 'whisper_model' not in globals():
                    print("Loading Whisper model...")
                    globals()['whisper_model'] = whisper.load_model("small")
                
                # Create a unique temporary filename
                temp_file_path = f"temp_{uuid.uuid4()}.wav"
                
                # Write audio bytes to the temporary file
                with open(temp_file_path, "wb") as f:
                    f.write(audio_bytes)

                # Transcribe using the file path
                result = globals()['whisper_model'].transcribe(temp_file_path)
                answer_text = result["text"]
                print(f"Transcribed Answer: {answer_text}")

            except Exception as stt_error:
                print(f"STT Error: {stt_error}")
                await websocket.send_json({"type": "error", "message": "Could not process your audio answer."})
                answer_text = "" # Set empty answer if transcription fails
            finally:
                # Clean up the temporary file
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

            # (TODO: Save the answer_text)
            await websocket.send_json({"type": "system", "message": f"Answer for question {question_index + 1} received.", "status": "processing"})
            # (TODO: Save the answer)
            await websocket.send_json({"type": "system", "message": f"Answer for question {question_index + 1} received.", "status": "processing"})
            
            question_index += 1

        # --- 3. End the interview ---
        await websocket.send_json({"type": "system", "message": "Interview finished. Thank you.", "status": "finished"})
        await websocket.close()

    except WebSocketDisconnect:
        print(f"Client for resume {resume_id} disconnected during interview.")
    except Exception as e:
        print(f"An error occurred during interview: {e}")
        await websocket.close(code=1011, reason=str(e))


# --- REST API Endpoints (can be deprecated or used for history) ---

@router.get("/", response_model=List[Interview])
def read_interviews(skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve interviews.
    """
    return list(DUMMY_INTERVIEWS.values())[skip:limit]

@router.post("/", response_model=Interview)
def create_interview(
    *,
    interview_in: InterviewCreate,
) -> Any:
    """
    Create new interview session.
    """
    new_id = max(DUMMY_INTERVIEWS.keys()) + 1
    interview = Interview(
        id=new_id,
        owner_id=1,  # Assuming a default owner
        resume_id=interview_in.resume_id,
        job_id=interview_in.job_id,
        status='scheduled',
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    DUMMY_INTERVIEWS[new_id] = interview.dict()
    return interview

@router.get("/{interview_id}", response_model=Interview)
def read_interview(
    *,
    interview_id: int,
) -> Any:
    """
    Get interview by ID.
    """
    if interview_id not in DUMMY_INTERVIEWS:
        raise HTTPException(status_code=404, detail="Interview not found")
    return DUMMY_INTERVIEWS[interview_id]

@router.put("/{interview_id}", response_model=Interview)
def update_interview(
    *,
    interview_id: int,
    interview_in: InterviewUpdate,
) -> Any:
    """
    Update an interview.
    """
    if interview_id not in DUMMY_INTERVIEWS:
        raise HTTPException(status_code=404, detail="Interview not found")

    interview = DUMMY_INTERVIEWS[interview_id]
    update_data = interview_in.dict(exclude_unset=True)

    for field, value in update_data.items():
        interview[field] = value
    interview["updated_at"] = datetime.now()

    DUMMY_INTERVIEWS[interview_id] = interview
    return interview

@router.delete("/{interview_id}", response_model=Interview)
def delete_interview(
    *,
    interview_id: int,
) -> Any:
    """
    Delete an interview.
    """
    if interview_id not in DUMMY_INTERVIEWS:
        raise HTTPException(status_code=404, detail="Interview not found")

    deleted_interview = DUMMY_INTERVIEWS.pop(interview_id)
    return deleted_interview
