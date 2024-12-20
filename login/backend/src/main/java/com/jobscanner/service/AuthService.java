package com.jobscanner.service;

import com.jobscanner.dto.SocialLoginDto;
import com.jobscanner.entity.User;
import com.jobscanner.repository.UserRepository;
import com.jobscanner.util.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final JwtTokenProvider jwtTokenProvider;

    // 카카오 회원가입 처리
    public String handleKakaoSignup(SocialLoginDto kakaoDto) {
        User user = userRepository.findBySocialIdAndProvider(kakaoDto.getId(), "kakao").orElse(null);
        if (user == null) {
            user = new User();
            user.setSocialId(kakaoDto.getId());
            user.setProvider("kakao");
            user.setName(kakaoDto.getName());
            user.setNickname(kakaoDto.getNickname()); // 필요시 사용
            user.setProfileImageUrl(kakaoDto.getProfileImageUrl()); // 필요시 사용
            userRepository.save(user);
        }

        // 사용자 정보가 DB에 저장된 후 JWT 토큰 발급
        String token = jwtTokenProvider.generateToken(user.getSocialId());
        return token;
    }

    // 네이버 회원가입 처리
    public String handleNaverSignup(SocialLoginDto naverDto) {
        User user = userRepository.findBySocialIdAndProvider(naverDto.getId(), "naver").orElse(null);
        if (user == null) {
            user = new User();
            user.setSocialId(naverDto.getId());
            user.setProvider("naver");
            user.setName(naverDto.getName());
            user.setNickname(naverDto.getNickname()); // 필요시 사용
            user.setProfileImageUrl(naverDto.getProfileImageUrl()); // 필요시 사용
            userRepository.save(user);
        }

        // 사용자 정보가 DB에 저장된 후 JWT 토큰 발급
        String token = jwtTokenProvider.generateToken(user.getSocialId());
        return token;
    }

    // 구글 회원가입 처리
    public String handleGoogleSignup(SocialLoginDto googleDto) {
        User user = userRepository.findBySocialIdAndProvider(googleDto.getId(), "google").orElse(null);
        if (user == null) {
            user = new User();
            user.setSocialId(googleDto.getId());
            user.setProvider("google");
            user.setName(googleDto.getName());
            user.setNickname(googleDto.getNickname()); // 필요시 사용
            user.setProfileImageUrl(googleDto.getProfileImageUrl()); // 필요시 사용
            userRepository.save(user);
        }

        // 사용자 정보가 DB에 저장된 후 JWT 토큰 발급
        String token = jwtTokenProvider.generateToken(user.getSocialId());
        return token;
    }
}
