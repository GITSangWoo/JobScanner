package com.jobscanner.dto;

import lombok.Data;

@Data
public class SocialLoginDto {
    private String id;
    private String name;
    private String nickname;
    private String profileImageUrl;
    private String provider;
}
