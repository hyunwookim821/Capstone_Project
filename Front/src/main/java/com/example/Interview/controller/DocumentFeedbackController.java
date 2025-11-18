package com.example.Interview.controller;

import com.example.Interview.dto.feedback.ResumeDetailDto;
import com.example.Interview.service.FeedbackService;
import com.example.Interview.service.ResumeService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import reactor.core.publisher.Mono;

import java.util.Map;

@Controller
@RequestMapping("/document-feedback")
@RequiredArgsConstructor
public class DocumentFeedbackController {

    private final FeedbackService feedbackService;
    private final ResumeService resumeService;

    @GetMapping
    public String documentFeedbackPage() {
        return "document-feedback/document-feedback";
    }

    @PostMapping("/upload")
    @ResponseBody
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
                    session.setAttribute("resumeId", resumeDto.getResumeId());
                })
                .map(resumeDto -> ResponseEntity.ok(Map.of("redirectUrl", "/document-feedback/feedback-result")));
    }

    @GetMapping("/feedback-result")
    public Mono<String> feedbackResultPage(HttpSession session, Model model) {
        String token = (String) session.getAttribute("token");
        Integer resumeId = (Integer) session.getAttribute("resumeId");

        if (token == null || resumeId == null) {
            return Mono.just("redirect:/document-feedback");
        }

        return feedbackService.checkGrammar(token, resumeId)
                .flatMap(result -> {
                    model.addAttribute("resumeId", resumeId);
                    model.addAttribute("originalText", result.getContent());
                    model.addAttribute("correctedText", result.getCorrectedContent());
                    model.addAttribute("feedback", result.getAiFeedback() != null ? result.getAiFeedback() : "");
                    return Mono.just("document-feedback/feedback-result");
                })
                .onErrorResume(e -> {
                    e.printStackTrace();
                    return Mono.just("redirect:/document-feedback");
                });
    }

    @PostMapping("/feedback/{resumeId}")
    @ResponseBody
    public Mono<String> getAiFeedback(@PathVariable int resumeId, HttpSession session) {
        String token = (String) session.getAttribute("token");
        if (token == null) {
            return Mono.error(new IllegalStateException("User not authenticated"));
        }
        return feedbackService.getAiFeedback(token, resumeId)
                .doOnNext(jsonString -> {
                    System.out.println("----------- Raw JSON Response from Backend -----------");
                    System.out.println(jsonString);
                    System.out.println("----------------------------------------------------");
                });
    }

    @GetMapping("/interview-questions")
    public Mono<String> interviewQuestionsPage(HttpSession session, Model model) {
        String token = (String) session.getAttribute("token");
        Integer resumeId = (Integer) session.getAttribute("resumeId");

        if (token == null || resumeId == null) {
            return Mono.just("redirect:/document-feedback");
        }

        return feedbackService.generateQuestions(token, resumeId)
                .map(resumeDetail -> {
                    model.addAttribute("questions", resumeDetail.getGeneratedQuestions());
                    model.addAttribute("resumeId", resumeId); // resumeId를 모델에 추가
                    return "document-feedback/interview-questions";
                })
                .onErrorResume(e -> Mono.just("redirect:/document-feedback"));
    }
}
