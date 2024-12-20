package com.jobscanner.security;

import lombok.RequiredArgsConstructor;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import com.jobscanner.service.OAuthService;

@Configuration
@RequiredArgsConstructor
public class SecurityConfig {

    private final OAuthService oAuthService; // final 필드를 생성자 주입으로 초기화

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .cors()
            .and()
            .csrf().disable()
            .headers().frameOptions().disable()
            .and()
            .logout().logoutSuccessUrl("/")
            .and()
            .oauth2Login()
            .defaultSuccessUrl("http://localhost:3000/oauth/callback", true)
            .userInfoEndpoint()
            .userService(oAuthService); // OAuth2 로그인 후 사용자 정보 처리
        return http.build();
    }
}
