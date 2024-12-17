package com.team2.jobscanner.entity;

import com.team2.jobscanner.time.AuditTime;
import jakarta.persistence.*;


@Entity
public class DailyRank {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name="job_title", length = 4)
    private String jobTitle;

    @ManyToOne
    @JoinColumn(name="tech_name", referencedColumnName = "tech_name")
    private TechStack techstack;

    @Column(name="count")
    private int count;

    @Column(name="category", length = 20)
    private String category;

    @Embedded
    private AuditTime auditTime;

    // Getter, Setter
}

