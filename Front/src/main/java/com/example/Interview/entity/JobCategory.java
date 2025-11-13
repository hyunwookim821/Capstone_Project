package com.example.Interview.entity;

public enum JobCategory {
    IT, MARKETING, SALES, FINANCE, HR, CONSULTING, DESIGN, OTHER;

    public static JobCategory fromFormValue(String v) {
        if (v == null || v.isBlank()) return null;
        return switch (v.toLowerCase()) {
            case "it" -> IT;
            case "marketing" -> MARKETING;
            case "sales" -> SALES;
            case "finance" -> FINANCE;
            case "hr" -> HR;
            case "consulting" -> CONSULTING;
            case "design" -> MARKETING;
            default -> OTHER;
        };
    }
}
