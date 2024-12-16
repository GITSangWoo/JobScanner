package com.team2.jobscanner.entity;

import com.team2.jobscanner.time.AuditTime;
import jakarta.persistence.*;


import java.time.LocalDateTime;
@Entity
public class JobRole {

    @Id
    private Long id;


    private String name;

    @Embedded
    private AuditTime auditTime;

    // Getter, Setter
}
