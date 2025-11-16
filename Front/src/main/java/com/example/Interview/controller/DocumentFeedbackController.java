package com.example.Interview.controller;

import com.example.Interview.service.FeedbackService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import reactor.core.publisher.Mono;

@Controller
@RequestMapping("/document-feedback")
@RequiredArgsConstructor
public class DocumentFeedbackController {

    private final FeedbackService feedbackService;

    @GetMapping
    public String documentFeedbackPage() {
        return "document-feedback/document-feedback";
    }

    @GetMapping("/feedback-result")
    public Mono<String> feedbackResultPage(HttpSession session, Model model) {
        String token = (String) session.getAttribute("token");
        Integer resumeId = (Integer) session.getAttribute("resumeId");
        String originalContent = (String) session.getAttribute("originalContent");

        if (token == null || resumeId == null) {
            return Mono.just("redirect:/document-feedback");
        }

        return feedbackService.checkGrammar(token, resumeId)
                .map(grammarAnalysis -> {
                    model.addAttribute("originalText", originalContent);
                    model.addAttribute("correctedText", grammarAnalysis.getCorrectedSentence());
                    return "document-feedback/feedback-result";
                })
                .onErrorResume(e -> Mono.just("redirect:/document-feedback")); // 에러 발생 시 리다이렉트
    }

    @GetMapping("/interview-questions")
    public Mono<String> interviewQuestionsPage(HttpSession session, Model model) {
        String token = (String) session.getAttribute("token");
        Integer resumeId = (Integer) session.getAttribute("resumeId");

        if (token == null || resumeId == null) {
            return Mono.just("redirect:/document-feedback");
        }

        return feedbackService.generateQuestions(token, resumeId)
                .map(questionList -> {
                    model.addAttribute("questions", questionList.getQuestions());
                    return "document-feedback/interview-questions";
                })
                .onErrorResume(e -> Mono.just("redirect:/document-feedback")); // 에러 발생 시 리다이렉트
    }
}
