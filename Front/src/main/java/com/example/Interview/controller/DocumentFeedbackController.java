package com.example.Interview.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/document-feedback")
public class DocumentFeedbackController {

    @GetMapping
    public String showDocumentFeedbackPage() {
        return "document-feedback/document-feedback";
    }
}
