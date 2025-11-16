package com.example.Interview.dto;

import lombok.Data;

@Data
public class DocumentAnalysisResultDto {
    private String originalText;
    private String correctedText;
    // 향후 맞춤법 오류 목록 등 추가될 수 있음
}
