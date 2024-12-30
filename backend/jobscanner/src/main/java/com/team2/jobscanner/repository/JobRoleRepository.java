package com.team2.jobscanner.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.team2.jobscanner.entity.JobRole;

@Repository
public interface JobRoleRepository extends JpaRepository<JobRole, String> {
    // jobTitle에 해당하는 하나의 JobRole만 반환
    JobRole findByJobTitle(String jobTitle);
}

