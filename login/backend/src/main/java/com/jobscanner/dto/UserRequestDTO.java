package com.jobscanner.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

public class UserRequestDTO {

    @Getter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LoginRequestDTO {
        private String email;
        // private String password;
    }
}
