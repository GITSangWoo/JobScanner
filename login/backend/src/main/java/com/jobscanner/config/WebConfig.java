package com.jobscanner.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import jakarta.servlet.Filter;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpServletResponseWrapper;
import java.io.IOException;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOrigins("http://localhost:3000")  // 프론트엔드 주소
                .allowedMethods("GET", "POST", "PUT", "DELETE")
                .allowedHeaders("*")
                .allowCredentials(true)
                .maxAge(3600);  // Preflight 요청에 대한 응답을 1시간 동안 캐시하도록 설정
    }

    @Bean
    public Filter coepHeaderFilter() {
        return (request, response, chain) -> {
            HttpServletResponseWrapper wrappedResponse = new HttpServletResponseWrapper((HttpServletResponse) response) {
                @Override
                public void addHeader(String name, String value) {
                    if ("Cross-Origin-Opener-Policy".equals(name)) {
                        super.addHeader(name, "same-origin");
                    } else {
                        super.addHeader(name, value);
                    }
                }
            };
            chain.doFilter(request, wrappedResponse);
        };
    }
}
