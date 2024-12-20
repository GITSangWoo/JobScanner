package com.team2.jobscanner.entity;

import com.team2.jobscanner.time.AuditTime;
import jakarta.persistence.*;
import lombok.Getter;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Getter
@Entity
public class Notice {

    @Id
    private Long notice_id;

    @ManyToOne
    @JoinColumn(name = "job_title", nullable = false, referencedColumnName = "job_title")
    private JobRole jobRoles;

    @Column(name = "due_type", length = 20, nullable = false)
    private String dueType;

    @Column(name = "due_date")
    private LocalDate dueDate;

    @Column(name = "company", length = 255, nullable = false)
    private String company;

    @Column(name = "post_title", length = 255, nullable = false)
    private String postTitle;

    @Column(name = "responsibility", columnDefinition = "TEXT")
    private String responsibility;

    @Column(name = "qualification", columnDefinition = "TEXT")
    private String qualification;

    @Column(name = "preferential", columnDefinition = "TEXT")
    private String preferential;

    @Column(name = "tot_tech", length = 1000)
    private String totTech;

    @Embedded
    private AuditTime auditTime;

    public Notice() {
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


