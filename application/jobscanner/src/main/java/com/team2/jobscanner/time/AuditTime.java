package com.team2.jobscanner.time;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import java.time.LocalDateTime;
import lombok.Getter;
import lombok.Setter;


@Embeddable
@Getter  // 클래스 수준에서 모든 필드의 getter를 자동 생성
@Setter  // 클래스 수준에서 모든 필드의 setter를 자동 생성
public class AuditTime {

    @Column(name = "create_time", updatable = false)
    private LocalDateTime createTime;

    @Column(name = "update_time")
    private LocalDateTime updateTime;

    // 기본 생성자
    public AuditTime() {
        this.createTime = LocalDateTime.now();
        this.updateTime = LocalDateTime.now();
    }
}




