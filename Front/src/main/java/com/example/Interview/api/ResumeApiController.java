package com.example.Interview.api;

import com.example.Interview.dto.ResumeDto;
import com.example.Interview.dto.feedback.ResumeDetailDto;
import com.example.Interview.service.ResumeService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import reactor.core.publisher.Mono;

import java.util.List;

@RestController
@RequestMapping("/api/resumes")
@RequiredArgsConstructor
public class ResumeApiController {

    private final ResumeService resumeService;

    @GetMapping
    public Mono<ResponseEntity<List<ResumeDto>>> getResumes(HttpSession session) {
        String token = (String) session.getAttribute("token");
        return resumeService.getResumes(token)
                .map(ResponseEntity::ok);
    }

    @GetMapping("/{id}")
    public Mono<ResponseEntity<ResumeDetailDto>> getResume(@PathVariable Long id, HttpSession session) {
        String token = (String) session.getAttribute("token");
        return resumeService.getResume(id, token)
                .map(ResponseEntity::ok);
    }

    @PostMapping
    public Mono<ResponseEntity<ResumeDto>> uploadResume(@RequestParam("title") String title,
                                                        @RequestParam("file") MultipartFile file,
                                                        HttpSession session) {
        String token = (String) session.getAttribute("token");
        return resumeService.createResume(token, file)
                .map(ResponseEntity::ok);
    }

    @DeleteMapping("/{id}")
    public Mono<ResponseEntity<Void>> deleteResume(@PathVariable Long id, HttpSession session) {
        String token = (String) session.getAttribute("token");
        return resumeService.deleteResume(id, token)
                .map(ResponseEntity::ok);
    }
}
