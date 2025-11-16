package com.example.Interview.service;

import com.example.Interview.dto.InterviewSessionDto;
import com.example.Interview.dto.AnalysisDto; // AnalysisDto 임포트 추가
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class InterviewService {

    private final WebClient webClient;

    // 파라미터 순서 및 타입 변경: (Long resumeId, String token)
    public Mono<InterviewSessionDto> createInterviewSession(Long resumeId, String token) {
        return webClient.post()
                .uri(uriBuilder -> uriBuilder.path("/interviews/")
                        .queryParam("resume_id", resumeId)
                        .build())
                .headers(headers -> headers.setBearerAuth(token))
                .retrieve()
                .bodyToMono(InterviewSessionDto.class);
    }

    // 컴파일 에러 해결을 위한 임시 플레이스홀더 메소드
    public Mono<AnalysisDto> getInterviewResults(Long interviewId, String token) {
        // TODO: 실제 백엔드 API 연동 로직 구현 필요
        return webClient.get()
                .uri("/interviews/{interviewId}/results", interviewId)
                .headers(headers -> headers.setBearerAuth(token))
                .retrieve()
                .bodyToMono(AnalysisDto.class);
    }

    // 컴파일 에러 해결을 위한 임시 플레이스홀더 메소드
    public Mono<Void> sendVideoAnalysisData(Long interviewId, List<Map<String, Object>> landmarkData, String token) {
        // TODO: 실제 백엔드 API 연동 로직 구현 필요
        return Mono.empty();
    }
}