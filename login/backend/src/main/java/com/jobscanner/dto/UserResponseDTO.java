package com.jobscanner.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;

public class UserResponseDTO {

    @Getter
    @Builder
    @AllArgsConstructor
    public static class JoinResultDTO {
        private Long id;
        private String email;
        private String name;
    }
}
