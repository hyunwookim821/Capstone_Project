from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, UploadFile, File
from typing import List, Any, Dict
import os
import base64
import uuid
import re
import google.generativeai as genai
import google.cloud.texttospeech as tts
import whisper
import anthropic
import httpx
from pydub import AudioSegment
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app import crud, models
from app.api import deps
from app.schemas.interview import InterviewCreate, QuestionCreate, AnswerCreate, InterviewSession, VideoAnalysisRequest
from app.schemas.analysis import Analysis, AnalysisCreate
from app.schemas.video_analysis import VideoAnalysisCreate
from app.utils.audio_analysis import analyze_speech_audio
from app.utils.video_analysis import analyze_video_landmarks

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
    """
    resume = crud.resume.get(db, resume_id=resume_id)
    if not resume or resume.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")

    existing_questions = crud.interview.get_latest_questions_by_resume(db, resume_id=resume_id)
    
    if existing_questions:
        questions_text = [q.question_text for q in existing_questions]
    else:
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
                if not q or "예상 면접 질문 리스트" in q or q == "$$공통$$":
                    continue
                q = re.sub(r'^\d+\.\s*', '', q)
                q = q.replace('🌶️', '').strip()
                if q:
                    questions_text.append(q)

            if not questions_text:
                raise HTTPException(status_code=500, detail="Failed to generate questions.")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI question generation failed: {str(e)}")

    cleaned_questions_text = []
    for q in questions_text:
        q = q.strip()
        if not q or "예상 면접 질문 리스트" in q or q == "$$공통$$":
            continue
        q = re.sub(r'^\d+\.\s*', '', q)
        q = q.replace('🌶️', '').strip()
        if q:
            cleaned_questions_text.append(q)
    questions_text = cleaned_questions_text

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
        if q.answers and q.answers[0].audio_path and os.path.exists(q.answers[0].audio_path):
            answer = q.answers[0]
            speech_rate, silence_ratio = analyze_speech_audio(answer.audio_path, answer.answer_text)
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
    api_key = os.getenv("CLAUDE_API_KEY")
    claude_model = os.getenv("CLAUDE_MODEL")
    if not api_key or not claude_model:
        raise HTTPException(status_code=500, detail="Claude API configuration missing.")
    api_key = api_key.strip().strip('"').strip("'")

    prompt = f"""당신은 수많은 면접 경험을 가진 전문 채용 컨설턴트입니다. 당신의 임무는 아래 제공되는 지원자의 "자기소개서", "면접 대화록", "음성 분석 데이터", "영상 분석 데이터"를 종합적으로 분석하여, 지원자의 역량과 개선점에 대한 심층적인 피드백 리포트를 작성하는 것입니다.

반드시 아래의 "분석 기준"과 "출력 형식"을 엄격하게 준수하여 리포트를 작성해 주세요. (영상 분석 데이터가 없다면 해당 부분은 생략하고 리포트를 작성하세요.)

---
### **자기소개서**
```
{resume_content}
```
---
### **면접 대화록**
```
{conversation_history}
```
{audio_analysis_summary}
{video_analysis_summary}
---
### **분석 기준**

1.  **답변의 명확성 및 논리성 (Clarity & Logic):**
    *   질문의 의도를 정확히 파악하고 있는가?
    *   답변이 체계적이고 이해하기 쉬운가? (예: STAR 기법 활용)
    *   주장에 대한 근거가 명확하고 타당한가?

2.  **핵심 역량 및 경험 어필 (Keyword & Experience):**
    *   자기소개서에 언급된 자신의 경험과 강점을 답변에 잘 녹여내고 있는가?
    *   질문과 관련된 자신의 핵심 역량 키워드를 적절히 사용하고 있는가?

3.  **커뮤니케이션 스킬 (음성 및 영상 포함):**
    *   자신감 있는 어조와 긍정적인 태도를 보이는가? (대화 내용, 음성, 영상 데이터를 종합하여 추론)
    *   불필요한 단어나 반복적인 표현을 최소화하고 있는가?
    *   말하기 속도, 머뭇거림, 시선 처리, 표정, 자세 등은 적절한가? (음성 및 영상 분석 데이터 참고)

