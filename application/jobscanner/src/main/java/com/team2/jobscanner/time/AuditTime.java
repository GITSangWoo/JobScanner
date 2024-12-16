package com.team2.jobscanner.time;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;


@Embeddable
public class AuditTime {

    // create_time은 최초 생성 시에만 설정되고 수정되지 않도록 설정
    @CreationTimestamp
    @Column(name = "create_time", updatable = false)
    private LocalDateTime createTime;

    // update_time은 값이 수정될 때마다 갱신되도록 설정
    @UpdateTimestamp
    @Column(name = "update_time")
    private LocalDateTime updateTime;

    // 생성자, Getter, Setter 추가 (필요 시)
}
