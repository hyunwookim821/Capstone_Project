package com.example.Interview.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.util.List;

@Data
public class InterviewHistoryDto {
    @JsonProperty("interview_id")
    private Long interviewId;

    @JsonProperty("resume_title")
    private String resumeTitle;

    @JsonProperty("created_at")
    private String createdAt;

    @JsonProperty("qa_list")
    private List<QADto> qaList;

    @JsonProperty("has_feedback")
    private Boolean hasFeedback;

    @Data
    public static class QADto {
        @JsonProperty("question_text")
        private String questionText;

        @JsonProperty("answer_text")
        private String answerText;
    }
}