package com.example.Interview.controller;

import com.example.Interview.dto.UserDto;
import com.example.Interview.dto.ResumeDto; // ResumeDto 임포트 추가
import com.example.Interview.dto.InterviewHistoryDto; // InterviewHistoryDto 임포트 추가
import com.example.Interview.service.ResumeService;
import com.example.Interview.service.UserService;
import com.example.Interview.service.InterviewService; // InterviewService 임포트 추가
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.server.ResponseStatusException;
import reactor.core.publisher.Mono;

import java.util.List; // List 임포트 추가

@RequestMapping("myPage")
@Controller
@RequiredArgsConstructor
public class MyPageController {

    private final UserService userService;
    private final ResumeService resumeService; // ResumeService 주입
    private final InterviewService interviewService; // InterviewService 주입
    private final ObjectMapper objectMapper;

    @GetMapping
    public Mono<String> myPage(HttpSession session, Model model) {
        String token = (String) session.getAttribute("token");
        if (token == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "로그인이 필요합니다.");
        }

        // 1. 사용자 프로필 정보 Mono
        Mono<UserDto> userProfileMono = userService.getUserProfile(token);

        // 2. 사용자 이력서 목록 Mono
        Mono<List<ResumeDto>> resumesMono = resumeService.getResumes(token);

        // 3. 면접 이력 Mono
        Mono<List<InterviewHistoryDto>> interviewsMono = interviewService.getUserInterviews(token);

        // 4. 세 비동기 작업이 모두 완료된 후 Model에 데이터를 담고 페이지 렌더링
        return Mono.zip(userProfileMono, resumesMono, interviewsMono)
                .map(tuple -> {
                    UserDto userProfile = tuple.getT1();
                    List<ResumeDto> resumes = tuple.getT2();
                    List<InterviewHistoryDto> interviews = tuple.getT3();

                    // 피드백이 있는 이력서만 필터링
                    List<ResumeDto> feedbackResumes = resumes.stream()
                            .filter(r -> r.getAiFeedback() != null && !r.getAiFeedback().isEmpty())
                            .toList();

                    try {
                        String userJson = objectMapper.writeValueAsString(userProfile);
                        model.addAttribute("userJson", userJson);

                        // resumes를 JSON으로 변환하여 모델에 추가
                        String resumesJson = objectMapper.writeValueAsString(resumes);
                        model.addAttribute("resumesJson", resumesJson);

                        // interviews를 JSON으로 변환하여 모델에 추가
                        String interviewsJson = objectMapper.writeValueAsString(interviews);
                        model.addAttribute("interviewsJson", interviewsJson);

                    } catch (JsonProcessingException e) {
                        // JsonProcessingException 발생 시 RuntimeException을 던져 onErrorResume에서 처리
                        throw new RuntimeException("Error serializing data to JSON", e);
                    }

                    model.addAttribute("resumes", resumes);
                    model.addAttribute("feedbackResumes", feedbackResumes); // 필터링된 목록을 모델에 추가
                    model.addAttribute("interviews", interviews); // 면접 이력 추가
                    model.addAttribute("token", token);
                    return "/myPage/myPage";
                })
                .onErrorResume(e -> {
                    System.err.println("Error loading myPage data: " + e.getMessage());
                    e.printStackTrace(); // 전체 스택 트레이스 출력
                    return Mono.just("redirect:/"); // 에러 발생 시 홈으로 리다이렉트
                });
    }
}
