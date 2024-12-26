package com.jobscanner.util;

import lombok.Getter;

@Getter
public class BaseResponse<T> {
    private final String message;
    private final T data;

    private BaseResponse(String message, T data) {
        this.message = message;
        this.data = data;
    }

    public static <T> BaseResponse<T> onSuccess(T data) {
        return new BaseResponse<>("Success", data);
    }

    public static <T> BaseResponse<T> onFailure(String message) {
        return new BaseResponse<>(message, null);
    }
}
