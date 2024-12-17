package com.team2.jobscanner.entity;

import java.time.LocalDateTime;

import org.hibernate.annotations.CreationTimestamp;

import jakarta.persistence.*;


@Entity
public class ApiHistory {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name="user_id",nullable = false)
    private Users users;

    @Column(name="request_api_url", length = 200 ,nullable = false)
    private String requestApiUrl;

    @Column(name="request_params",columnDefinition = "TEXT")
    private String  requestParams;

    @Column(name="agent", length = 255 ,nullable = false)
    private String agent;

    @Column(name="ip", length = 39 ,nullable = false)
    private String ip;


    // create_time은 최초 생성 시에만 설정되고 수정되지 않도록 설정
    @CreationTimestamp
    @Column(name = "create_time", updatable = false)
    private LocalDateTime createTime;

    // Getter, Setter
}
