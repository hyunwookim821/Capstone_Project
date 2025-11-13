package com.example.Interview.repository;

import com.example.Interview.entity.Member;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface MemberRepository extends JpaRepository<Member, Long> {

    // 이메일(대소문자 무시) 중복 체크/조회
    boolean existsByEmailIgnoreCase(String email);
    Optional<Member> findByEmailIgnoreCase(String email);

    // 닉네임 중복 체크/조회
    boolean existsByNickname(String nickname);
    Optional<Member> findByNickname(String nickname);

    Optional<Member> findByEmail(String email);
}
