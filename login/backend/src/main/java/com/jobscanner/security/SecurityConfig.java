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
}
