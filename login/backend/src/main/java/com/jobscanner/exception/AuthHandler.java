package com.jobscanner.exception;

public class AuthHandler extends RuntimeException {
    public AuthHandler(String message) {
        super(message);
    }
}
