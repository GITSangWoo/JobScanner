package com.team2.jobscanner.dto;

import lombok.Getter;


@Getter
public class JobRoleDTO {
    private String jobTitle;
    private String roleName;
    private String roleDescription;

    // 생성자
    public JobRoleDTO(String jobTitle, String roleName, String roleDescription) {
        this.jobTitle = jobTitle;
        this.roleName = roleName;
        this.roleDescription = roleDescription;
    }
}
