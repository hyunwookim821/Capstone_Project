from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Any
from sqlalchemy.orm import Session
import os
import io
import docx
from PyPDF2 import PdfReader
from hanspell import spell_checker
import anthropic
import google.generativeai as genai
from dotenv import load_dotenv

from app import crud, models
from app.api import deps
from app.schemas.resume import Resume, ResumeCreate, ResumeUpdate, ResumeDetail
from app.schemas.generated_question import GeneratedQuestionCreate

load_dotenv()

router = APIRouter()

# --- Helper Functions (File Parsers) ---
def _parse_docx(file_content: bytes) -> str:
    try:
        document = docx.Document(io.BytesIO(file_content))
        return "\n".join([para.text for para in document.paragraphs])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing DOCX file: {e}")

def _parse_pdf(file_content: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(file_content))
        return "\n".join([page.extract_text() for page in reader.pages])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing PDF file: {e}")

# --- Resume CRUD Endpoints ---

@router.get("/", response_model=List[ResumeDetail])
def read_resumes(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """Retrieve resumes for the current user."""
    resumes = crud.crud_resume.get_multi_by_owner(db, owner_id=current_user.user_id, skip=skip, limit=limit)
    return resumes

@router.post("/", response_model=Resume)
async def create_resume(
    *,
    db: Session = Depends(deps.get_db),
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """Create new resume from an uploaded file for the current user."""
    file_content = await file.read()
    content = ""
    if file.content_type == "application/pdf":
        content = _parse_pdf(file_content)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        content = _parse_docx(file_content)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")
    
    if not content:
        raise HTTPException(status_code=400, detail="Could not extract text from file.")

    resume_in = ResumeCreate(title=title, content=content)
    resume = crud.crud_resume.create(db=db, obj_in=resume_in, user_id=current_user.user_id)
    return resume

@router.get("/{resume_id}", response_model=ResumeDetail)
def read_resume_detail(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """Get a resume with all its details including feedback and questions."""
    resume = crud.crud_resume.get(db=db, resume_id=resume_id)
    if not resume or resume.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")
    return resume

@router.put("/{resume_id}", response_model=Resume)
def update_resume(
    resume_id: int,
    *,
    db: Session = Depends(deps.get_db),
    resume_in: ResumeUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """Update a resume. User can only update their own resume."""
    resume = crud.crud_resume.get(db=db, resume_id=resume_id)
    if not resume or resume.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")
    resume = crud.crud_resume.update(db=db, db_obj=resume, obj_in=resume_in)
    return resume

@router.delete("/{resume_id}", response_model=Resume)
def delete_resume(
    resume_id: int,
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """Delete a resume. User can only delete their own resume."""
    resume = crud.crud_resume.get(db=db, resume_id=resume_id)
    if not resume or resume.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")
    resume = crud.crud_resume.remove(db=db, resume_id=resume_id)
    return resume

# --- Analysis Endpoints ---

@router.post("/{resume_id}/check-grammar", response_model=ResumeDetail)
def check_resume_grammar(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Check resume grammar and save the corrected content.
    """
    resume = crud.crud_resume.get(db=db, resume_id=resume_id)
    if not resume or resume.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")

    if resume.corrected_content:
        return resume

    content = resume.content or ""
    lines = content.split('\n')
    corrected_lines = []
    for line in lines:
        if not line.strip():
            corrected_lines.append(line)
            continue
        try:
            result = spell_checker.check(line)
            corrected_lines.append(result.checked)
        except Exception:
            corrected_lines.append(line)
    corrected_content = '\n'.join(corrected_lines)

    update_data = {"corrected_content": corrected_content}
    updated_resume = crud.crud_resume.update(db=db, db_obj=resume, obj_in=update_data)
    return updated_resume

@router.post("/{resume_id}/feedback")
def get_ai_feedback(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get AI feedback on a resume. If feedback doesn't exist, generate and save it.
    """
    resume = crud.crud_resume.get(db=db, resume_id=resume_id)
    if not resume or resume.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")

    if resume.ai_feedback:
        return resume

    corrected_content = resume.corrected_content
    if not corrected_content:
        raise HTTPException(status_code=400, detail="Corrected content not found. Please run grammar check first.")

    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="CLAUDE_API_KEY not set.")
    claude_model = os.getenv("CLAUDE_MODEL")
    if not claude_model:
        raise HTTPException(status_code=500, detail="CLAUDE_MODEL environment variable not set.")

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=claude_model,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": f"""당신은 수많은 지원자를 평가해 온 베테랑 채용 담당자입니다. 당신의 임무는 지원자의 자기소개서를 분석하고, 합격 가능성을 높일 수 있도록 구체적이고 건설적인 피드백을 제공하는 것입니다. 반드시 아래의 규칙과 출력 형식을 엄격하게 준수하여 답변해야 합니다.

[규칙]

내용 기반 분석: 자기소개서에 명시적으로 언급된 내용(경험, 장점, 단점, 역량 등)에만 근거하여 분석합니다. 절대 내용을 추측하거나 없는 사실을 가정하지 마세요.

건설적인 톤: 지원자의 자신감을 떨어뜨리지 않도록, 긍정적이고 격려하는 어조를 유지하세요. 비판이 아닌 개선을 위한 제안 형태로 피드백을 제공하세요.

간결성: 각 항목은 핵심만 명확하고 간결하게 작성하여 토큰 사용을 최소화하세요.

형식 준수: 아래에 제시된 **[출력 형식]**의 구조와 순서, 아이콘(👍, ✍️, 💡)을 반드시 지켜야 합니다.

[출력 형식]

총평

자기소개서 전체에 대한 핵심적인 인상과 가장 중요한 개선 포인트를 한두 문장으로 요약합니다.

👍 잘한 점

(자기소개서의 강점 1: STAR 기법 활용, 직무 역량 강조, 구체적인 성과 제시 등 자기소개서 내용에 기반한 칭찬)

(자기소개서의 강점 2)

(자기소개서의 강점 3)

✍️ 개선할 점

(자기소개서의 약점 1: 수치적 근거 부족, 추상적인 표현, 경험과 역량의 연결성 부족 등 구체적인 개선 제안)

(자기소개서의 약점 2)

(자기소개서의 약점 3)

💡 최종 제안

피드백을 종합하여, 지원자가 가장 먼저 수정해야 할 한 가지 액션 아이템을 제시합니다.

이제 이 지침에 따라 아래 자기소개서를 분석하고 피드백을 생성해 주세요.

[지원자 자기소개서]
{corrected_content}
"""
                }
            ]
        )
        feedback_text = message.content[0].text

        # --- DEBUG: Claude API 응답을 파일에 저장 ---
        with open("claude_response.txt", "w", encoding="utf-8") as f:
            f.write(feedback_text)
        # -----------------------------------------

        # 1. DB에 결과를 저장합니다.
        update_data = {"ai_feedback": feedback_text}
        crud.crud_resume.update(db=db, db_obj=resume, obj_in=update_data)

        # 2. 수동으로 JSON 응답을 구성하여 반환합니다.
        response_data = {
            "resume_id": resume.resume_id,
            "title": resume.title,
            "content": resume.content,
            "corrected_content": resume.corrected_content,
            "ai_feedback": feedback_text,  # Claude에서 받은 텍스트를 직접 사용
            "generated_questions": [
                {"question_id": q.question_id, "resume_id": q.resume_id, "question_text": q.question_text}
                for q in resume.generated_questions
            ]
        }
        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Claude API: {e}")


@router.post("/{resume_id}/generate-questions", response_model=ResumeDetail)
def generate_interview_questions(
    resume_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Generate and save interview questions if they don't exist.
    """
    resume = crud.crud_resume.get(db=db, resume_id=resume_id)
    if not resume or resume.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")

    if resume.generated_questions:
        return resume

    content = resume.content or ""
    if not content:
        raise HTTPException(status_code=400, detail="Resume content is empty.")

    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not set.")
    gemini_model = os.getenv("GEMINI_MODEL")
    if not gemini_model:
        raise HTTPException(status_code=500, detail="GEMINI_MODEL environment variable not set.")

    try:
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel(gemini_model)

        prompt = f"""당신은 지원자의 역량을 깊이 있게 파악하려는 날카로운 면접관입니다. 당신의 임무는 지원자의 자기소개서와 일반적인 면접 질문을 조합하여, 핵심 역량과 경험의 진위, 그리고 문제 해결 능력을 종합적으로 검증할 수 있는 면접 질문 목록을 생성하는 것입니다. 반드시 아래 규칙과 출력 형식을 엄격하게 준수하여 답변해야 합니다.

[규칙]

질문 유형 조합: 질문 목록은 아래 두 가지 유형을 반드시 조합하여 생성해야 합니다.

- 자기소개서 기반 질문: 지원자의 자기소개서에 명시된 경험, 역량, 성과, 장단점 등을 깊이 있게 파고드는 질문입니다.
- 공통 질문: 모든 지원자에게 물어볼 수 있는 직무/회사 관련 질문이나 인성/가치관 질문입니다. (예: 입사 후 포부, 지원 동기, 마지막으로 하고 싶은 말 등)

질문 개수: 자기소개서 내용의 분량과 깊이를 고려하여, 두 유형을 합쳐 최소 5개에서 최대 15개의 질문을 유동적으로 생성합니다.

압박 질문 포함: 전체 질문 중 1~2개는 지원자의 논리력, 위기 대처 능력 등을 확인하기 위한 압박 질문(꼬리 질문, 반대 상황 가정 등)을 포함해야 합니다. 압박 질문은 🌶️ 아이콘으로 명확히 표시하세요.

형식 준수: 아래에 제시된 **[출력 형식]**의 구조와 순서를 반드시 지켜야 합니다. 공통 질문 앞에는 [공통] 말머리를 붙여주세요. 실제 면접에서 바로 사용할 수 있도록 구어체로 작성하세요.

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

        for q_text in questions:
            q_in = GeneratedQuestionCreate(resume_id=resume_id, question_text=q_text)
            crud.crud_generated_question.create_question(db=db, obj_in=q_in)
        
        db.refresh(resume)
        return resume

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Gemini API: {e}")
