package com.team2.jobscanner.entity;
import java.time.LocalDateTime;
import com.team2.jobscanner.time.AuditTime;
import jakarta.persistence.*;
import lombok.Getter;

@Getter
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

    public ApiHistory() {
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
