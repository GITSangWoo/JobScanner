package com.team2.jobscanner.entity;

import com.team2.jobscanner.time.AuditTime;
import jakarta.persistence.*;

import java.util.List;


@Entity
public class Users {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToMany(mappedBy = "users")
    private List<UserActions> userActions;

    @OneToMany(mappedBy = "users")
    private List<Auth> auths;

    @OneToMany(mappedBy = "users")
    private List<ApiHistory> apiHistories;

    @Column(name="oauth_provider", length = 50 ,nullable = false)
    private String oauthProvider;

    @Column(name="oauth_id", length = 255 ,nullable = false)
    private String oauthId;

    @Column(name = "book_mark", columnDefinition = "json")
    private String bookMark;

    @OneToMany(fetch = FetchType.LAZY, cascade = CascadeType.ALL)
    @Column(name = "notice_id")
    private List<Notice> noticeId;

    @OneToMany(fetch = FetchType.LAZY, cascade = CascadeType.ALL)
    @Column(name = "tech_stack_id")
    private List<TechStack> techStackId;

    @Column

    @Embedded
    private AuditTime auditTime;

    // Getter, Setter
    
}