---
### **출력 형식 (Markdown)**

아래 형식을 반드시 준수하여, 각 항목에 대해 1-5점 척도로 점수를 매기고 구체적인 피드백을 작성해 주세요.

# **AI 면접 분석 리포트**

## **종합 평가**
> 총평을 2-3문장으로 요약하여 제공합니다. 지원자의 가장 큰 강점과 가장 시급한 개선점을 언급해 주세요.

---

## **세부 분석**

### **1. 답변의 명확성 및 논리성**
*   **점수:** [1-5점]
*   **👍 잘한 점:**
    *   (구체적인 답변 내용을 인용하며 칭찬)
*   **👎 개선할 점:**
    *   (구체적인 답변 내용을 인용하며 개선 방향 제시)

### **2. 핵심 역량 및 경험 어필**
*   **점수:** [1-5점]
*   **👍 잘한 점:**
    *   (자기소개서 내용과 답변을 비교하며 칭찬)
*   **👎 개선할 점:**
    *   (답변에서 아쉬웠던 부분과 자기소개서의 어떤 경험을 더 어필할 수 있었는지 제안)

### **3. 커뮤니케이션 스킬 (음성 및 영상 포함)**
*   **점수:** [1-5점]
*   **👍 잘한 점:**
    *   (자신감 있는 표현, 안정적인 시선 처리, 긍정적인 표정 등 칭찬)
*   **👎 개선할 점:**
    *   (음성/영상 분석 결과를 바탕으로 말하기 습관, 시선, 자세 등에 대한 조언)

---

## **총점 및 제안**
*   **총점:** [세 항목의 평균 점수를 소수점 첫째 자리까지 계산하여 표시] / 5.0
*   **마지막 조언:**
    > 지원자가 다음 면접에서 최고의 성과를 낼 수 있도록, 가장 중요한 핵심 조언 한 가지를 격려의 메시지와 함께 전달해 주세요.
"""

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
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=180.0
            )
            response.raise_for_status()
            
            response_data = response.json()
            feedback_text = response_data['content'][0]['text']

        analysis_create = AnalysisCreate(
            interview_id=interview_id, 
            feedback_text=feedback_text,
            speech_rate=avg_speech_rate,
            silence_ratio=avg_silence_ratio,
            gaze_stability=gaze_stability,
            expression_stability=expression_stability,
            posture_stability=posture_stability
        )
        new_analysis = crud.analysis.create_analysis(db=db, obj_in=analysis_create)
        return new_analysis

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
    await websocket.accept()
    db: Session = SessionLocal()
    try:
        try:
            user = deps.get_user_from_token(db=db, token=token)
        except HTTPException as e:
            await websocket.send_json({"type": "error", "message": f"Authentication failed: {e.detail}"})
            await websocket.close(code=1008)
            return

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

            audio_dir = "audio_files"
            os.makedirs(audio_dir, exist_ok=True)
            
            audio_filename = f"{uuid.uuid4()}.wav"
            audio_path = os.path.join(audio_dir, audio_filename)

            try:
                if 'whisper_model' not in globals():
                    globals()['whisper_model'] = whisper.load_model("small")
                
                with open(audio_path, "wb") as f:
                    f.write(audio_bytes)
                
                result = globals()['whisper_model'].transcribe(audio_path, language="ko")
                print(f"Whisper transcription result: {result}")
                answer_text = result.get("text", "")
            except Exception as e:
                print(f"Error during transcription: {e}")
                answer_text = ""
            
            answer_create = AnswerCreate(
                question_id=question.question_id, 
                answer_text=answer_text,
                audio_path=audio_path
            )
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
    interview = crud.interview.get_interview(db, interview_id=interview_id)
    if not interview or interview.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Interview not found or access denied")

    landmark_data = request_data.landmarks
    video_metrics = analyze_video_landmarks(landmark_data)

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
