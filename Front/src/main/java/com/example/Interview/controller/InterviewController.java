package com.example.Interview.controller;

import com.example.Interview.service.FeedbackService;
import com.example.Interview.service.InterviewService; // InterviewService 임포트 추가
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable; // PathVariable 임포트 추가
import org.springframework.web.bind.annotation.RequestMapping;
import reactor.core.publisher.Mono;

@Controller
@RequestMapping("/interview")
@RequiredArgsConstructor
public class InterviewController {

    private final FeedbackService feedbackService;
    private final InterviewService interviewService; // InterviewService 주입

    @GetMapping("/start")
    public Mono<String> startInterview(HttpSession session, Model model) {
        String token = (String) session.getAttribute("token");
        Integer resumeId = (Integer) session.getAttribute("resumeId");

        if (token == null || resumeId == null) {
            return Mono.just("redirect:/document-feedback");
        }

        return feedbackService.generateQuestions(token, resumeId)
                .map(questionList -> {
                    model.addAttribute("questions", questionList.getQuestions());
                    model.addAttribute("resumeId", resumeId);
                    model.addAttribute("token", token); // token을 모델에 추가
                    return "interview/interview-start";
                })
                .onErrorResume(e -> Mono.just("redirect:/document-feedback"));
    }

    @GetMapping("/{interviewId}/results")
    public Mono<String> getInterviewResults(@PathVariable Long interviewId, HttpSession session, Model model) {
        String token = (String) session.getAttribute("token");
        if (token == null) {
            return Mono.just("redirect:/auth/login");
        }

        return interviewService.getInterviewResults(interviewId, token)
                .map(analysisDto -> {
                    model.addAttribute("analysis", analysisDto);
                    return "interview/interview-results";
                })
                .onErrorResume(e -> Mono.just("redirect:/")); // 에러 발생 시 홈으로
    }
}
