package com.team2.jobscanner.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.team2.jobscanner.dto.JobRoleDTO;
import com.team2.jobscanner.entity.JobRole;
import com.team2.jobscanner.repository.JobRoleRepository;

@Service
public class JobRoleService {

    @Autowired
    private JobRoleRepository jobRoleRepository;

    // jobTitle에 해당하는 JobRole을 조회하고, DTO로 변환하여 반환
    public JobRoleDTO getJobRoleByTitle(String jobTitle) {
        JobRole jobRole = jobRoleRepository.findByJobTitle(jobTitle);
        
        if (jobRole != null) {
            // JobRole 엔티티를 DTO로 변환
            return new JobRoleDTO(
                jobRole.getJobTitle(),
                jobRole.getRoleName(),
                jobRole.getRoleDescription()
            );
        }
        return null;  // jobTitle에 해당하는 JobRole이 없으면 null 반환
    }
}

