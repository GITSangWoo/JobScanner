package com.team2.jobscanner.entity;
import jakarta.persistence.*;
import org.springframework.boot.autoconfigure.batch.BatchProperties;

import java.util.List;


@Entity
public class JobRole {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToMany(mappedBy = "jobroles")
    private List<Notice> notices;

    @Column(name="role_name", length = 100, nullable = false)
    private String roleName;

    @Column(name="role_description", columnDefinition = "TEXT", nullable = false)
    private String roleDescription; 




  

    // Getter, Setter
}
