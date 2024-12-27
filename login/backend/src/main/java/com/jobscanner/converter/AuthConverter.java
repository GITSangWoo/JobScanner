package com.jobscanner.converter;

import com.jobscanner.domain.User;


public class AuthConverter {

    public static User toUser(String email, String name) {
        return User.builder()
                .email(email)
                .role("ROLE_USER")
                .name(name)
                .provider("KAKAO")
                .build();
    }
}
