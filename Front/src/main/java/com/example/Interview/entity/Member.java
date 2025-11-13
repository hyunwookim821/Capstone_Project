package com.example.Interview.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "member", indexes = {
        @Index(name = "uk_member_email", columnList = "email", unique = true),
        @Index(name = "uk_member_nickname", columnList = "nickname", unique = true)
})
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Member {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 191, unique = true)
    private String email;

    @Column(nullable = false, length = 100)
    private String passwordHash;

    @Column(nullable = false, length = 40, unique = true)
    private String nickname;

    @Enumerated(EnumType.STRING)
    @Column(length = 30)
    private JobCategory jobCategory;

    @Column(nullable = false)
    private boolean marketingOptIn;

    @Column(nullable = false)
    private LocalDateTime termsAgreedAt;

    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    @PrePersist
    public void onCreate() {
        LocalDateTime now = LocalDateTime.now();
        this.createdAt = now;
        this.updatedAt = now;
        if (this.email != null) this.email = this.email.toLowerCase();
    }

    @PreUpdate
    public void onUpdate() {
        this.updatedAt = LocalDateTime.now();
        if (this.email != null) this.email = this.email.toLowerCase();
    }
}
