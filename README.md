# AI기반 면접 시뮬레이션 플랫폼

AI를 활용하여 실제와 같은 모의 면접을 연습하고, 음성 및 영상 분석을 통해 종합적인 피드백을 제공받을 수 있는 AI기반 취업 준비 플랫폼입니다.

## 1. 프로젝트 개요

본 프로젝트는 사용자가 자신의 이력서를 기반으로 맞춤형 면접 질문을 받고, AI 면접관과 실시간으로 대화하며 면접을 연습할 수 있는 환경을 제공합니다. 면접 종료 후에는 답변 내용, 말하기 습관(음성), 시각적 태도(영상)를 종합적으로 분석한 심층 리포트를 받아볼 수 있습니다.

## 👥 Team

| 이름 | 역할 |
|------|------|
| 김현우 | Backend |
| 오현우 | Backend |
| 홍성혁 | Frontend |


## 🛠️ Tech Stack

### Backend
![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)

### Frontend
![Java](https://img.shields.io/badge/Java-007396?style=for-the-badge&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-6DB33F?style=for-the-badge&logo=springboot&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Mustache](https://img.shields.io/badge/Mustache-000000?style=for-the-badge&logo=mustache&logoColor=white)

### AI & ML
![Google Gemini](https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)
![Anthropic Claude](https://img.shields.io/badge/Claude-181818?style=for-the-badge&logo=anthropic&logoColor=D4976D)
![OpenAI](https://img.shields.io/badge/Whisper-412991?style=for-the-badge&logo=openai&logoColor=white)
![Google Cloud](https://img.shields.io/badge/TTS-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)

### Video/Audio Processing
![MediaPipe](https://img.shields.io/badge/MediaPipe-0097A7?style=for-the-badge&logo=mediapipe&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)

### DevOps & Tools
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![WebSocket](https://img.shields.io/badge/WebSocket-010101?style=for-the-badge&logo=socketdotio&logoColor=white)

---

## 2. 시스템 아키텍처

이 프로젝트는 두 개의 독립적인 서버로 구성된 **BFF(Backend for Frontend)** 패턴을 따릅니다.

-   **핵심 백엔드 (Core Backend) - `jobprep-api`**
    -   **프레임워크:** FastAPI (Python)
    -   **역할:**
        -   모든 비즈니스 로직 처리 (사용자 인증, 이력서/면접 관리 등)
        -   데이터베이스(PostgreSQL)와의 모든 상호작용 담당
        -   외부 AI 서비스 연동
            -   **Google Gemini**: 맞춤형 면접 질문 생성
            -   **Anthropic Claude**: 종합 면접 분석 리포트 생성
            -   **Google Gemini TTS**: 자연스러운 면접관 음성 합성
            -   **OpenAI Whisper**: 면접 답변 음성-텍스트 변환 및 분석
        -   음성 분석: 말하기 속도(어절/분), 침묵 비율 계산
        -   영상 분석: MediaPipe 기반 시선/표정/자세 안정성 측정

-   **프론트엔드 BFF 서버 (Frontend BFF) - `Front`**
    -   **프레임워크:** Spring Boot (Java)
    -   **역할:**
        -   사용자에게 보여지는 UI(HTML, CSS, JS) 렌더링 및 제공
        -   사용자 요청을 받아 핵심 백엔드(FastAPI)로 전달하는 API 게이트웨이 역할
        -   백엔드로부터 받은 데이터를 가공하여 UI에 맞게 표시

## 3. 사전 요구사항

-   Git
-   Python (3.11 이상 권장)
-   Java (17 이상 권장)
-   PostgreSQL (13 이상 권장)
-   FFmpeg (오디오/비디오 처리 및 변환에 필요)
    -    ffmpeg.exe, ffplay.exe, ffprobe.exe 프로젝트 루트 디렉토리에 위치
 
## ERD
<img width="1870" height="862" alt="AI JOP ERD" src="https://github.com/user-attachments/assets/1d00a19a-c02c-4ea8-884a-972bd87b1030" />


## 4. 로컬 환경 설정 및 실행 가이드

### 4.1. 소스 코드 클론

```bash
git clone <저장소_URL>
cd <프로젝트_디렉토리>
```

### 4.2. 데이터베이스 설정 (PostgreSQL with Docker)

이 프로젝트는 Docker Compose를 사용하여 PostgreSQL 데이터베이스를 실행합니다. 로컬에 PostgreSQL을 직접 설치할 필요 없이, Docker만 설치되어 있으면 됩니다.

1.  **Docker 및 Docker Compose 설치:**
    -   [Docker Desktop](https://www.docker.com/products/docker-desktop/)을 설치합니다. (Docker Compose가 포함되어 있습니다.)

2.  **Docker 컨테이너 실행:**
    프로젝트 루트 디렉토리에서 다음 명령어를 실행하여 PostgreSQL 데이터베이스 서버를 시작합니다.

    ```bash
    docker-compose up -d
    ```
    `-d` 옵션은 컨테이너를 백그라운드에서 실행합니다.

3.  **데이터베이스 연결 확인:**
    `docker-compose.yml` 파일에 정의된 설정(`jobprep_db` 데이터베이스, `jobprep` 사용자)으로 데이터베이스가 자동으로 생성 및 실행됩니다. `.env` 파일의 `DATABASE_URL`이 이 설정과 일치하는지 확인하세요.


### 4.3. 백엔드 설정 (FastAPI)

1.  **가상환경 생성 및 활성화:**
    프로젝트 루트 디렉토리에서 다음 명령어를 실행합니다.

    ```bash
    # 가상환경 생성
    python -m venv .venv

    # Windows
    .\.venv\Scripts\activate

    # macOS / Linux
    source .venv/bin/activate
    ```

2.  **환경 변수 설정:**
    프로젝트 루트 디렉토리에 `.env` 파일을 생성하고, 아래 내용을 자신의 환경에 맞게 수정하여 붙여넣습니다.

    ```env
    # .env

    SECRET_KEY=my_super_secret_key_for_jwt_development

    # === API KEYS ===
    GOOGLE_API_KEY=your_google_api_key_here
    CLAUDE_API_KEY=your_claude_api_key_here

    # === AI MODELS ===
    GEMINI_MODEL=gemini-2.5-flash    // 질문 생성용 (변경 가능)
    CLAUDE_MODEL=claude-haiku-4-5-20251001   // 면접 분석용 (변경 가능)

    # === DATABASE ===
    POSTGRES_SERVER=localhost
    POSTGRES_PORT=5432
    POSTGRES_USER=jobprep
    POSTGRES_PASSWORD=jobprep_password
    POSTGRES_DB=jobprep_db

    DATABASE_URL=postgresql://jobprep:jobprep_password@localhost:5432/jobprep_db

    # === TTS (Gemini TTS - 자연스러운 음성 생성) ===
    EMBEDDING_MODEL=jhgan/ko-sroberta-multitask
    TTS_MODEL_NAME=gemini-2.5-flash-tts     // gemini-2.5-pro-tts로 변경 가능 (고품질)
    TTS_VOICE_NAME=Charon    // Gemini TTS 음성 (Kore, Aoede, Puck 등으로 변경 가능)
    TTS_STYLE_PROMPT=당신은 경험이 풍부한 전문 면접관입니다. 친절하면서도 전문적인 톤으로, 명확하고 또렷하게 질문을 전달합니다. 아주 살짝 빠른 속도로 말하며, 지원자가 편안하게 답변할 수 있도록 격려적인 분위기를 조성합니다.
    GOOGLE_APPLICATION_CREDENTIALS=./your-service-account-key.json

    # === JWT 토큰 설정 ===
    ACCESS_TOKEN_EXPIRE_MINUTES=120    // 면접 시간을 고려하여 2시간으로 설정
    ```

3.  **의존성 설치:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **데이터베이스 마이그레이션:**
    Alembic을 사용하여 데이터베이스에 테이블을 생성합니다.

    ```bash
    alembic upgrade head
    ```

### 4.4. 프론트엔드(BFF) 설정 (Spring Boot)

`Front` 디렉토리의 `build.gradle` 파일이 모든 의존성을 관리하므로, 별도의 설정은 필요하지 않습니다.

## 5. 서버 실행

두 개의 터미널을 열고 각각 백엔드와 프론트엔드 서버를 실행합니다.

### 5.1. 백엔드 서버 실행

-   **터미널 1** (프로젝트 루트 디렉토리)
-   가상환경이 활성화된 상태여야 합니다.

```bash
uvicorn app.main:app --reload
python -m uvicorn app.main:app --reload --ws-max-size 10485760
```

-   서버가 `http://127.0.0.1:8000`에서 실행됩니다.
-   FastAPI 앱을 개발 모드(자동 재시작)로 실행하며, WebSocket 메시지 크기를 10MB까지 허용(두번째 커맨드)

### 5.2. 프론트엔드(BFF) 서버 실행

-   **터미널 2**

```bash
cd Front
./gradlew bootRun
```

서버가 `http://localhost:8080`에서 실행됩니다.

### 5.3. 애플리케이션 접속

웹 브라우저를 열고 `http://localhost:8080` 주소로 접속하여 애플리케이션을 사용합니다.

## 6. 주요 기능 및 API 엔드포인트 (BFF 기준)

-   `GET /`: 메인 페이지
-   `GET /auth/login`: 로그인 페이지
-   `GET /auth/signup`: 회원가입 페이지
-   `POST /api/auth/login`: 로그인 처리
-   `POST /api/auth/signup`: 회원가입 처리
-   `POST /api/resumes`: 이력서 업로드
-   `POST /api/interviews`: 면접 세션 생성
-   `POST /api/interviews/{id}/video-analysis`: 영상 분석 데이터 전송
-   `GET /api/interviews/{id}/results`: 최종 종합 분석 결과 요청

## 🖥️ 실행 화면

<details>
<summary>▶️ 시작 화면</summary>

<img width="1462" height="1269" alt="KakaoTalk_20251025_172135237" src="https://github.com/user-attachments/assets/79e394d9-b1e2-453d-8e6d-e0946293ad66" />

</details>

<details>
<summary>▶️ 로그인 / 회원가입 화면</summary>

<img width="656" height="850" alt="KakaoTalk_20251025_172151494" src="https://github.com/user-attachments/assets/cc51d874-5ebe-4931-bf9c-7a456f6ab448" />
<img width="625" height="1179" alt="KakaoTalk_20251025_172144826" src="https://github.com/user-attachments/assets/12b87c11-8f65-4752-9f19-801f6658e00f" />


</details>

<details>
<summary>▶️ 자소서 피드백 화면</summary>

<img width="2532" height="1170" alt="KakaoTalk_20251203_200220889" src="https://github.com/user-attachments/assets/2b32ba8a-e94f-4a22-94e0-552e11f8358a" />


</details>

<details>
<summary>▶️ 면접 진행 화면</summary>

<img width="2532" height="1170" alt="KakaoTalk_20251203_200220889_03" src="https://github.com/user-attachments/assets/f71d3787-72a4-4ad0-8a15-b2eed4bdecb8" />


</details>

<details>
<summary>▶️ 면접 피드백 화면</summary>

<img width="2532" height="1170" alt="KakaoTalk_20251203_200220889_04" src="https://github.com/user-attachments/assets/6b528039-d4f9-44e5-92ae-74921566a69f" />


</details>
