package com.example.Interview.service;

import com.example.Interview.dto.ResumeDto;
import com.example.Interview.dto.feedback.ResumeDetailDto; // ResumeDetailDto 임포트
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ResumeService {

    private final WebClient webClient;

    public Mono<List<ResumeDto>> getResumes(String token) {
        return webClient.get()
                .uri("/resumes/")
                .header("Authorization", "Bearer " + token)
                .retrieve()
                .bodyToFlux(ResumeDto.class)
                .collectList();
    }

    public Mono<ResumeDetailDto> getResume(Long id, String token) {
        return webClient.get()
                .uri("/resumes/" + id)
                .header("Authorization", "Bearer " + token)
                .retrieve()
                .bodyToMono(ResumeDetailDto.class);
    }

    public Mono<ResumeDto> createResume(String token, MultipartFile file) {
        MultipartBodyBuilder builder = new MultipartBodyBuilder();
        builder.part("title", file.getOriginalFilename());
        builder.part("file", file.getResource());

        return webClient.post()
                .uri("/resumes/")
                .headers(headers -> headers.setBearerAuth(token))
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(BodyInserters.fromMultipartData(builder.build()))
                .retrieve()
                .bodyToMono(ResumeDto.class);
    }

    public Mono<Void> deleteResume(Long id, String token) {
        return webClient.delete()
                .uri("/resumes/" + id)
                .header("Authorization", "Bearer " + token)
                .retrieve()
                .bodyToMono(Void.class);
    }
}
