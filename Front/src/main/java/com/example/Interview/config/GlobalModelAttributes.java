package com.example.Interview.config;

import com.example.Interview.service.UserService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.lang.Nullable;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ModelAttribute;

@ControllerAdvice
@RequiredArgsConstructor
public class GlobalModelAttributes {

    private final UserService userService;

    @ModelAttribute("_csrf")
    public @Nullable CsrfToken csrfToken(@Nullable CsrfToken token) {
        return token;
    }

    @ModelAttribute("isLoggedIn")
    public boolean isLoggedIn(HttpSession session) {
        return session.getAttribute("token") != null;
    }

    @ModelAttribute("nickname")
    public String nickname(HttpSession session) {
        if (isLoggedIn(session)) {
            try {
                String token = (String) session.getAttribute("token");
                // In a real-world scenario, consider handling the blocking call more gracefully
                return userService.getUserProfile(token).block().getUserName();
            } catch (Exception e) {
                // Log the exception and return a default nickname
                System.err.println("Error fetching user profile: " + e.getMessage());
                return "사용자";
            }
        }
        return "";
    }
}
