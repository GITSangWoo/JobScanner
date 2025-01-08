package com.team2.jobscanner.dto;

import lombok.Getter;


@Getter
public class KakaoTokenDTO {
    private String accessToken;
    private String refreshToken;  // 리프레시 토큰 추가

    public KakaoTokenDTO(String accessToken, String refreshToken) {
        this.accessToken = accessToken;
        this.refreshToken = refreshToken;
    }
}
