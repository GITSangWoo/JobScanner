package com.team2.jobscanner.controller;

import com.team2.jobscanner.dto.KakaoTokenDTO;
import com.team2.jobscanner.entity.User;
import com.team2.jobscanner.service.UserService;
import org.slf4j.LoggerFactory;
import org.slf4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;



@CrossOrigin(origins = "http://43.202.186.119/8973")
@RequestMapping("/login")
@RestController
public class OAuthController {
    private static final Logger logger = LoggerFactory.getLogger(OAuthController.class);

    @Autowired
    private UserService userService;


    @PostMapping("/kakao")
    public ResponseEntity<String> kakaologin(@RequestBody KakaoTokenDTO kakaoTokenDTO) {
        // 카카오 로그인에서 받은 액세스 토큰과 리프레시 토큰
        String accessToken = kakaoTokenDTO.getAccessToken();
        String refreshToken = kakaoTokenDTO.getRefreshToken();

        try {
            // 카카오 API를 통해 사용자 정보를 받아오는 서비스 호출 (액세스 토큰 사용)
            User user = userService.getUserInfoFromKakao(accessToken);

            if (user == null) {
                // 유저 정보가 없으면 새로 등록
                user = userService.createUserFromKakao(accessToken);
            } else {
                // 기존 유저 정보가 있으면 이메일, 이름 등을 갱신
                userService.updateUserFromKakao(user, accessToken);
            }

            // 리프레시 토큰을 Auth 테이블에 저장
            userService.saveAuthToken(user, refreshToken);

            // 성공 응답 반환
            return ResponseEntity.ok("로그인 성공");
        } catch (Exception e) {
            logger.error("카카오 로그인 오류: ", e);
            return ResponseEntity.status(500).body("로그인 처리에 실패했습니다.");
        }
    }
}
