// GlobalModelAttributes.java
package com.example.Interview.config;

// import com.example.Interview.entity.Member;
// import com.example.Interview.repository.MemberRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.lang.Nullable;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ModelAttribute;

@ControllerAdvice
@RequiredArgsConstructor
public class GlobalModelAttributes {

    // private final MemberRepository memberRepository;

    @ModelAttribute("_csrf")
    public @Nullable CsrfToken csrfToken(@Nullable CsrfToken token) { return token; }


    @ModelAttribute("isLoggedIn")
    public boolean isLoggedIn(@Nullable Authentication authentication) {
        return authentication != null
                && authentication.isAuthenticated()
                && !(authentication instanceof AnonymousAuthenticationToken);
    }

    /*
    @ModelAttribute("nickname")
    public String nickname(@Nullable Authentication authentication) {
        if (!isLoggedIn(authentication)) return "";

        // username은 보통 email로 설정돼 있음
        String email = null;
        Object principal = authentication.getPrincipal();

        if (principal instanceof org.springframework.security.core.userdetails.UserDetails u) {
            email = u.getUsername();     // 대부분 여기로 들어옴
        } else {
            email = authentication.getName();  // 혹시모를 폴백
        }

        if (email == null || email.isBlank()) return "";
        // 엔티티에서 email을 소문자로 저장하므로 조회도 소문자로 맞춤(PrePersist 참고)
        return memberRepository.findByEmail(email.toLowerCase())
                .map(Member::getNickname)
                .orElse(""); // 계정이 삭제/비활성화된 드문 경우 대비
    }
    */
}
