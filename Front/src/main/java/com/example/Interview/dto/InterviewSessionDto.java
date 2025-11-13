package com.example.Interview.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class InterviewSessionDto {

    @JsonProperty("interview_id")
    private int interviewId;
    private List<String> questions;

    // Getters and Setters
    public int getInterviewId() {
        return interviewId;
    }

    public void setInterviewId(int interviewId) {
        this.interviewId = interviewId;
    }

    public List<String> getQuestions() {
        return questions;
    }

    public void setQuestions(List<String> questions) {
        this.questions = questions;
    }
}
