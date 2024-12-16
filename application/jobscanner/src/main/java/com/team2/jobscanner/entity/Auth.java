package com.team2.jobscanner.entity;

import com.team2.jobscanner.time.AuditTime;
import jakarta.persistence.*;

import java.time.LocalDateTime;


@Entity
public class Auth {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name="user_id",nullable = false)
    private Users users;

    @Column(name="access_token", length = 512 ,nullable = false)
    private String accessToken;

    @Column(name="refresh_token", length = 512 ,nullable = false)
    private String refreshToken;

    @Column(name = "expired_time")
    private LocalDateTime expiredTime;

    @Embedded
    private AuditTime auditTime;

    // Getter, Setter
}
