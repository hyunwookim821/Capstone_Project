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
import org.springframework.web.bind.annotation.RequestParam;
import reactor.core.publisher.Mono;

@Controller
@RequestMapping("/interview")
@RequiredArgsConstructor
public class InterviewController {

    private final FeedbackService feedbackService;
    private final InterviewService interviewService; // InterviewService 주입

    @GetMapping("/start")
    public String startInterview(
            @RequestParam Integer resumeId,
            // This parameter is no longer needed here but kept to avoid breaking links
            @RequestParam(required = false) Boolean use_existing_questions,
            HttpSession session,
            Model model
    ) {
        String token = (String) session.getAttribute("token");

        if (token == null || resumeId == null) {
            return "redirect:/document-feedback";
        }

        model.addAttribute("resumeId", resumeId);
        model.addAttribute("token", token);
        return "interview/interview-start";
    }

    @GetMapping("/{interviewId}/results")
    public Mono<String> getInterviewResults(@PathVariable Long interviewId, HttpSession session, Model model) {
        final String token = (String) session.getAttribute("token");
        if (token == null) {
            return Mono.just("redirect:/auth/login");
        }

        return interviewService.getInterviewResults(interviewId, token)
                .map(analysisDto -> {
                    model.addAttribute("analysis", analysisDto);
                    return "interview/interview-results";
                })
                .onErrorResume(e -> {
                    // Log the error for debugging and pass it to the view
                    System.err.println("Error fetching interview results: " + e.getMessage());
                    model.addAttribute("errorMessage", "면접 결과를 가져오는 중 오류가 발생했습니다: " + e.getMessage());
                    return Mono.just("error"); // 에러 페이지로 이동
                });
    }}
