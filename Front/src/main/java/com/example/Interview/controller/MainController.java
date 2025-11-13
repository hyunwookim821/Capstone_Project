package com.example.Interview.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

@Controller
public class MainController {

    @GetMapping("/")
    public String main(Model model) {
        // 통계 데이터
        List<Map<String, String>> stats = Arrays.asList(
                Map.of("number", "10,000+", "label", "사용자"),
                Map.of("number", "95%", "label", "만족도"),
                Map.of("number", "4.8", "label", "평균 평점"),
                Map.of("number", "24/7", "label", "언제든 이용")
        );

        // 기능 데이터
        List<Map<String, String>> features = Arrays.asList(
                Map.of(
                        "icon", "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z\"></path>",
                        "title", "AI 면접관",
                        "description", "실제 면접관처럼 질문하고 피드백을 제공하는 AI 시스템"
                ),
                Map.of(
                        "icon", "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z\"></path>",
                        "title", "맞춤형 질문",
                        "description", "직무와 경력에 맞는 개인화된 면접 질문 생성"
                ),
                Map.of(
                        "icon", "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z\"></path>",
                        "title", "실시간 분석",
                        "description", "답변 내용, 말하기 속도, 자신감 등을 실시간으로 분석"
                ),
                Map.of(
                        "icon", "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253\"></path>",
                        "title", "상세한 피드백",
                        "description", "면접 후 상세한 분석 리포트와 개선점 제안"
                )
        );

        // 단계 데이터
        List<Map<String, Object>> steps = Arrays.asList(
                Map.of(
                        "step", "STEP 01",
                        "title", "회원가입",
                        "description", "간단한 정보 입력으로 빠르게 시작하세요",
                        "icon", "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z\"></path>",
                        "showArrow", true
                ),
                Map.of(
                        "step", "STEP 02",
                        "title", "면접 설정",
                        "description", "직무와 레벨에 맞는 면접을 선택하세요",
                        "icon", "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z\"></path><path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M15 12a3 3 0 11-6 0 3 3 0 016 0z\"></path>",
                        "showArrow", true
                ),
                Map.of(
                        "step", "STEP 03",
                        "title", "실전 연습",
                        "description", "AI와 함께 실제같은 면접을 경험하세요",
                        "icon", "<path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M13 10V3L4 14h7v7l9-11h-7z\"></path>",
                        "showArrow", false
                )
        );

        // 후기 데이터
        List<Map<String, Object>> testimonials = Arrays.asList(
                Map.of(
                        "content", "면접 시뮬레이터 덕분에 실제 면접에서 긴장하지 않고 좋은 결과를 얻을 수 있었어요. 정말 실제 면접관과 대화하는 것 같았습니다!",
                        "name", "김민수",
                        "role", "개발자",
                        "stars", Arrays.asList(1, 2, 3, 4, 5)
                ),
                Map.of(
                        "content", "다양한 질문 유형과 즉시 피드백이 정말 도움이 되었습니다. 특히 답변의 구조화 방법을 배울 수 있어서 좋았어요.",
                        "name", "이지은",
                        "role", "마케터",
                        "stars", Arrays.asList(1, 2, 3, 4, 5)
                ),
                Map.of(
                        "content", "언제든지 연습할 수 있다는 점이 가장 큰 장점이에요. 밤늦게도, 주말에도 면접 연습을 할 수 있어서 정말 편리했습니다.",
                        "name", "박준영",
                        "role", "디자이너",
                        "stars", Arrays.asList(1, 2, 3, 4, 5)
                )
        );

        model.addAttribute("stats", stats);
        model.addAttribute("features", features);
        model.addAttribute("steps", steps);
        model.addAttribute("testimonials", testimonials);

        return "view/main";
    }
}
