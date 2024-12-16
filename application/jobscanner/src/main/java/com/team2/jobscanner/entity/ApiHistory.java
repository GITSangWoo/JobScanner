package com.team2.jobscanner.entity;

import com.team2.jobscanner.time.AuditTime;
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


    @Embedded
    private AuditTime auditTime;

    // Getter, Setter
}
