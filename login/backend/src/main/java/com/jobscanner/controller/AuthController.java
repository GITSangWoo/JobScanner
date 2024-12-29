package com.jobscanner.controller;

import lombok.RequiredArgsConstructor;
import jakarta.servlet.http.HttpServletResponse;

import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.jobscanner.converter.UserConverter;
import com.jobscanner.domain.User;
import com.jobscanner.dto.UserRequestDTO;
import com.jobscanner.dto.UserResponseDTO;
import com.jobscanner.service.AuthService;
import com.jobscanner.util.BaseResponse;

import org.springframework.http.ResponseEntity;

@RestController
@RequiredArgsConstructor
@RequestMapping("")
@CrossOrigin(origins="http://localhost:3000", allowCredentials = "true")
public class AuthController {

    private final AuthService authService;

    @PostMapping("/login")
    public ResponseEntity<?> join(@RequestBody UserRequestDTO.LoginRequestDTO loginRequestDTO) {
        return null;
    }

    @GetMapping("/auth/login/kakao")
    public BaseResponse<UserResponseDTO.JoinResultDTO> kakaoLogin(@RequestParam("code") String accessCode, HttpServletResponse httpServletResponse) {
        User user = authService.oAuthLogin(accessCode, httpServletResponse);
        return BaseResponse.onSuccess(UserConverter.toJoinResultDTO(user));
    }
}


// // import com.jobscanner.dto.LoginResponseDto;
// import com.jobscanner.dto.SocialLoginDto;
// import com.jobscanner.service.AuthService;   
// import com.jobscanner.service.SocialLoginService;

// import jakarta.servlet.http.HttpServletRequest;
// import lombok.RequiredArgsConstructor;
// import org.springframework.http.ResponseEntity;
// import org.springframework.web.bind.annotation.*;

// @RestController
// @RequestMapping("/auth")
// @RequiredArgsConstructor
// public class AuthController {

//     private final SocialLoginService socialLoginService;
//     private final AuthService authService;

//     // 카카오 로그인 처리
//     @GetMapping("/login/kakao")
//     public ResponseEntity<String> kakaoLogin(@RequestParam String code) {
//         try {
//             String token = socialLoginService.handleKakaoLogin(code);
//             return ResponseEntity.ok(token); // JWT 토큰 반환
//         } catch (Exception e) {
//             return ResponseEntity.status(500).body("카카오 로그인 실패: " + e.getMessage());
//         }
//     }

//     // // 네이버 로그인 처리
//     // @GetMapping("/login/naver")
//     // public ResponseEntity<String> naverLogin(@RequestParam String code, @RequestParam String state) {
//     //     try {
//     //         String token = socialLoginService.handleNaverLogin(code, state);
//     //         return ResponseEntity.ok(token); // JWT 토큰 반환
//     //     } catch (Exception e) {
//     //         return ResponseEntity.status(500).body("네이버 로그인 실패: " + e.getMessage());
//     //     }
//     // }

//     // 구글 로그인 처리
//     @GetMapping("/login/google")
//     public ResponseEntity<String> googleLogin(@RequestParam String code) {
//         try {
//             String token = socialLoginService.handleGoogleLogin(code);
//             return ResponseEntity.ok(token); // JWT 토큰 반환
//         } catch (Exception e) {
//             return ResponseEntity.status(500).body("구글 로그인 실패: " + e.getMessage());
//         }
//     }

//     // 카카오 회원가입 처리
//     @PostMapping("/signup/kakao")
//     public ResponseEntity<String> kakaoSignup(@RequestBody SocialLoginDto kakaoDto) {
//         try {
//             authService.handleKakaoSignup(kakaoDto);
//             return ResponseEntity.status(201).body("User created with Kakao");
//         } catch (Exception e) {
//             return ResponseEntity.status(500).body("카카오 회원가입 실패: " + e.getMessage());
//         }
//     }

//     // // 네이버 회원가입 처리
//     // @PostMapping("/signup/naver")
//     // public ResponseEntity<String> naverSignup(@RequestBody SocialLoginDto naverDto) {
//     //     try {
//     //         authService.handleNaverSignup(naverDto);
//     //         return ResponseEntity.status(201).body("User created with Naver");
//     //     } catch (Exception e) {
//     //         return ResponseEntity.status(500).body("네이버 회원가입 실패: " + e.getMessage());
//     //     }
//     // }

//     // 구글 회원가입 처리
//     @PostMapping("/signup/google")
//     public ResponseEntity<String> googleSignup(@RequestBody SocialLoginDto googleDto) {
//         try {
//             authService.handleGoogleSignup(googleDto);
//             return ResponseEntity.status(201).body("User created with Google");
//         } catch (Exception e) {
//             return ResponseEntity.status(500).body("구글 회원가입 실패: " + e.getMessage());
//         }
//     }
// }

// // @RestController
// // @RequestMapping("/auth/login")
// // public class AuthController {

// //     private final AuthService authService;

// //     public AuthController(AuthService authService) {
// //         this.authService = authService;
// //     }

// //     @GetMapping("/kakao")
// //     public ResponseEntity<LoginResponseDto> kakaoLogin(HttpServletRequest request) {
// //         // 1. 클라이언트에서 전달된 "code" 파라미터 추출
// //         String code = request.getParameter("code");

// //         // 2. code로 Access Token을 얻음
// //         String kakaoAccessToken = authService.getKakaoAccessToken(code);

// //         // 3. Access Token으로 카카오 사용자 정보를 가져오고, 로그인 처리
// //         return authService.kakaoLogin(kakaoAccessToken);
// //     }
// // }
