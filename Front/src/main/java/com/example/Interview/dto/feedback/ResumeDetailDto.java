package com.example.Interview.dto.feedback;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import java.util.List;

@Data
public class ResumeDetailDto {
    @JsonProperty("resume_id")
    private int resumeId;

    @JsonProperty("title")
    private String title;

    @JsonProperty("content")
    private String content;

    @JsonProperty("corrected_content")
    private String correctedContent;

    @JsonProperty("ai_feedback")
    private String aiFeedback;

    @JsonProperty("generated_questions")
    private List<GeneratedQuestionDto> generatedQuestions;
}
