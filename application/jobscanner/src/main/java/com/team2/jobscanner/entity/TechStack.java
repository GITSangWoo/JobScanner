package com.team2.jobscanner.entity;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.team2.jobscanner.time.AuditTime;
import jakarta.persistence.*;
import lombok.Getter;

import java.time.LocalDateTime;
import java.util.List;

@Getter
@Entity
public class TechStack {
    @Id
    @Column(name="tech_name", length = 100, nullable = false)
    private String techName;

    @JsonIgnoreProperties("techStack") 
    @OneToMany(mappedBy = "techStack")
    private List<DailyRank> dailyRank;

    @OneToMany(mappedBy = "techStack",cascade = CascadeType.ALL, orphanRemoval = true)
    private List<TechStackBookmark> techStackBookmarks;

    @Column(name="tech_description", columnDefinition = "TEXT",nullable = false)
    private String techDescription;

    @Column(name="youtube_link", columnDefinition = "TEXT")
    private String youtubeLink;

    @Column(name="book_link", columnDefinition = "TEXT")
    private String bookLink;

    @Column(name="docs_link", columnDefinition = "TEXT")
    private String docsLink;


    @Embedded
    private AuditTime auditTime;

    public TechStack() {
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
