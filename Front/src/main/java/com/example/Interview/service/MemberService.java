// src/main/java/com/example/Interview/simulator/service/MemberService.java
package com.example.Interview.service;

import com.example.Interview.repository.MemberRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class MemberService {
    private final MemberRepository memberRepository;

    public Long getCurrentMemberId() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated() || "anonymousUser".equals(auth.getPrincipal())) {
            throw new IllegalStateException("로그인이 필요합니다.");
        }
        String username = auth.getName(); // 보통 email 또는 username
        return memberRepository.findByEmail(username)   // email 로그인이라면
                .orElseThrow(() -> new IllegalStateException("회원 정보를 찾을 수 없습니다."))
                .getId();
    }
}