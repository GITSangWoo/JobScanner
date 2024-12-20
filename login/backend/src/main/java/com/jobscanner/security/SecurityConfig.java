package com.jobscanner.security;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    public SecurityConfig(JwtAuthenticationFilter jwtAuthenticationFilter) {
        this.jwtAuthenticationFilter = jwtAuthenticationFilter;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http.csrf(csrf -> csrf.disable()) // CSRF 비활성화
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/login/oauth2/**", "/", "/details/**", "/job-summary").permitAll() // 특정 경로 허용
                .anyRequest().authenticated() // 나머지 경로는 인증 필요
            )
            .oauth2Login(oauth2 -> oauth2
                .authorizationEndpoint(authorization -> 
                    authorization.baseUri("/login/oauth2/authorization") // OAuth2 요청 URI
                )
                .redirectionEndpoint(redirection -> 
                    redirection.baseUri("/oauth2/callback") // OAuth2 콜백 URI
                )
                .defaultSuccessUrl("http://localhost:3000/oauth/callback", true) // 성공 시 React로 리다이렉트
                .failureUrl("http://localhost:3000/login?error=true") // 실패 시 React로 리다이렉트
            )
            .formLogin().disable() // 기본 로그인 폼 비활성화
            .httpBasic().disable() // HTTP Basic 인증 비활성화
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class); // JWT 필터 추가

        return http.build();
    }
}
