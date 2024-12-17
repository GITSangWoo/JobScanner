package com.team2.jobscanner.entity;

import com.team2.jobscanner.time.AuditTime;
import jakarta.persistence.*;
import org.springframework.boot.autoconfigure.batch.BatchProperties;

import java.util.List;


@Entity
public class TechStack {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToMany(mappedBy = "techstack")
    private List<DailyRank> dailyRank;

    @Column(name="tech_name", length = 100, nullable = false, unique = true)
    private String techName;

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

    // Getter, Setter
    
}
