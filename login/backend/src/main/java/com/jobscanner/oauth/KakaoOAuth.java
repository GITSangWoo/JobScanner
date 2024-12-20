package com.jobscanner.oauth;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.json.JSONObject;
import org.springframework.stereotype.Service;
import com.jobscanner.dto.SocialLoginDto;

@Service
public class KakaoOAuth {

    private static final String KAKAO_API_URL = "https://kapi.kakao.com/v2/user/me";

    @Value("${spring.security.oauth2.client.registration.kakao.clientId}")
    private String clientId;

    @Value("${spring.security.oauth2.client.registration.kakao.clientSecret}")
    private String clientSecret;

    @Value("${spring.security.oauth2.client.registration.kakao.redirectUri}")
    private String redirectUri;

    // 카카오 액세스 토큰을 사용해 사용자 정보를 가져오는 메서드
    public SocialLoginDto getUserInfo(String accessToken) {
        RestTemplate restTemplate = new RestTemplate();
        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", "Bearer " + accessToken);
        HttpEntity<String> entity = new HttpEntity<>(headers);
        ResponseEntity<String> response = restTemplate.exchange(KAKAO_API_URL, HttpMethod.GET, entity, String.class);

        String responseBody = response.getBody();
        JSONObject jsonResponse = new JSONObject(responseBody);

        SocialLoginDto userDto = new SocialLoginDto();
        
        // 카카오 로그인 API 응답 처리
        userDto.setId(jsonResponse.getString("id"));
        
        // properties를 JSONObject로 가져온 후 닉네임과 프로필 이미지 URL 추출
        JSONObject properties = jsonResponse.getJSONObject("properties");
        userDto.setNickname(properties.getString("nickname"));
        userDto.setProfileImageUrl(properties.getString("profile_image"));

        return userDto;
    }

    // 카카오 로그인 후 액세스 토큰을 요청하는 메서드
    public String getAccessToken(String code) {
        String tokenUrl = "https://kauth.kakao.com/oauth/token";

        MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
        params.add("grant_type", "authorization_code");
        params.add("client_id", clientId);
        params.add("redirect_uri", redirectUri);
        params.add("code", code);
        params.add("client_secret", clientSecret);

        RestTemplate restTemplate = new RestTemplate();
        HttpEntity<MultiValueMap<String, String>> entity = new HttpEntity<>(params);
        ResponseEntity<String> response = restTemplate.exchange(tokenUrl, HttpMethod.POST, entity, String.class);

        String responseBody = response.getBody();
        JSONObject jsonResponse = new JSONObject(responseBody);
        return jsonResponse.getString("access_token"); // 액세스 토큰 반환
    }
}
