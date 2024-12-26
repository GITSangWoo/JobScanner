package com.jobscanner.service;

import com.jobscanner.domain.User;
import jakarta.servlet.http.HttpServletResponse;

public interface AuthServiceInterface {
    User oAuthLogin(String accessCode, HttpServletResponse httpServletResponse);
}
