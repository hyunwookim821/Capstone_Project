package com.example.Interview.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/interview-practice")
public class InterviewPracticeController {

    @GetMapping
    public String showInterviewPracticePage() {
        return "interview-practice/interview-practice";
    }
}
