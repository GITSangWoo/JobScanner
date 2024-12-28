package com.team2.jobscanner.entity;

import com.team2.jobscanner.time.AuditTime;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import java.time.LocalDateTime;
import java.util.List;

@Setter
@Getter
@Entity
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToMany(fetch = FetchType.LAZY, cascade = CascadeType.ALL,orphanRemoval = true,mappedBy = "user")
    private List<Auth> auths;

    private String email;
    private String name;

    private String oauthProvider;

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL,orphanRemoval = true)
    private List<TechStackBookmark> techStackBookmarks;

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL,orphanRemoval = true)
    private List<NoticeBookmark> noticeBookmarks;


    @Embedded
    private AuditTime auditTime;

    public User() {
        this.auditTime = new AuditTime();
    }

    @PrePersist
    public void onPrePersist() {
        // 새 데이터가 삽입될 때만 create_time은 현재 시간으로 설정됨
        if (this.auditTime.getCreateTime() == null) {
            this.auditTime.setCreateTime(LocalDateTime.now());
        }
        this.auditTime.setUpdateTime(LocalDateTime.now());  // update_time은 삽입 시점에 설정됨
    }

    @PreUpdate
    public void onPreUpdate() {
        this.auditTime.setUpdateTime(LocalDateTime.now());  // 데이터가 수정될 때마다 update_time 갱신
    }
    
}
