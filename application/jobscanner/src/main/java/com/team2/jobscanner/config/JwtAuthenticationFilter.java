package com.team2.jobscanner.config;

import com.team2.jobscanner.entity.User;
import com.team2.jobscanner.service.UserService;
import com.team2.jobscanner.util.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private UserService userService;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        String token = getTokenFromRequest(request); // 요청에서 토큰을 추출

        if (token != null) {
            try {
                // JWT 토큰에서 이메일 추출
                String email = jwtUtil.extractEmailFromToken(token);

                // 토큰 만료 여부 검사
                if (jwtUtil.isTokenExpired(token)) {
                    response.setStatus(HttpServletResponse.SC_FORBIDDEN);
                    response.getWriter().write("Token expired");
                    return;
                }

                // UserService를 통해 이메일로 사용자 정보를 로드
                User user = userService.findUserByEmail(email);  // 이메일로 사용자 조회

                if (user != null) {
                    // 인증된 사용자 정보를 SecurityContext에 설정
                    UserDetails userDetails = createUserDetails(user);
                    UsernamePasswordAuthenticationToken authentication =
                            new UsernamePasswordAuthenticationToken(userDetails, null, userDetails.getAuthorities());
                    SecurityContextHolder.getContext().setAuthentication(authentication);
                }
            } catch (Exception e) {
                // 토큰이 유효하지 않거나 오류가 발생하면 403 상태 코드 반환
                response.setStatus(HttpServletResponse.SC_FORBIDDEN);
                response.getWriter().write("Invalid token");
                return;
            }
        }

        // 필터 체인의 나머지 필터를 실행
        filterChain.doFilter(request, response);
    }

    // HTTP 요청에서 Authorization 헤더를 가져와 Bearer 토큰을 추출하는 메서드
    private String getTokenFromRequest(HttpServletRequest request) {
        String header = request.getHeader("Authorization");
        if (header != null && header.startsWith("Bearer ")) {
            return header.substring(7); // "Bearer "를 제외한 토큰 부분만 반환
        }
        return null;
    }

    // User 객체를 UserDetails로 변환하는 메서드
    private UserDetails createUserDetails(User user) {
        // User 객체를 UserDetails로 변환하는 방식
        return org.springframework.security.core.userdetails.User
                .withUsername(user.getEmail())  // 이메일을 사용자명으로 설정
                .password("")  // 실제 패스워드 없이 사용
                .authorities("USER")  // 사용자의 권한을 설정 (여기서는 예시로 "USER" 권한을 설정)
                .build();
    }

}

