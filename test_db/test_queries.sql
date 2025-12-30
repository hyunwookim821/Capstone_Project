use ai_joppass;

-- 1-1. 전체 회원 조회
SELECT * FROM user;

-- 1-2. 전체 이력서 조회
SELECT r.resume_id, u.user_name, r.title, r.create_at, r.content, r.resume_file
FROM resume r
JOIN user u ON r.user_id = u.user_id
ORDER BY r.create_at DESC;

-- 1-3. 전체 면접 조회
SELECT i.interview_id, u.user_name, r.title, i.start_time, i.end_time
FROM interview i
JOIN user u ON i.user_id = u.user_id
JOIN resume r ON i.resume_id = r.resume_id
ORDER BY i.start_time DESC;


-- 2. NULL 데이터 확인

-- 2-1. 프로필 이미지 없는 회원
SELECT user_id, user_name, email
FROM user
WHERE profileimage IS NULL;

-- 2-2. 내용이나 파일이 없는 이력서
SELECT resume_id, user_id, title,
       CASE WHEN content IS NULL THEN '내용없음' ELSE '있음' END as content_status,
       CASE WHEN resume_file IS NULL THEN '파일없음' ELSE '있음' END as file_status
FROM resume
WHERE content IS NULL OR resume_file IS NULL;

-- 2-3. 카테고리 미분류 질문
SELECT question_id, interview_id, question_content
FROM question
WHERE category IS NULL;

-- 2-4. 답변 상태 확인 (미답변, 부분답변 등)
SELECT a.answer_id, q.question_content,
       CASE WHEN a.answer_content IS NULL THEN '텍스트없음' ELSE '있음' END as text_status,
       CASE WHEN a.audio_file IS NULL THEN '오디오없음' ELSE '있음' END as audio_status,
       CASE WHEN a.video_file IS NULL THEN '비디오없음' ELSE '있음' END as video_status
FROM answer a
JOIN question q ON a.question_id = q.question_id
WHERE a.answer_content IS NULL
   OR a.audio_file IS NULL
   OR a.video_file IS NULL;

-- 3-1. 특정 회원의 면접 이력 전체
SELECT
    u.user_name,
    r.title as resume_title,
    i.start_time,
    q.question_content,
    q.category,
    a.answer_content,
    an.description as analysis_result
FROM user u
JOIN resume r ON u.user_id = r.user_id
JOIN interview i ON r.resume_id = i.resume_id
JOIN question q ON i.interview_id = q.interview_id
LEFT JOIN answer a ON q.question_id = a.question_id
LEFT JOIN analysis an ON a.answer_id = an.answer_id
WHERE u.user_id = 1001
ORDER BY i.start_time, q.question_id;

-- 4-1. 회원별 활동 현황
SELECT
    u.user_id,
    u.user_name,
    COUNT(DISTINCT r.resume_id) as resume_count,
    COUNT(DISTINCT i.interview_id) as interview_count,
    COUNT(DISTINCT q.question_id) as question_count,
    COUNT(DISTINCT a.answer_id) as answer_count
FROM user u
LEFT JOIN resume r ON u.user_id = r.user_id
LEFT JOIN interview i ON u.user_id = i.user_id
LEFT JOIN question q ON i.interview_id = q.interview_id
LEFT JOIN answer a ON q.question_id = a.question_id
GROUP BY u.user_id, u.user_name
ORDER BY u.user_id;

-- 4-2. 카테고리별 질문 개수
SELECT
    COALESCE(category, '미분류') as category,
    COUNT(*) as question_count
FROM question
GROUP BY category
ORDER BY question_count DESC;

-- 4-3. 면접별 답변 완성률
SELECT
    i.interview_id,
    u.user_name,
    r.title,
    COUNT(q.question_id) as total_questions,
    SUM(CASE WHEN a.answer_content IS NOT NULL THEN 1 ELSE 0 END) as answered_count,
    ROUND(SUM(CASE WHEN a.answer_content IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(q.question_id), 2) as answer_rate
FROM interview i
JOIN user u ON i.user_id = u.user_id
JOIN resume r ON i.resume_id = r.resume_id
JOIN question q ON i.interview_id = q.interview_id
LEFT JOIN answer a ON q.question_id = a.question_id
GROUP BY i.interview_id, u.user_name, r.title
ORDER BY answer_rate DESC;

-- 5-1. 답변 완성도가 높은 사용자
SELECT
    u.user_id,
    u.user_name,
    COUNT(a.answer_id) as total_answers,
    SUM(CASE
        WHEN a.answer_content IS NOT NULL
         AND a.audio_file IS NOT NULL
         AND a.video_file IS NOT NULL
        THEN 1 ELSE 0
    END) as complete_answers,
    ROUND(SUM(CASE
        WHEN a.answer_content IS NOT NULL
         AND a.audio_file IS NOT NULL
         AND a.video_file IS NOT NULL
        THEN 1 ELSE 0
    END) * 100.0 / COUNT(a.answer_id), 2) as completion_rate
FROM user u
JOIN interview i ON u.user_id = i.user_id
JOIN question q ON i.interview_id = q.interview_id
JOIN answer a ON q.question_id = a.question_id
GROUP BY u.user_id, u.user_name
HAVING COUNT(a.answer_id) > 0
ORDER BY completion_rate DESC;
