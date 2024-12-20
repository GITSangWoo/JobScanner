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
public class GoogleOAuth {

    private static final String GOOGLE_API_URL = "https://www.googleapis.com/oauth2/v3/userinfo";

    @Value("${spring.security.oauth2.client.registration.google.clientId}")
    private String clientId;

    @Value("${spring.security.oauth2.client.registration.google.clientSecret}")
    private String clientSecret;

    @Value("${spring.security.oauth2.client.registration.google.redirectUri}")
    private String redirectUri;

    public SocialLoginDto getUserInfo(String accessToken) {
        RestTemplate restTemplate = new RestTemplate();
        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", "Bearer " + accessToken);
        HttpEntity<String> entity = new HttpEntity<>(headers);
        ResponseEntity<String> response = restTemplate.exchange(GOOGLE_API_URL, HttpMethod.GET, entity, String.class);

        String responseBody = response.getBody();
        JSONObject jsonResponse = new JSONObject(responseBody);

        SocialLoginDto userDto = new SocialLoginDto();
        userDto.setId(jsonResponse.getString("sub"));
        userDto.setNickname(jsonResponse.getString("name"));
        userDto.setProfileImageUrl(jsonResponse.getString("picture"));

        return userDto;
    }

    public String getAccessToken(String code) {
        String tokenUrl = "https://oauth2.googleapis.com/token";
//        String clientId = "your-client-id";
//        String redirectUri = "your-redirect-uri";
//        String clientSecret = "your-client-secret";

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
        return jsonResponse.getString("access_token");
    }
}
