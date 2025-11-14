package com.example.Interview.service;

import com.example.Interview.dto.UserDto;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Service
public class UserService {

    private final WebClient webClient;

    public UserService(WebClient webClient) {
        this.webClient = webClient;
    }

    public Mono<UserDto> getUserProfile(String token) {
        return webClient.get()
                .uri("/users/me")
                .headers(headers -> headers.setBearerAuth(token))
                .retrieve()
                .bodyToMono(UserDto.class);
    }

    public Mono<UserDto> updateUserProfile(String token, UserDto userDto) {
        return webClient.put()
                .uri("/users/me")
                .headers(headers -> headers.setBearerAuth(token))
                .body(Mono.just(userDto), UserDto.class)
                .retrieve()
                .bodyToMono(UserDto.class);
    }
}
