// package com.jobscanner.security;

// import lombok.RequiredArgsConstructor;

// import org.springframework.context.annotation.Bean;
// import org.springframework.context.annotation.Configuration;
// import org.springframework.security.config.annotation.web.builders.HttpSecurity;
// import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
// import org.springframework.security.web.SecurityFilterChain;
// import com.jobscanner.service.OAuthService;

// @Configuration
// @RequiredArgsConstructor
// public class SecurityConfig {

//     private final OAuthService oAuthService; // final 필드를 생성자 주입으로 초기화

//     @Bean
//     public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
//         http
//             .cors()
//             .and()
//             .csrf().disable()
//             .headers().frameOptions().disable()
//             .and()
//             .logout().logoutSuccessUrl("/")
//             .and()
//             .oauth2Login()
//             .defaultSuccessUrl("http://localhost:3000/oauth/callback", true)
//             .userInfoEndpoint()
//             .userService(oAuthService); // OAuth2 로그인 후 사용자 정보 처리
//         return http.build();
//     }
// }

package com.jobscanner.security;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import com.jobscanner.auth.AuthSuccessHandler;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    // 허용 URL 배열
    private static final String[] ALLOWED_URLS = {
        "/dailyrank",
        "/details?**",
        "/techstack?**",
        "/job-summary",
        "/login",
        "/auth/login/kakao/**",
        "/user/**"
    };

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .cors()
            .and()
            .formLogin()
            .loginPage("/login")
            .successHandler(new AuthSuccessHandler())
            .and()
            .csrf().disable()  // CSRF 보호 비활성화
            .authorizeHttpRequests(authorizeRequests ->
                authorizeRequests
                    .requestMatchers(ALLOWED_URLS).permitAll()  // 허용된 URL
                    .anyRequest().authenticated()  // 그 외 모든 요청은 인증 필요
            )
            .headers(headers -> headers.frameOptions().disable())  // H2 콘솔 등에서 사용
            .logout(logout -> logout.logoutSuccessUrl("/"))  // 로그아웃 성공 시 리다이렉트 URL
            .oauth2Login(oauth2 -> oauth2
                .defaultSuccessUrl("http://localhost:3000/oauth/callback", true)
            );

        return http.build();
    }
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.addAllowedOrigin("http://localhost:3000"); // React 클라이언트 URL
        configuration.addAllowedMethod("*"); // 모든 HTTP 메서드 허용
        configuration.addAllowedHeader("*"); // 모든 헤더 허용
        configuration.setAllowCredentials(true); // 쿠키 및 자격증명 허용
        configuration.addExposedHeader("Authorization"); // Authorization 헤더 노출
    
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration); // 모든 경로에 대해 CORS 적용
        return source;
    }
    
}
