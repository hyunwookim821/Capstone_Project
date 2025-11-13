// src/main/java/com/example/Interview/simulator/controller/PageController.java
package com.example.Interview.controller;

import com.example.Interview.service.MemberService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
@RequiredArgsConstructor
public class PageController {

    private final MemberService memberService; // 추가

    @GetMapping("/selection")
    public String onboarding(Model model) {
        model.addAttribute("memberId", memberService.getCurrentMemberId()); // ✅ 서비스 통해 조회
        return "view/selection";
    }
}
