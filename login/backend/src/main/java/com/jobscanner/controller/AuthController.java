package com.jobscanner.controller;

import com.jobscanner.dto.SocialLoginDto;
import com.jobscanner.service.AuthService;
import com.jobscanner.service.SocialLoginService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final SocialLoginService socialLoginService;
    private final AuthService authService;

    // 카카오 로그인 처리
    @GetMapping("/login/kakao")
    public ResponseEntity<String> kakaoLogin(@RequestParam String code) {
        try {
            // 카카오 로그인 후 JWT 토큰 발급
            String token = socialLoginService.handleKakaoLogin(code);
            return ResponseEntity.ok(token); // JWT 토큰 반환
        } catch (Exception e) {
            return ResponseEntity.status(500).body("카카오 로그인 실패: " + e.getMessage());
        }
    }

    // 네이버 로그인 처리
    @GetMapping("/login/naver")
    public ResponseEntity<String> naverLogin(@RequestParam String code, @RequestParam String state) {
        try {
            // 네이버 로그인 후 JWT 토큰 발급
            String token = socialLoginService.handleNaverLogin(code, state);
            return ResponseEntity.ok(token); // JWT 토큰 반환
        } catch (Exception e) {
            return ResponseEntity.status(500).body("네이버 로그인 실패: " + e.getMessage());
        }
    }

    // 구글 로그인 처리
    @GetMapping("/login/google")
    public ResponseEntity<String> googleLogin(@RequestParam String code) {
        try {
            // 구글 로그인 후 JWT 토큰 발급
            String token = socialLoginService.handleGoogleLogin(code);
            return ResponseEntity.ok(token); // JWT 토큰 반환
        } catch (Exception e) {
            return ResponseEntity.status(500).body("구글 로그인 실패: " + e.getMessage());
        }
    }

    // 카카오 회원가입 처리
    @PostMapping("/signup/kakao")
    public ResponseEntity<String> kakaoSignup(@RequestBody SocialLoginDto kakaoDto) {
        try {
            // 카카오 회원가입 후 사용자 정보 DB 저장
            authService.handleKakaoSignup(kakaoDto);
            return ResponseEntity.status(201).body("User created with Kakao");
        } catch (Exception e) {
            return ResponseEntity.status(500).body("카카오 회원가입 실패: " + e.getMessage());
        }
    }

    // 네이버 회원가입 처리
    @PostMapping("/signup/naver")
    public ResponseEntity<String> naverSignup(@RequestBody SocialLoginDto naverDto) {
        try {
            // 네이버 회원가입 후 사용자 정보 DB 저장
            authService.handleNaverSignup(naverDto);
            return ResponseEntity.status(201).body("User created with Naver");
        } catch (Exception e) {
            return ResponseEntity.status(500).body("네이버 회원가입 실패: " + e.getMessage());
        }
    }

    // 구글 회원가입 처리
    @PostMapping("/signup/google")
    public ResponseEntity<String> googleSignup(@RequestBody SocialLoginDto googleDto) {
        try {
            // 구글 회원가입 후 사용자 정보 DB 저장
            authService.handleGoogleSignup(googleDto);
            return ResponseEntity.status(201).body("User created with Google");
        } catch (Exception e) {
            return ResponseEntity.status(500).body("구글 회원가입 실패: " + e.getMessage());
        }
    }
}
