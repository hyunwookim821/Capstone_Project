package com.example.Interview.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new LoginCheckInterceptor())
                .order(1) // 인터셉터 체인 순서
                .addPathPatterns("/**") // 모든 경로에 인터셉터 적용
                .excludePathPatterns(
                        "/", "/start", "/free-start", "/auth/login", "/auth/signup", "/api/auth/login", "/api/auth/signup",
                        "/css/**", "/js/**", "/*.ico", "/error"
                ); // 제외할 경로 지정
    }
}
