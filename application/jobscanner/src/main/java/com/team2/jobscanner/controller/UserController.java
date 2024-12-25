package com.team2.jobscanner.controller;

import com.team2.jobscanner.dto.UserDTO;
import com.team2.jobscanner.entity.User;
import com.team2.jobscanner.service.UserService;
import com.team2.jobscanner.util.JwtUtil;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/user")
public class UserController {

    private final UserService userService;
    private final JwtUtil jwtUtil;  // JwtUtil을 주입받습니다.

    // 생성자 주입 방식
    public UserController(UserService userService, JwtUtil jwtUtil) {
        this.userService = userService;
        this.jwtUtil = jwtUtil;
    }

    @GetMapping("/profile")
    public ResponseEntity<UserDTO> getProfile(@AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            return ResponseEntity.status(401).body(null);  // 인증되지 않은 사용자
        }

        try {
            // UserService를 사용하여 UserDTO를 반환
            User user = userService.findUserByEmail(userDetails.getUsername());
            if (user == null) {
                return ResponseEntity.status(404).body(null);  // 사용자 정보가 없을 때 404 응답
            }
            UserDTO userDTO = userService.getUserProfile(user.getEmail());
            return ResponseEntity.ok(userDTO);  // 인증된 사용자 정보를 UserDTO 형식으로 반환
        } catch (Exception e) {
            // 서버 오류 처리 (500 오류)
            return ResponseEntity.status(500).body(null);
        }
    }
}


