package com.example.Interview.api;

import com.example.Interview.dto.UserDto;
import com.example.Interview.service.UserService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/my-page")
@RequiredArgsConstructor
public class MyPageApiController {

    private final UserService userService;

    @GetMapping("/profile")
    public Mono<ResponseEntity<UserDto>> getUserProfile(HttpSession session) {
        String token = (String) session.getAttribute("token");
        if (token == null) {
            return Mono.error(new ResponseStatusException(HttpStatus.UNAUTHORIZED, "로그인이 필요합니다."));
        }
        return userService.getUserProfile(token)
                .map(ResponseEntity::ok)
                .onErrorResume(e -> {
                    System.err.println("Error fetching user profile: " + e.getMessage());
                    return Mono.error(new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "사용자 프로필을 불러오는데 실패했습니다.", e));
                });
    }

    @PutMapping("/profile")
    public Mono<ResponseEntity<UserDto>> updateUserProfile(@RequestBody UserDto userDto, HttpSession session) {
        String token = (String) session.getAttribute("token");
        if (token == null) {
            return Mono.error(new ResponseStatusException(HttpStatus.UNAUTHORIZED, "로그인이 필요합니다."));
        }
        return userService.updateUserProfile(token, userDto)
                .map(ResponseEntity::ok)
                .onErrorResume(e -> {
                    System.err.println("Error updating user profile: " + e.getMessage());
                    return Mono.error(new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "사용자 프로필을 업데이트하는데 실패했습니다.", e));
                });
    }
}
