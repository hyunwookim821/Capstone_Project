package com.example.Interview.service;

import com.example.Interview.dto.ResumeDto;
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.core.io.buffer.DataBufferUtils;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;

import java.io.IOException;
import java.util.List;

@Service
public class ResumeService {

    private final WebClient webClient;

    public ResumeService(WebClient webClient) {
        this.webClient = webClient;
    }

    public List<ResumeDto> getResumes(String token) {
        return webClient.get()
                .uri("/resumes/")
                .header("Authorization", "Bearer " + token)
                .retrieve()
                .bodyToFlux(ResumeDto.class)
                .collectList()
                .block();
    }

    public ResumeDto getResume(Long id, String token) {
        return webClient.get()
                .uri("/resumes/" + id)
                .header("Authorization", "Bearer " + token)
                .retrieve()
                .bodyToMono(ResumeDto.class)
                .block();
    }

    public ResumeDto uploadResume(String title, MultipartFile file, String token) {
        MultipartBodyBuilder builder = new MultipartBodyBuilder();
        builder.part("title", title);
        try {
            builder.part("file", file.getResource());
        } catch (Exception e) {
            throw new RuntimeException("Failed to read file for upload", e);
        }

        System.out.println("Authorization Header being sent: " + "Bearer " + token); // Debugging line

        return webClient.post()
                .uri("/resumes/")
                .header("Authorization", "Bearer " + token)
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(BodyInserters.fromMultipartData(builder.build()))
                .retrieve()
                .bodyToMono(ResumeDto.class)
                .block();
    }
}
