package com.example.Interview.service;

import com.example.Interview.dto.ResumeDto;
import com.example.Interview.dto.feedback.AIFeedbackDto;
import com.example.Interview.dto.feedback.GrammarAnalysisDto;
import com.example.Interview.dto.feedback.QuestionListDto;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.core.io.buffer.DataBufferUtils;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.io.IOException;

@Service
@RequiredArgsConstructor
public class FeedbackService {

    private final WebClient webClient;

    // 1. 파일 업로드 및 이력서 생성
    public Mono<ResumeDto> uploadAndCreateResume(String token, MultipartFile file) {
        MultipartBodyBuilder builder = new MultipartBodyBuilder();
        builder.part("title", file.getOriginalFilename());
        builder.part("file", file.getResource());

        return webClient.post()
                .uri("/resumes/")
                .headers(headers -> headers.setBearerAuth(token))
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(BodyInserters.fromMultipartData(builder.build()))
                .retrieve()
                .bodyToMono(ResumeDto.class);
    }

    // 2. 맞춤법 검사
    public Mono<GrammarAnalysisDto> checkGrammar(String token, int resumeId) {
        return webClient.post()
                .uri("/resumes/{resume_id}/check-grammar", resumeId)
                .headers(headers -> headers.setBearerAuth(token))
                .retrieve()
                .bodyToMono(GrammarAnalysisDto.class);
    }

    // 3. AI 종합 피드백 요청
    public Mono<AIFeedbackDto> getAiFeedback(String token, int resumeId) {
        return webClient.post()
                .uri("/resumes/{resume_id}/feedback", resumeId)
                .headers(headers -> headers.setBearerAuth(token))
                .retrieve()
                .bodyToMono(AIFeedbackDto.class);
    }

    // 4. 예상 면접 질문 생성
    public Mono<QuestionListDto> generateQuestions(String token, int resumeId) {
        return webClient.post()
                .uri("/resumes/{resume_id}/generate-questions", resumeId)
                .headers(headers -> headers.setBearerAuth(token))
                .retrieve()
                .bodyToMono(QuestionListDto.class);
    }
}
