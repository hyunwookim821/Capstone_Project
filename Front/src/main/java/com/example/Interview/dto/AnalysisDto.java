package com.example.Interview.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.LocalDateTime;

public class AnalysisDto {

    @JsonProperty("analysis_id")
    private int analysisId;

    @JsonProperty("interview_id")
    private int interviewId;

    @JsonProperty("resume_id")
    private Integer resumeId;  // 재면접을 위한 resume_id 추가

    @JsonProperty("feedback_text")
    private String feedbackText;

    @JsonProperty("speech_rate")
    private Float speechRate;

    @JsonProperty("silence_ratio")
    private Float silenceRatio;

    @JsonProperty("gaze_stability")
    private Float gazeStability;

    @JsonProperty("expression_stability")
    private Float expressionStability;

    @JsonProperty("posture_stability")
    private Float postureStability;

    @JsonProperty("created_at")
    private LocalDateTime createdAt;

    // Getters and Setters
    public int getAnalysisId() {
        return analysisId;
    }

    public void setAnalysisId(int analysisId) {
        this.analysisId = analysisId;
    }

    public int getInterviewId() {
        return interviewId;
    }

    public void setInterviewId(int interviewId) {
        this.interviewId = interviewId;
    }

    public Integer getResumeId() {
        return resumeId;
    }

    public void setResumeId(Integer resumeId) {
        this.resumeId = resumeId;
    }

    public String getFeedbackText() {
        return feedbackText;
    }

    public void setFeedbackText(String feedbackText) {
        this.feedbackText = feedbackText;
    }

    public Float getSpeechRate() {
        return speechRate;
    }

    public void setSpeechRate(Float speechRate) {
        this.speechRate = speechRate;
    }

    public Float getSilenceRatio() {
        return silenceRatio;
    }

    public void setSilenceRatio(Float silenceRatio) {
        this.silenceRatio = silenceRatio;
    }

    public Float getGazeStability() {
        return gazeStability;
    }

    public void setGazeStability(Float gazeStability) {
        this.gazeStability = gazeStability;
    }

    public Float getExpressionStability() {
        return expressionStability;
    }

    public void setExpressionStability(Float expressionStability) {
        this.expressionStability = expressionStability;
    }

    public Float getPostureStability() {
        return postureStability;
    }

    public void setPostureStability(Float postureStability) {
        this.postureStability = postureStability;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}
