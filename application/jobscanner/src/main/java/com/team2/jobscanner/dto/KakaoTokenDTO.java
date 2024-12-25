package com.team2.jobscanner.dto;

import lombok.Getter;

@Getter
public class KakaoTokenDTO {
    private String accessToken;

    // Getters and Setters
    public String getAccessToken() {
        return accessToken;
    }

    public void setAccessToken(String accessToken) {
        this.accessToken = accessToken;
    }
}