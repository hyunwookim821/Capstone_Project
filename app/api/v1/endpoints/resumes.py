from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Any
from datetime import datetime
import io
import os
import docx
from PyPDF2 import PdfReader
from hanspell import spell_checker
import anthropic
import google.generativeai as genai
from dotenv import load_dotenv

from app.schemas.resume import Resume, ResumeCreate, ResumeUpdate
from app.schemas.analysis import GrammarAnalysis
from app.schemas.feedback import AIFeedback
from app.schemas.interview import QuestionList

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
def read_resume(resume_id: int) -> Any:
    if resume_id not in DUMMY_RESUMES:
        raise HTTPException(status_code=404, detail="Resume not found")
    return DUMMY_RESUMES[resume_id]

@router.put("/{resume_id}", response_model=Resume)
def update_resume(resume_id: int, resume_in: ResumeUpdate) -> Any:
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
def delete_resume(resume_id: int) -> Any:
    if resume_id not in DUMMY_RESUMES:
        raise HTTPException(status_code=404, detail="Resume not found")
    return DUMMY_RESUMES.pop(resume_id)

# --- Analysis Endpoints ---

@router.post("/{resume_id}/check-grammar", response_model=GrammarAnalysis)
def check_resume_grammar(resume_id: int) -> Any:
    """
    Check the grammar of a resume using hanspell.
    """
    if resume_id not in DUMMY_RESUMES:
        raise HTTPException(status_code=404, detail="Resume not found")

    content = DUMMY_RESUMES[resume_id].get("content", "")
    
    # Split the content by newlines to handle texts longer than 500 characters.
    lines = content.split('\n')
    total_errors = 0
    corrected_lines = []

    for line in lines:
        if not line.strip():
            corrected_lines.append(line)
            continue
        
        result = spell_checker.check(line)
        total_errors += result.errors
        corrected_lines.append(result.checked)

    corrected_sentence = '\n'.join(corrected_lines)

    return GrammarAnalysis(
        error_count=total_errors,
        corrected_sentence=corrected_sentence
    )

@router.post("/{resume_id}/feedback", response_model=AIFeedback)
def get_ai_feedback(resume_id: int) -> Any:
    """
    Get AI feedback on a resume using Claude API.
    """
    if resume_id not in DUMMY_RESUMES:
        raise HTTPException(status_code=404, detail="Resume not found")

    content = DUMMY_RESUMES[resume_id].get("content", "")
    
    # First, check the grammar of the content, handling long texts by splitting them.
    lines = content.split('\n')
    total_errors = 0
    corrected_lines = []

    for line in lines:
        if not line.strip():
            corrected_lines.append(line)
            continue
        
        result = spell_checker.check(line)
        total_errors += result.errors
        corrected_lines.append(result.checked)

    corrected_content = '\n'.join(corrected_lines)

    if not corrected_content:
        raise HTTPException(status_code=400, detail="Resume content is empty after spell check.")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not set.")

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
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
        return AIFeedback(
            error_count=total_errors,
            corrected_sentence=corrected_content,
            feedback=feedback_text
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Claude API: {e}")

@router.post("/{resume_id}/generate-questions", response_model=QuestionList)
def generate_interview_questions(resume_id: int) -> Any:
    """
    Generate interview questions based on the resume using Gemini API.
    """
    if resume_id not in DUMMY_RESUMES:
        raise HTTPException(status_code=404, detail="Resume not found")

    content = DUMMY_RESUMES[resume_id].get("content", "")
    if not content:
        raise HTTPException(status_code=400, detail="Resume content is empty.")

    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not set.")

    try:
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
        
        # The response text might contain the title "예상 면접 질문 리스트". 
        # We split the text by newlines and filter out empty lines and the title.
        questions = [q.strip() for q in response.text.split('\n') if q.strip() and "예상 면접 질문 리스트" not in q]
        
        return QuestionList(questions=questions)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Gemini API: {e}")