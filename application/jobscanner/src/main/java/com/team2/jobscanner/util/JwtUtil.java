package com.team2.jobscanner.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.util.Date;

@Component
public class JwtUtil {

    @Value("${jwt.header}")
    private String jwtHeader;

    // application.properties 또는 application.yml에서 secret-key와 expiration-time을 읽어옵니다.
    @Value("${jwt.secret-key}")
    private String secretKeybase64;

    @Value("${jwt.expiration-time}")
    private long expirationTime;

    private SecretKey getSigningKey() {
        byte[] keyBytes = Decoders.BASE64.decode(this.secretKeybase64);
        return Keys.hmacShaKeyFor(keyBytes);
    }

    // JWT 토큰 생성 메서드
    public String createToken(String email) {
        return Jwts.builder()
                .issuer("jobscanner")
                .header()
                .keyId(jwtHeader)
                .and()
                .subject(email)  // 토큰에 이메일 설정
                .issuedAt(new Date())  // 발급 시간 설정
                .expiration(new Date(System.currentTimeMillis() + expirationTime))  // 만료 시간 설정
                .signWith(this.getSigningKey())  // 서명
                .compact();  // 최종 JWT 토큰 생성
    }

    // JWT 토큰에서 이메일 추출 메서드
    public String extractEmailFromToken(String token) {
        Claims claims = Jwts.parser()  // JwtParserBuilder를 사용
                .verifyWith(this.getSigningKey())  // 서명 검증을 위한 비밀 키 설정
                .build()  // JwtParser 인스턴스 생성
                .parseSignedClaims(token)  // JWT 파싱
                .getPayload();  // Claims 객체 가져오기
        return claims.getSubject();  // 이메일 반환
    }

    // JWT 토큰 유효성 검사 (예: 만료 여부)
    public boolean isTokenExpired(String token) {
        return extractExpirationDate(token).before(new Date());
    }

    // 토큰에서 만료일 추출
    private Date extractExpirationDate(String token) {
        Claims claims = Jwts.parser()  // JwtParserBuilder를 사용
                .verifyWith(this.getSigningKey())  // 서명 검증을 위한 비밀 키 설정
                .build()  // JwtParser 인스턴스 생성
                .parseSignedClaims(token)  // JWT 파싱
                .getPayload();  // Claims 객체 가져오기
        return claims.getExpiration();  // 만료일 반환
    }
}




