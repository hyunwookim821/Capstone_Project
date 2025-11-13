package com.example.Interview.dto;

import com.example.Interview.entity.JobCategory;
import com.example.Interview.entity.Member;
import lombok.*;

import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SignupRequest {

    private String nickname;         // 필수
    private String email;            // 필수
    private String password;         // 필수
    private String confirmPassword;  // 필수
    private String jobCategory;      // 선택 (it/marketing/...)
    private boolean marketing;       // 선택 체크박스
    private boolean terms;           // 필수 체크박스

    public Member toEntity(String encodedPassword) {
        return Member.builder()
                .email(email == null ? null : email.toLowerCase())
                .passwordHash(encodedPassword)
                .nickname(nickname)
                .jobCategory(JobCategory.fromFormValue(jobCategory))
                .marketingOptIn(marketing)
                .termsAgreedAt(LocalDateTime.now())
                .build();
    }
}
