from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Any
from sqlalchemy.orm import Session
import os
import io
import json
import re
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
from app.prompts import get_resume_feedback_prompt, get_question_generation_prompt

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
        # 개선된 프롬프트 모듈 사용
        prompt = get_resume_feedback_prompt(corrected_content)

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=claude_model,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": prompt
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

        # 개선된 프롬프트 모듈 사용
        prompt = get_question_generation_prompt(content)

        response = model.generate_content(prompt)

        # JSON 형식으로 파싱 시도
        try:
            # 응답에서 JSON 부분 추출 (```json ... ``` 형태일 수 있음)
            response_text = response.text.strip()
            if "```json" in response_text:
                # JSON 코드 블록에서 추출
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                # 일반 코드 블록에서 추출
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                # 코드 블록 없이 바로 JSON
                json_str = response_text

            parsed_response = json.loads(json_str)
            # 태그와 이모티콘 유지 (프론트엔드에서 질문 유형 구분용)
            questions = [q["text"] for q in parsed_response.get("questions", [])]
        except (json.JSONDecodeError, KeyError) as json_error:
            # JSON 파싱 실패 시 기존 방식으로 폴백
            print(f"JSON parsing failed, falling back to text split: {json_error}")
            questions = []
            raw_questions = response.text.split('\n')
            for q in raw_questions:
                q = q.strip()
                if not q or "예상 면접 질문 리스트" in q:
                    continue
                # 번호만 제거, 태그와 이모티콘은 유지
                q = re.sub(r'^\d+\.\s*', '', q).strip()
                if q:
                    questions.append(q)

        for q_text in questions:
            q_in = GeneratedQuestionCreate(resume_id=resume_id, question_text=q_text)
            crud.crud_generated_question.create_question(db=db, obj_in=q_in)

        db.refresh(resume)
        return resume

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Gemini API: {e}")
