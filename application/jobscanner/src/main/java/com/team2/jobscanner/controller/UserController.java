package com.team2.jobscanner.controller;

import com.team2.jobscanner.dto.UserDTO;
import com.team2.jobscanner.entity.User;
import com.team2.jobscanner.service.UserService;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/user")
public class UserController {

    private final UserService userService;

    // 생성자 주입 방식
    public UserController(UserService userService) {
        this.userService = userService;
    }

    // 프로필 정보 제공
    @GetMapping("/profile")
    public ResponseEntity<?> getProfile(@RequestHeader(value = HttpHeaders.AUTHORIZATION) String accessToken) {
        try {
            // 액세스 토큰을 해석하여 사용자 정보를 조회
            User user = userService.getUserInfoFromAccessToken(accessToken);

            if (user == null) {
                // 액세스 토큰이 만료되었으면 리프레시 토큰으로 새 액세스 토큰 발급
                String refreshToken = userService.getRefreshTokenByUserId(user.getId());
                String newAccessToken = userService.refreshAccessToken(refreshToken);

                if (newAccessToken != null) {
                    // 새 액세스 토큰을 응답에 포함시켜 전달
                    return ResponseEntity.ok(newAccessToken);
                } else {
                    // 리프레시 토큰도 만료되었으면 재로그인 요청
                    return ResponseEntity.status(401).body("Re-login required");
                }
            }

            // 유저 정보 반환
            UserDTO userDTO = userService.getUserProfile(user.getEmail());
            return ResponseEntity.ok(userDTO);
        } catch (Exception e) {
            // 액세스 토큰을 통한 사용자 정보 조회 실패
            return ResponseEntity.status(500).body("Internal Server Error");
        }
    }
}


