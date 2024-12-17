package com.team2.jobscanner.entity;

import com.team2.jobscanner.time.AuditTime;
import jakarta.persistence.*;

import java.util.List;


@Entity
public class Users {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToMany(fetch = FetchType.LAZY, cascade = CascadeType.ALL,mappedBy = "users")
    private List<UserActions> userActions;

    @OneToMany(fetch = FetchType.LAZY, cascade = CascadeType.ALL,mappedBy = "users")
    private List<Auth> auths;

    @OneToMany(fetch = FetchType.LAZY, cascade = CascadeType.ALL,mappedBy = "users")
    private List<ApiHistory> apiHistories;

    @Column(name="oauth_provider", length = 50 ,nullable = false)
    private String oauthProvider;

    @Column(name="oauth_id", length = 255 ,nullable = false)
    private String oauthId;

    @Column(name = "book_mark", columnDefinition = "json")
    private String bookMark;

    @Embedded
    private AuditTime auditTime;

    // Getter, Setter
    
}
