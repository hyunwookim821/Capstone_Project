package com.example.Interview.dto.feedback;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class AIFeedbackDto {
    @JsonProperty("error_count")
    private int errorCount;

    @JsonProperty("corrected_sentence")
    private String correctedSentence;

    @JsonProperty("feedback")
    private String feedback;
}
