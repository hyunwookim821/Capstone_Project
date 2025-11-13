package com.example.Interview.controller;

import com.example.Interview.dto.SignupRequest;
import com.example.Interview.service.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@RequestMapping("/auth")
@Controller
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @GetMapping("/login")
    public String login(@RequestParam(value = "error", required = false) String error, Model model) {
        if (error != null) model.addAttribute("error", "이메일 또는 비밀번호가 올바르지 않습니다.");
        return "auth/login";
    }

    @GetMapping("/signup")
    public String signup() {
        return "auth/signup";
    }

    @PostMapping("/signup")
    public String processSignup(@ModelAttribute SignupRequest req,
                                RedirectAttributes ra) {
        try {
            authService.signup(req);
            ra.addFlashAttribute("success", "회원가입이 완료되었습니다. 로그인해주세요.");
            return "redirect:/auth/login";
        } catch (ResponseStatusException e) {
            ra.addFlashAttribute("error", e.getReason() != null ? e.getReason() : "회원가입 중 오류가 발생했습니다.");
            return "redirect:/auth/signup";
        } catch (Exception e) {
            ra.addFlashAttribute("error", "회원가입 중 오류가 발생했습니다.");
            return "redirect:/auth/signup";
        }
    }
}
