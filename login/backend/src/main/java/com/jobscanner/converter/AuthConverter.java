package com.jobscanner.converter;

import com.jobscanner.domain.User;
import org.springframework.security.crypto.password.PasswordEncoder;

public class AuthConverter {

    public static User toUser(String email, String name, String password, PasswordEncoder passwordEncoder) {
        return User.builder()
                .email(email)
                .role("ROLE_USER")
                .name(name)
                .provider("KAKAO")
                .build();
    }
}
