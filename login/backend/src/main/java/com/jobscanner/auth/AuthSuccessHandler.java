package com.jobscanner.auth;

import java.io.PrintWriter;
import java.io.IOException;  // java.io.IOException 임포트 추가

import org.springframework.context.annotation.Configuration;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationSuccessHandler;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@Configuration
public class AuthSuccessHandler extends SimpleUrlAuthenticationSuccessHandler {

    public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response,
            Authentication authentication){
        String targetUrl = "";
        try {
            response.setStatus(HttpServletResponse.SC_OK);
            PrintWriter writer = response.getWriter();
            writer.write(targetUrl);
            writer.flush();
            writer.close();
        } catch (IOException e) {
            logger.error(e.getMessage(), e);
        }
    }
}