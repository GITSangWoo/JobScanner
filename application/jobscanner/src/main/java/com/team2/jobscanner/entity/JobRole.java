package com.team2.jobscanner.entity;
import jakarta.persistence.*;


@Entity
public class JobRole {

    @Id
    @ManyToOne
    @JoinColumn(name= "id", referencedColumnName = "job_role_id")
    private Notice notice;

    @Column(name="role_name", length = 100, nullable = false)
    private String roleName;

    @Column(name="role_description", columnDefinition = "TEXT", nullable = false)
    private String roleDescription; 




  

    // Getter, Setter
}
