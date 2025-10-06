from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Any
from datetime import datetime
import io
import os
import docx
from PyPDF2 import PdfReader
from app.utils.spell_check import check_spelling
import anthropic
from dotenv import load_dotenv

from app.schemas.resume import Resume, ResumeCreate, ResumeUpdate
from app.schemas.analysis import GrammarCheckResult
from app.schemas.feedback import AIFeedback

load_dotenv()

router = APIRouter()

# Dummy database
DUMMY_RESUMES = {
    1: {
        "id": 1,
        "owner_id": 1,
        "title": "My First Resume",
        "content": "아버지가방에 들어가신다. 이력서에 오타가 있으면 않되요.",
        "created_at": datetime(2023, 1, 1),
        "updated_at": datetime(2023, 1, 1),
    },
    2: {
        "id": 2,
        "owner_id": 1,
        "title": "My Second Resume",
        "content": "This is the content of my second resume, focused on AI.",
        "created_at": datetime(2023, 1, 2),
        "updated_at": datetime(2023, 1, 2),
    },
}

# --- Helper Functions ---

def _parse_docx(file: UploadFile) -> str:
    try:
        document = docx.Document(io.BytesIO(file.file.read()))
        return "\n".join([para.text for para in document.paragraphs])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing DOCX file: {e}")

def _parse_pdf(file: UploadFile) -> str:
    try:
        reader = PdfReader(io.BytesIO(file.file.read()))
        return "\n".join([page.extract_text() for page in reader.pages])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing PDF file: {e}")

# --- Resume CRUD Endpoints ---

@router.get("/", response_model=List[Resume])
def read_resumes(skip: int = 0, limit: int = 100) -> Any:
    return list(DUMMY_RESUMES.values())[skip:limit]

@router.post("/", response_model=Resume)
async def create_resume(title: str = Form(...), file: UploadFile = File(...)) -> Any:
    content = ""
    if file.content_type == "application/pdf":
        content = _parse_pdf(file)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        content = _parse_docx(file)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    if not content:
        raise HTTPException(status_code=400, detail="Could not extract text.")

    new_id = max(DUMMY_RESUMES.keys()) + 1
    resume = Resume(
        id=new_id, owner_id=1, title=title, content=content,
        created_at=datetime.now(), updated_at=datetime.now()
    )
    DUMMY_RESUMES[new_id] = resume.model_dump()
    return resume

@router.get("/{resume_id}", response_model=Resume)
def read_resume(
    resume_id: int,
) -> Any:
    if resume_id not in DUMMY_RESUMES:
        raise HTTPException(status_code=404, detail="Resume not found")
    return DUMMY_RESUMES[resume_id]

@router.put("/{resume_id}", response_model=Resume)
def update_resume(
    *, 
    resume_id: int,
    resume_in: ResumeUpdate,
) -> Any:
    if resume_id not in DUMMY_RESUMES:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    resume_data = DUMMY_RESUMES[resume_id]
    resume = Resume(**resume_data)
    update_data = resume_in.model_dump(exclude_unset=True)
    
    updated_resume = resume.model_copy(update=update_data)
    updated_resume.updated_at = datetime.now()
    
    DUMMY_RESUMES[resume_id] = updated_resume.model_dump()
    return updated_resume

@router.delete("/{resume_id}", response_model=Resume)
def delete_resume(
    *, 
    resume_id: int,
) -> Any:
    if resume_id not in DUMMY_RESUMES:
        raise HTTPException(status_code=404, detail="Resume not found")
    return DUMMY_RESUMES.pop(resume_id)

# --- Analysis Endpoints ---

@router.post("/{resume_id}/check-grammar", response_model=GrammarCheckResult)
def check_resume_grammar(resume_id: int) -> Any:
    """
    Check the grammar of a resume using kospellpy.
    """
    if resume_id not in DUMMY_RESUMES:
        raise HTTPException(status_code=404, detail="Resume not found")

    content = DUMMY_RESUMES[resume_id].get("content", "")
    if not content:
        return GrammarCheckResult(original=content, corrected=content)

    corrected_content = check_spelling(content)
    return GrammarCheckResult(original=content, corrected=corrected_content)

@router.post("/{resume_id}/feedback", response_model=AIFeedback)
def get_ai_feedback(resume_id: int) -> Any:
    """
    Get AI feedback on a resume using Claude API.
    """
    if resume_id not in DUMMY_RESUMES:
        raise HTTPException(status_code=404, detail="Resume not found")

    content = DUMMY_RESUMES[resume_id].get("content", "")
    if not content:
        raise HTTPException(status_code=400, detail="Resume content is empty.")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not set.")

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": f"You are a professional career coach. Please review the following resume content and provide constructive feedback. Focus on clarity, impact, and suggest specific improvements to make it more compelling to recruiters.\n\n---\n\n{content}"
                }
            ]
        )
        feedback_text = message.content[0].text
        return AIFeedback(feedback=feedback_text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Claude API: {e}")