package com.jobscanner.util;

import org.springframework.beans.factory.annotation.Value; // @Value 어노테이션
import org.springframework.stereotype.Component; // @Component 어노테이션
import org.springframework.util.LinkedMultiValueMap; // LinkedMultiValueMap
import org.springframework.util.MultiValueMap; // MultiValueMap
import org.springframework.web.client.RestTemplate; // RestTemplate

import org.springframework.http.HttpEntity; // HTTP 요청
import org.springframework.http.HttpHeaders; // HTTP Header
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity; // HTTP 응답

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.jobscanner.dto.KakaoDTO; // KakaoDTO 클래스
import java.util.Arrays; // Arrays 임포트
import lombok.extern.slf4j.Slf4j; // @Slf4j 어노테이션


@Component
@Slf4j
public class KakaoUtil {

    @Value("${spring.security.oauth2.client.registration.kakao.client-id}")
    private String client;
    @Value("${spring.security.oauth2.client.registration.kakao.redirect-uri}")
    private String redirect;

    public KakaoDTO.OAuthToken requestToken(String accessCode) {
        RestTemplate restTemplate = new RestTemplate();
        HttpHeaders headers = new HttpHeaders();
        headers.add("Content-type", "application/x-www-form-urlencoded;charset=utf-8");

        MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
        params.add("grant_type", "authorization_code");
        params.add("client_id", client);
        params.add("redirect_url", redirect);
        params.add("code", accessCode);

        HttpEntity<MultiValueMap<String, String>> kakaoTokenRequest = new HttpEntity<>(params, headers);

        ResponseEntity<String> response = restTemplate.exchange(
                "https://kauth.kakao.com/oauth/token",
                HttpMethod.POST,
                kakaoTokenRequest,
                String.class);

        ObjectMapper objectMapper = new ObjectMapper();

        KakaoDTO.OAuthToken oAuthToken = null;

        try {
            oAuthToken = objectMapper.readValue(response.getBody(), KakaoDTO.OAuthToken.class);
            log.info("oAuthToken : " + oAuthToken.getAccess_token());
        } catch (JsonProcessingException e) {
            log.error("Error occurred while parsing the OAuthToken response.", e); // 에러를 로그로만 출력
        }
        return oAuthToken;
    }

    public KakaoDTO.KakaoProfile requestProfile(KakaoDTO.OAuthToken oAuthToken){
        RestTemplate restTemplate2 = new RestTemplate();
        HttpHeaders headers2 = new HttpHeaders();

        headers2.add("Content-type", "application/x-www-form-urlencoded;charset=utf-8");
        headers2.add("Authorization","Bearer "+ oAuthToken.getAccess_token());

        HttpEntity<MultiValueMap<String,String>> kakaoProfileRequest = new HttpEntity <>(headers2);

        ResponseEntity<String> response2 = restTemplate2.exchange(
                "https://kapi.kakao.com/v2/user/me",
                HttpMethod.GET,
                kakaoProfileRequest,
                String.class);

        ObjectMapper objectMapper = new ObjectMapper();

        KakaoDTO.KakaoProfile kakaoProfile = null;

        try {
            kakaoProfile = objectMapper.readValue(response2.getBody(), KakaoDTO.KakaoProfile.class);
        } catch (JsonProcessingException e) {
            log.error("Error occurred while parsing the KakaoProfile response.", e); // 에러를 로그로만 출력
        }

        return kakaoProfile;
    }
}
