from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Any
from datetime import datetime
import io
import docx
from PyPDF2 import PdfReader
from kospellpy import spellchecker

from app.schemas.resume import Resume, ResumeCreate, ResumeUpdate
from app.schemas.analysis import GrammarAnalysis, GrammarError

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

def _parse_docx(file: UploadFile) -> str:
    """Helper function to parse .docx files."""
    try:
        document = docx.Document(io.BytesIO(file.file.read()))
        return "\n".join([para.text for para in document.paragraphs])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing DOCX file: {e}")

def _parse_pdf(file: UploadFile) -> str:
    """Helper function to parse .pdf files."""
    try:
        reader = PdfReader(io.BytesIO(file.file.read()))
        return "\n".join([page.extract_text() for page in reader.pages])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing PDF file: {e}")

@router.get("/", response_model=List[Resume])
def read_resumes(skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve resumes.
    """
    return list(DUMMY_RESUMES.values())[skip:limit]

@router.post("/", response_model=Resume)
async def create_resume(
    title: str = Form(...),
    file: UploadFile = File(...),
) -> Any:
    """
    Create new resume from an uploaded file.
    """
    content = ""
    if file.content_type == "application/pdf":
        content = _parse_pdf(file)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        content = _parse_docx(file)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PDF or DOCX file.")

    if not content:
        raise HTTPException(status_code=400, detail="Could not extract text from the file.")

    new_id = max(DUMMY_RESUMES.keys()) + 1
    resume = Resume(
        id=new_id,
        owner_id=1, # Assuming a default owner for now
        title=title,
        content=content,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    DUMMY_RESUMES[new_id] = resume.model_dump()
    return resume

@router.post("/{resume_id}/check-grammar", response_model=GrammarAnalysis)
def check_resume_grammar(
    resume_id: int,
) -> Any:
    """
    Check the grammar of a resume.
    """
    if resume_id not in DUMMY_RESUMES:
        raise HTTPException(status_code=404, detail="Resume not found")

    content = DUMMY_RESUMES[resume_id].get("content", "")
    if not content:
        return GrammarAnalysis(errors=[], error_count=0)

    # kospellpy returns a list of dicts
    # [{'orgStr': '않되요', 'candWord': '안 돼요', 'context': '...있으면 않되요. ...', 'help': '...'}, ...]
    spelling_errors = spellchecker.check(content)

    formatted_errors = [
        GrammarError(
            original=err["orgStr"],
            corrected=err["candWord"],
            context=err["context"],
            type=err["help"],
        )
        for err in spelling_errors
    ]

    return GrammarAnalysis(errors=formatted_errors, error_count=len(formatted_errors))


@router.get("/{resume_id}", response_model=Resume)
def read_resume(
    *,
    resume_id: int,
) -> Any:
    """
    Get resume by ID.
    """
    if resume_id not in DUMMY_RESUMES:
        raise HTTPException(status_code=404, detail="Resume not found")
    return DUMMY_RESUMES[resume_id]

@router.put("/{resume_id}", response_model=Resume)
def update_resume(
    *,
    resume_id: int,
    resume_in: ResumeUpdate,
) -> Any:
    """
    Update a resume.
    """
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
    """
    Delete a resume.
    """
    if resume_id not in DUMMY_RESUMES:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    deleted_resume = DUMMY_RESUMES.pop(resume_id)
    return deleted_resume
