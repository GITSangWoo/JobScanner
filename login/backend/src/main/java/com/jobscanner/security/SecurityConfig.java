package com.jobscanner.security;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .cors().configurationSource(corsConfigurationSource()) // CORS 설정 추가
            .and()
            .csrf(csrf -> csrf.disable()) // CSRF 비활성화
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/login/oauth2/**", "/", "/details/**", "/job-summary").permitAll() // 특정 경로 허용
                .requestMatchers(HttpMethod.OPTIONS, "/auth/login/**").permitAll() // OPTIONS 요청을 리다이렉트 처리하지 않도록 허용
                .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll() // 모든 OPTIONS 요청을 허용
                .anyRequest().authenticated() // 나머지 경로는 인증 필요
            )
            .oauth2Login(oauth2 -> oauth2
                .authorizationEndpoint(authorization ->
                    authorization.baseUri("/login/oauth2/authorization")
                )
                .redirectionEndpoint(redirection ->
                    redirection.baseUri("/oauth2/callback")
                )
                .defaultSuccessUrl("http://localhost:3000/oauth/callback", true)
                .failureUrl("http://localhost:3000/login?error=true")
            )
            .formLogin().disable()
            .httpBasic().disable();

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowCredentials(true); // 인증 정보 허용
        config.addAllowedOrigin("http://localhost:3000"); // React 프론트엔드 URL
        config.addAllowedHeader("*"); // 모든 헤더 허용
        config.addAllowedMethod("*"); // 모든 HTTP 메서드 허용
        config.addExposedHeader("Authorization"); // 클라이언트에서 Authorization 헤더 접근 허용

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);

        return source;
    }
}
