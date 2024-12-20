package com.jobscanner.security;

// import org.springframework.context.annotation.Bean;
// import org.springframework.context.annotation.Configuration;
// import org.springframework.http.HttpMethod;
// import org.springframework.security.config.annotation.web.builders.HttpSecurity;
// import org.springframework.security.web.SecurityFilterChain;
// import org.springframework.web.cors.CorsConfiguration;
// import org.springframework.web.cors.CorsConfigurationSource;
// import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
// import org.springframework.web.cors.CorsUtils;

// @Configuration
// public class SecurityConfig {

//     @Bean
//     public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
//         http
//             .cors().configurationSource(corsConfigurationSource()) // CORS 설정 추가
//             .and()
//             .csrf(csrf -> csrf.disable()) // CSRF 비활성화
//             .authorizeHttpRequests(auth -> auth
//                 .requestMatchers("/login/oauth2/**", "/", "/details/**", "/job-summary").permitAll() // 특정 경로 허용
//                 .requestMatchers(HttpMethod.OPTIONS, "/auth/login/**").permitAll() // OPTIONS 요청을 허용
//                 .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll() // 모든 OPTIONS 요청을 허용
//                 .anyRequest().authenticated() // 나머지 경로는 인증 필요
//             )
//             .oauth2Login(oauth2 -> oauth2
//                 .authorizationEndpoint(authorization -> authorization.baseUri("/login/oauth2/authorization"))
//                 .redirectionEndpoint(redirection -> redirection.baseUri("/oauth2/callback"))
//                 .defaultSuccessUrl("https://localhost:8443/oauth/callback", true)
//                 .failureUrl("https://localhost:8443/login?error=true")
//             )
//             .formLogin().disable()
//             .httpBasic().disable();
    
//         return http.build();
//     }

//     @Bean
//     public CorsConfigurationSource corsConfigurationSource() {
//         CorsConfiguration config = new CorsConfiguration();
//         config.setAllowCredentials(true); // 인증 정보 허용
//         config.addAllowedOrigin("https://localhost:8443"); // React 프론트엔드 URL
//         config.addAllowedHeader("*"); // 모든 헤더 허용
//         config.addAllowedMethod("*"); // 모든 HTTP 메서드 허용
//         config.addExposedHeader("Authorization"); // 클라이언트에서 Authorization 헤더 접근 허용

//         UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
//         source.registerCorsConfiguration("/**", config);

//         return source;
//     }
// }

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests()
                .requestMatchers("/static/**", "/login-test.html", "/favicon.ico", "/default-ui.css").permitAll() // 정적 리소스 허용
                .anyRequest().authenticated() // 나머지 요청은 인증 필요
            .and()
            .formLogin()
                .loginPage("/login") // 로그인 페이지 설정
                .permitAll()
            .and()
            .logout()
                .permitAll();

        return http.build();
    }
}
