package com.example.Interview.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.time.LocalDate; // For birthdate

@Data
public class UserDto {
    @JsonProperty("user_id")
    private int userId;
    @JsonProperty("email")
    private String email;
    @JsonProperty("user_name")
    private String userName;
    @JsonProperty("phone")
    private String phone;
    @JsonProperty("birthdate")
    private LocalDate birthdate; // Use LocalDate for date type
    @JsonProperty("desired_position")
    private String desiredPosition;
    @JsonProperty("desired_industry")
    private String desiredIndustry;
    @JsonProperty("career_years")
    private String careerYears;
    @JsonProperty("career_description")
    private String careerDescription;
    @JsonProperty("education")
    private String education;
    @JsonProperty("major")
    private String major;
    @JsonProperty("skills")
    private String skills;
    @JsonProperty("introduction")
    private String introduction;
    @JsonProperty("interview_goal")
    private String interviewGoal;
}
