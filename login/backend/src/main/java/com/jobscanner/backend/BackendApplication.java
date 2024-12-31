package com.jobscanner.backend;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

@SpringBootApplication // 기본 스캔 범위는 이미 "com.jobscanner"와 하위 패키지들
// @ComponentScan(basePackages = "com.jobscanner")
public class BackendApplication {
    public static void main(String[] args) {
        SpringApplication.run(BackendApplication.class, args);
    }
}
