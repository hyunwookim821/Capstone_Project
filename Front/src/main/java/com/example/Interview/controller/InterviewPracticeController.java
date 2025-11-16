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
@RequestMapping("/interview-practice")
@RequiredArgsConstructor
public class InterviewPracticeController {

    private final FeedbackService feedbackService;

    @GetMapping
    public Mono<String> interviewPracticePage(HttpSession session, Model model) {
        String token = (String) session.getAttribute("token");
        Integer resumeId = (Integer) session.getAttribute("resumeId");

        if (token == null || resumeId == null) {
            // 면접을 시작할 이력서 정보가 없으면 피드백 페이지로 리다이렉트
            return Mono.just("redirect:/document-feedback");
        }

        // 면접에 사용할 질문 목록을 다시 가져옴
        return feedbackService.generateQuestions(token, resumeId)
                .map(questionList -> {
                    model.addAttribute("questions", questionList.getQuestions());
                    return "interview-practice/interview-practice";
                })
                .onErrorResume(e -> Mono.just("redirect:/document-feedback"));
    }
}