package com.example.Interview.dto;

import com.example.Interview.entity.Member;
import lombok.AllArgsConstructor;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@AllArgsConstructor
public class MemberResponse {
    private Long id;
    private String email;
    private String nickname;
    private LocalDateTime createdAt;

    public static MemberResponse from(Member m) {
        return new MemberResponse(m.getId(), m.getEmail(), m.getNickname(), m.getCreatedAt());
    }
}
