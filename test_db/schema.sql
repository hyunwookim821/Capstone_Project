CREATE DATABASE ai_joppass;

use ai_joppass;

-- 회원정보
CREATE TABLE user (
    user_id BIGINT NOT NULL PRIMARY KEY,
    user_name VARCHAR(20) NOT NULL,
    password VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL,
    profileimage VARCHAR(255) NULL,
    created_at DATETIME NOT NULL
);

-- 이력서
CREATE TABLE resume (
    resume_id BIGINT NOT NULL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    title VARCHAR(50) NOT NULL,
    create_at DATETIME NOT NULL,
    update_at DATETIME NOT NULL,
    content TEXT NULL,
    resume_file VARCHAR(255) NULL,
    CONSTRAINT fk_resume_user FOREIGN KEY(user_id) REFERENCES user(user_id)
);

-- 면접
CREATE TABLE interview (
    interview_id BIGINT NOT NULL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    resume_id BIGINT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    CONSTRAINT fk_interview_user FOREIGN KEY(user_id) REFERENCES user(user_id),
    CONSTRAINT fk_interview_resume FOREIGN KEY(resume_id) REFERENCES resume(resume_id)
);

-- 이력서 기반 질문
CREATE TABLE question (
    question_id BIGINT NOT NULL PRIMARY KEY,
    interview_id BIGINT NOT NULL,
    resume_id BIGINT NOT NULL,
    question_content TEXT NOT NULL,
    category VARCHAR(50) NULL,
    CONSTRAINT fk_question_interview FOREIGN KEY(interview_id) REFERENCES interview(interview_id),
    CONSTRAINT fk_question_resume FOREIGN KEY(resume_id) REFERENCES resume(resume_id)
);

-- 답변
CREATE TABLE answer (
    answer_id BIGINT NOT NULL PRIMARY KEY,
    question_id BIGINT NOT NULL,
    interview_id BIGINT NOT NULL,
    answer_content TEXT NULL,
    audio_file VARCHAR(255) NULL,
    video_file VARCHAR(255) NULL,
    CONSTRAINT fk_answer_question FOREIGN KEY(question_id) REFERENCES question(question_id),
    CONSTRAINT fk_answer_interview FOREIGN KEY(interview_id) REFERENCES interview(interview_id)
);

-- 분석결과
CREATE TABLE analysis (
    analysis_id BIGINT NOT NULL PRIMARY KEY,
    answer_id BIGINT NOT NULL,
    description TEXT NULL,
    data_file VARCHAR(255) NULL,
    created_at DATETIME NOT NULL,
    CONSTRAINT fk_analysis_answer FOREIGN KEY(answer_id) REFERENCES answer(answer_id)
);




