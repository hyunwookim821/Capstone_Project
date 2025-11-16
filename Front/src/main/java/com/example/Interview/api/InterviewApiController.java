package com.example.Interview.api;

import com.example.Interview.dto.AnalysisDto;
import com.example.Interview.dto.InterviewSessionDto;
import com.example.Interview.service.InterviewService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/interviews")
public class InterviewApiController {

    private final InterviewService interviewService;

    public InterviewApiController(InterviewService interviewService) {
        this.interviewService = interviewService;
    }

    @PostMapping
    public Mono<ResponseEntity<InterviewSessionDto>> createInterviewSession(@RequestParam("resume_id") Long resumeId,
                                                                            @RequestHeader("Authorization") String authHeader) {
        String token = authHeader.replace("Bearer ", "");
        return interviewService.createInterviewSession(resumeId, token)
                .map(ResponseEntity::ok)
                .defaultIfEmpty(ResponseEntity.notFound().build());
    }

    @GetMapping("/{interviewId}/results")
    public Mono<ResponseEntity<AnalysisDto>> getInterviewResults(@PathVariable Long interviewId,
                                                                 @RequestHeader("Authorization") String authHeader) {
        String token = authHeader.replace("Bearer ", "");
        return interviewService.getInterviewResults(interviewId, token)
                .map(ResponseEntity::ok)
                .defaultIfEmpty(ResponseEntity.notFound().build());
    }

    @PostMapping("/{interviewId}/video-analysis")
    public Mono<ResponseEntity<Void>> sendVideoAnalysisData(@PathVariable Long interviewId,
                                                               @RequestBody List<Map<String, Object>> landmarkData,
                                                               @RequestHeader("Authorization") String authHeader) {
        String token = authHeader.replace("Bearer ", "");
        return interviewService.sendVideoAnalysisData(interviewId, landmarkData, token)
                .then(Mono.just(ResponseEntity.ok().<Void>build()))
                .defaultIfEmpty(ResponseEntity.badRequest().build());
    }
}
