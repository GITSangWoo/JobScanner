package com.jobscanner.service;

import com.jobscanner.dto.SocialLoginDto;
import com.jobscanner.oauth.KakaoOAuth;
import com.jobscanner.oauth.NaverOAuth;
import com.jobscanner.oauth.GoogleOAuth;
import com.jobscanner.util.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class SocialLoginService {

    private final KakaoOAuth kakaoOAuth;
    private final NaverOAuth naverOAuth;
    private final GoogleOAuth googleOAuth;
    private final JwtTokenProvider jwtTokenProvider; // JwtTokenProvider를 통해 JWT 발급

    // 카카오 로그인 처리
    public String handleKakaoLogin(String code) {
        String accessToken = kakaoOAuth.getAccessToken(code); // 카카오 토큰 받기
        SocialLoginDto userDto = kakaoOAuth.getUserInfo(accessToken); // 사용자 정보 받기

        // JWT 토큰 생성 및 반환
        String token = jwtTokenProvider.generateToken(userDto.getId()); // JWT 토큰 생성
        return token; // 생성된 JWT 토큰 반환
    }

    // 네이버 로그인 처리
    public String handleNaverLogin(String code, String state) {
        String accessToken = naverOAuth.getAccessToken(code, state); // 네이버 토큰 받기
        SocialLoginDto userDto = naverOAuth.getUserInfo(accessToken); // 사용자 정보 받기

        // JWT 토큰 생성 및 반환
        String token = jwtTokenProvider.generateToken(userDto.getId()); // JWT 토큰 생성
        return token; // 생성된 JWT 토큰 반환
    }

    // 구글 로그인 처리
    public String handleGoogleLogin(String code) {
        String accessToken = googleOAuth.getAccessToken(code); // 구글 토큰 받기
        SocialLoginDto userDto = googleOAuth.getUserInfo(accessToken); // 사용자 정보 받기

        // JWT 토큰 생성 및 반환
        String token = jwtTokenProvider.generateToken(userDto.getId()); // JWT 토큰 생성
        return token; // 생성된 JWT 토큰 반환
    }
}
