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
public class NaverOAuth {

    private static final String NAVER_API_URL = "https://openapi.naver.com/v1/nid/me";

    @Value("${spring.security.oauth2.client.registration.naver.clientId}")
    private String clientId;

    @Value("${spring.security.oauth2.client.registration.naver.clientSecret}")
    private String clientSecret;

    @Value("${spring.security.oauth2.client.registration.naver.redirectUri}")
    private String redirectUri;

    public SocialLoginDto getUserInfo(String accessToken) {
        RestTemplate restTemplate = new RestTemplate();
        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", "Bearer " + accessToken);
        HttpEntity<String> entity = new HttpEntity<>(headers);
        ResponseEntity<String> apiResponse = restTemplate.exchange(NAVER_API_URL, HttpMethod.GET, entity, String.class);

        String responseBody = apiResponse.getBody();
        JSONObject jsonResponse = new JSONObject(responseBody);

        SocialLoginDto userDto = new SocialLoginDto();
        // 네이버 로그인 API 응답 처리
        JSONObject response = jsonResponse.getJSONObject("response"); // "response"가 JSONObject일 때
        userDto.setId(response.getString("id"));
        userDto.setNickname(response.getString("nickname"));
        userDto.setProfileImageUrl(response.getString("profile_image"));

        return userDto;
    }

    public String getAccessToken(String code, String state) {
        String tokenUrl = "https://nid.naver.com/oauth2.0/token";

        MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
        params.add("grant_type", "authorization_code");
        params.add("client_id", clientId);
        params.add("redirect_uri", redirectUri);
        params.add("code", code);
        params.add("state", state);
        params.add("client_secret", clientSecret);

        RestTemplate restTemplate = new RestTemplate();
        HttpEntity<MultiValueMap<String, String>> entity = new HttpEntity<>(params);
        ResponseEntity<String> tokenResponse = restTemplate.exchange(tokenUrl, HttpMethod.POST, entity, String.class);

        String responseBody = tokenResponse.getBody();
        JSONObject jsonResponse = new JSONObject(responseBody);
        return jsonResponse.getString("access_token");
    }
}
