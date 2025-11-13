package com.example.Interview.api;

import com.example.Interview.dto.InterviewSessionDto;
import com.example.Interview.dto.AnalysisDto;
import com.example.Interview.service.InterviewService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

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
    public ResponseEntity<InterviewSessionDto> createInterviewSession(@RequestParam("resume_id") Long resumeId,
                                                                      @RequestHeader("Authorization") String authHeader) {
        String token = authHeader.replace("Bearer ", "");
        return ResponseEntity.ok(interviewService.createInterviewSession(resumeId, token));
    }

    @GetMapping("/{interviewId}/results")
    public ResponseEntity<AnalysisDto> getInterviewResults(@PathVariable Long interviewId,
                                                           @RequestHeader("Authorization") String authHeader) {
        String token = authHeader.replace("Bearer ", "");
        return ResponseEntity.ok(interviewService.getInterviewResults(interviewId, token));
    }

    @PostMapping("/{interviewId}/video-analysis")
    public ResponseEntity<String> sendVideoAnalysisData(@PathVariable Long interviewId,
                                                        @RequestBody List<Map<String, Object>> landmarkData,
                                                        @RequestHeader("Authorization") String authHeader) {
        String token = authHeader.replace("Bearer ", "");
        return ResponseEntity.ok(interviewService.sendVideoAnalysisData(interviewId, landmarkData, token));
    }
}
