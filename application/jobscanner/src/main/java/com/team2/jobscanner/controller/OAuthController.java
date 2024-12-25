package com.team2.jobscanner.controller;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.team2.jobscanner.dto.KakaoTokenDTO;
import com.team2.jobscanner.dto.LoginRequestDTO;
import com.team2.jobscanner.entity.User;
import com.team2.jobscanner.service.UserService;
import com.team2.jobscanner.util.JwtUtil;
import org.slf4j.LoggerFactory;
import org.slf4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;


@CrossOrigin(origins = "http://localhost:8972")
@RequestMapping("/auth")
@RestController
public class OAuthController {
    private static final Logger logger = LoggerFactory.getLogger(OAuthController.class);

    @Autowired
    private UserService userService;

    @Autowired
    private JwtUtil jwtUtil;

    @PostMapping("/kakao")
    public ResponseEntity<String> kakaoLogin(@RequestBody KakaoTokenDTO kakaoTokenDTO) {
        // 카카오 API에 access token을 사용하여 사용자 정보 가져오기
        String accessToken = kakaoTokenDTO.getAccessToken();
        String url = "https://kapi.kakao.com/v2/user/me";
        RestTemplate restTemplate = new RestTemplate();

        // 카카오 API로 사용자 정보 요청
        String response = restTemplate.getForObject(url + "?access_token=" + accessToken, String.class);

        // 사용자 정보 파싱
        try {
            ObjectMapper objectMapper = new ObjectMapper();
            JsonNode jsonNode = objectMapper.readTree(response);
            String email = jsonNode.path("kakao_account").path("email").asText();
            String name = jsonNode.path("properties").path("nickname").asText();

            // 사용자 등록 또는 로그인 처리
            User user = userService.findOrCreateUser("kakao",email, name);

            // JWT 토큰 생성
            String jwtToken = jwtUtil.createToken(user.getEmail());

            // JWT 토큰 반환
            return ResponseEntity.ok(jwtToken);
        } catch (Exception e) {
            logger.error("카카오 로그인 처리 중 오류 발생: {}", e.getMessage(), e);
            return ResponseEntity.status(500).body("카카오 로그인 오류");
        }
    }

    // 수정된 로그인 메서드
    @PostMapping("/login")
    public ResponseEntity<Map<String,String>> login(@RequestBody LoginRequestDTO loginRequestDTO) {
        try {
            // 클라이언트에서 보내는 email, name, oauthProvider를 LoginRequest로 받음
            String oauthProvider = loginRequestDTO.getOauthProvider();
            String email = loginRequestDTO.getEmail();
            String name = loginRequestDTO.getName();

            // 이메일로 사용자 조회 (새로 생성하지 않고)
            userService.findUserByEmail(email);  // 기존 사용자가 있는지 확인
            // 이메일로 사용자 조회 (새로 생성하지 않고)
            User user = userService.findUserByEmail(email);
            // JWT 토큰 생성
            String jwtToken = jwtUtil.createToken(user.getEmail());

            Map<String, String> response = new HashMap<>();
            response.put("token", jwtToken);
            System.out.println("Generated JWT Token: " + jwtToken);
            // JWT 토큰 반환
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            // 예외 발생 시 로깅
            logger.error("로그인 처리 중 오류 발생: {}", e.getMessage(), e);
            return ResponseEntity.status(500).body(Collections.singletonMap("error", "로그인 처리 오류"));
        }
    }
}
