package com.example.Interview.controller;

import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
@RequiredArgsConstructor
public class PageController {

    @GetMapping("/selection")
    public String onboarding(Model model, HttpSession session) {
        String token = (String) session.getAttribute("token");
        if (token == null) {
            // If token is not in session, redirect to login
            return "redirect:/auth/login";
        }
        model.addAttribute("token", token);
        return "view/selection";
    }
}
