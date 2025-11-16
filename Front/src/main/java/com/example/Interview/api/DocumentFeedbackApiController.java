package com.example.Interview.api;

import com.example.Interview.dto.feedback.AIFeedbackDto;
import com.example.Interview.service.FeedbackService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import reactor.core.publisher.Mono;

import java.util.Map;

@RestController
@RequestMapping("/api/feedback")
@RequiredArgsConstructor
public class DocumentFeedbackApiController {

    private final FeedbackService feedbackService;

    @PostMapping("/upload")
    public Mono<ResponseEntity<Map<String, String>>> uploadAndAnalyze(
            @RequestParam("document") MultipartFile file,
            HttpSession session) {

        String token = (String) session.getAttribute("token");
        if (token == null) {
            return Mono.just(ResponseEntity.status(401).body(Map.of("message", "Unauthorized")));
        }

        if (file.isEmpty()) {
            return Mono.just(ResponseEntity.badRequest().build());
        }

        return feedbackService.uploadAndCreateResume(token, file)
                .doOnSuccess(resumeDto -> {
                    // 이력서 ID를 세션에 저장
                    session.setAttribute("resumeId", resumeDto.getResumeId());
                    session.setAttribute("originalContent", resumeDto.getContent()); // 원본 내용도 저장
                })
                .map(resumeDto -> ResponseEntity.ok(Map.of("redirectUrl", "/document-feedback/feedback-result")));
    }

    @PostMapping("/ai-feedback")
    public Mono<AIFeedbackDto> getAiFeedback(HttpSession session) {
        String token = (String) session.getAttribute("token");
        Integer resumeId = (Integer) session.getAttribute("resumeId");

        if (token == null || resumeId == null) {
            // 적절한 예외 처리 또는 에러 응답
            return Mono.error(new IllegalStateException("User not authenticated or resumeId not found"));
        }

        return feedbackService.getAiFeedback(token, resumeId);
    }
}
