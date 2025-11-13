package com.example.Interview.api;

import com.example.Interview.dto.ResumeDto;
import com.example.Interview.service.ResumeService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequestMapping("/api/resumes")
public class ResumeApiController {

    private final ResumeService resumeService;

    public ResumeApiController(ResumeService resumeService) {
        this.resumeService = resumeService;
    }

    @GetMapping
    public ResponseEntity<List<ResumeDto>> getResumes(@RequestHeader("Authorization") String authHeader) {
        String token = authHeader.replace("Bearer ", "");
        return ResponseEntity.ok(resumeService.getResumes(token));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ResumeDto> getResume(@PathVariable Long id, @RequestHeader("Authorization") String authHeader) {
        String token = authHeader.replace("Bearer ", "");
        return ResponseEntity.ok(resumeService.getResume(id, token));
    }

    @PostMapping
    public ResponseEntity<ResumeDto> uploadResume(@RequestParam("title") String title,
                                                  @RequestParam("file") MultipartFile file,
                                                  @RequestHeader("Authorization") String authHeader) {
        String token = authHeader.replace("Bearer ", "");
        return ResponseEntity.ok(resumeService.uploadResume(title, file, token));
    }
}
