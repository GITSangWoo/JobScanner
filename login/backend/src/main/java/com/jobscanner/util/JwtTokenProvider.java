package com.jobscanner.util;

import io.jsonwebtoken.*;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.Date;

@Component
public class JwtTokenProvider {

    @Value("${app.auth.tokenSecret}")
    private String secretKey;

    @Value("${app.auth.tokenExpiry}")
    private long tokenValidity; // 30분

    @Value("${app.auth.refreshTokenExpiry}")
    private long refreshTokenValidity; // 7일

    // 토큰 생성
    public String generateToken(String userId) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + tokenValidity);

        return Jwts.builder()
                .setSubject(userId)
                .setIssuedAt(now)
                .setExpiration(expiryDate)
                .signWith(SignatureAlgorithm.HS512, secretKey)  // 여전히 deprecated되었지만 여전히 사용됨
                .compact();
    }

    // 토큰에서 사용자 ID 추출
    public String getUserIdFromToken(String token) {
        Claims claims = Jwts.parserBuilder()  // parser -> parserBuilder로 변경
                .setSigningKey(secretKey)
                .build()  // builder 패턴을 이용해 JWTParser 객체를 생성
                .parseClaimsJws(token)
                .getBody();

        return claims.getSubject();
    }

    // 토큰 유효성 검사
    public boolean validateToken(String token) {
        try {
            Jwts.parserBuilder()  // parser -> parserBuilder로 변경
                .setSigningKey(secretKey)
                .build()  // JWTParser 객체 생성
                .parseClaimsJws(token);  // JWT claims parsing
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            // 토큰이 유효하지 않음
            return false;
        }
    }
}
