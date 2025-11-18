package com.example.Interview.dto.feedback;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class AIFeedbackDto {
    @JsonProperty("content")
    private String originalContent;

    @JsonProperty("corrected_content")
    private String correctedSentence;

    @JsonProperty("ai_feedback")
    private String feedback;
}
