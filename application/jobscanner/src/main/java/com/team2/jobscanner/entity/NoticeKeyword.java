package com.team2.jobscanner.entity;

import com.team2.jobscanner.time.AuditTime;
import jakarta.persistence.Column;
import jakarta.persistence.Embedded;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

public class NoticeKeyword {
    @Embedded
    private AuditTime auditTime;

    @CreationTimestamp
    @Column(name = "create_time", updatable = false)
    public LocalDateTime getCreateTime() {
        return auditTime.getCreateTime();
    }

    @UpdateTimestamp
    @Column(name = "update_time")
    public LocalDateTime getUpdateTime() {
        return auditTime.getUpdateTime();
    }
}
