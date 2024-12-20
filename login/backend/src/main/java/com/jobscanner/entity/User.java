package com.jobscanner.entity;

import lombok.Data;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;

@Entity
@Data
public class User {

    @Id
    private Long id;

    private String socialId; // 소셜 ID 추가
    private String provider;  // (kakao, naver, google 등)
    private String name;      // 이름
    private String nickname;  // 닉네임 (필요시)
    private String profileImageUrl; // 프로필 이미지 URL (필요시)

    // Getter와 Setter는 @Data 어노테이션에서 자동으로 생성되므로 따로 작성할 필요 없음
}
