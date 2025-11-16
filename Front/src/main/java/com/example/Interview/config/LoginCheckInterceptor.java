package com.example.Interview.config;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import org.springframework.web.servlet.HandlerInterceptor;

public class LoginCheckInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        String requestURI = request.getRequestURI();
        HttpSession session = request.getSession(false);

        if (session == null || session.getAttribute("token") == null) {
            // 로그인이 되어있지 않은 경우, 메인 페이지로 리다이렉트
            response.sendRedirect("/");
            return false; // 컨트롤러 실행 중단
        }

        return true; // 로그인 되어있으면 컨트롤러 실행
    }
}
