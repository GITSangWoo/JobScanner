
package com.team2.jobscanner.dto;

import lombok.Getter;

@Getter
public class LoginRequestDTO {
    private final String email;
    private final String name;
    private final String oauthProvider;

   public LoginRequestDTO(String email, String name, String oauthProvider) {
       this.email = email;
       this.name = name;
       this.oauthProvider = oauthProvider;
   }
}

