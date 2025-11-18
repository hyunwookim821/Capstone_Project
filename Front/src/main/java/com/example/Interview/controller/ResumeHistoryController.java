package com.example.Interview.controller;

import com.example.Interview.dto.feedback.ResumeDetailDto;
import com.example.Interview.service.ResumeService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import reactor.core.publisher.Mono;

@Controller
@RequestMapping("/resumes/history")
@RequiredArgsConstructor
public class ResumeHistoryController {

    private final ResumeService resumeService;

    @GetMapping("/{resumeId}")
    public Mono<String> getResumeHistoryDetail(@PathVariable Long resumeId, HttpSession session, Model model) {
        String token = (String) session.getAttribute("token");
        if (token == null) {
            return Mono.just("redirect:/auth/login");
        }

        return resumeService.getResume(resumeId, token)
                .map(resumeDetail -> {
                    model.addAttribute("resume", resumeDetail);
                    model.addAttribute("grammarAnalysis", resumeDetail); // for correctedText
                    model.addAttribute("aiFeedback", resumeDetail); // for feedback
                    model.addAttribute("questions", resumeDetail.getGeneratedQuestions());
                    return "resume-history-detail/resume-history-detail";
                })
                .onErrorResume(e -> {
                    System.err.println("Error loading resume history detail: " + e.getMessage());
                    e.printStackTrace();
                    return Mono.just("redirect:/myPage"); // 에러 발생 시 마이페이지로 리다이렉트
                });
    }
}
