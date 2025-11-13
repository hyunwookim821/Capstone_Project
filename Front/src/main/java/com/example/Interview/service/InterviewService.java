package com.example.Interview.service;

import com.example.Interview.dto.InterviewSessionDto;
import com.example.Interview.dto.AnalysisDto;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import org.springframework.http.MediaType;

import java.util.List;
import java.util.Map;

@Service
public class InterviewService {

    private final WebClient webClient;

    public InterviewService(WebClient webClient) {
        this.webClient = webClient;
    }

    public InterviewSessionDto createInterviewSession(Long resumeId, String token) {
        return webClient.post()
                .uri(uriBuilder -> uriBuilder.path("/interviews/").queryParam("resume_id", resumeId).build())
                .header("Authorization", "Bearer " + token)
                .retrieve()
                .bodyToMono(InterviewSessionDto.class)
                .block();
    }

    public AnalysisDto getInterviewResults(Long interviewId, String token) {
        return webClient.get()
                .uri("/interviews/" + interviewId + "/results")
                .header("Authorization", "Bearer " + token)
                .retrieve()
                .bodyToMono(AnalysisDto.class)
                .block();
    }

    public String sendVideoAnalysisData(Long interviewId, List<Map<String, Object>> landmarkData, String token) {
        // Wrap the list in a map to match the VideoAnalysisRequest Pydantic model
        Map<String, Object> body = Map.of("landmarks", landmarkData);

        return webClient.post()
                .uri("/interviews/" + interviewId + "/video-analysis")
                .header("Authorization", "Bearer " + token)
                .contentType(MediaType.APPLICATION_JSON)
                .body(Mono.just(body), Map.class) // Send the map
                .retrieve()
                .bodyToMono(String.class) // Assuming a simple message response
                .block();
    }
}
