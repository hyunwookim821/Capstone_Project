package com.example.Interview.dto.feedback;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class GeneratedQuestionDto {
    @JsonProperty("question_id")
    private int questionId;

    @JsonProperty("resume_id")
    private int resumeId;

    @JsonProperty("question_text")
    private String questionText;
}
