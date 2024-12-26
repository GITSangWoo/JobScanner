package com.jobscanner.converter;

import com.jobscanner.domain.User;
import com.jobscanner.dto.UserResponseDTO;

public class UserConverter {

    public static UserResponseDTO.JoinResultDTO toJoinResultDTO(User user) {
        return UserResponseDTO.JoinResultDTO.builder()
                .id(user.getId())
                .email(user.getEmail())
                .name(user.getName())
                .build();
    }
}
