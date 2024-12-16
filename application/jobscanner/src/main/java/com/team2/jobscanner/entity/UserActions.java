package com.team2.jobscanner.entity;

import com.team2.jobscanner.time.AuditTime;
import jakarta.persistence.*;
import java.time.LocalTime;


@Entity
public class UserActions {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name="user_id",nullable = false)
    private Users users;

    @Column(name="action_type", length = 50, nullable = false)
    private String actionType;

    @Column(name="action_description", length = 255)
    private String actionDescription;

    @Column(name = "action_Duration")
    private LocalTime actionDuration;

    @Embedded
    private AuditTime auditTime;

    // Getter, Setter
    
}
