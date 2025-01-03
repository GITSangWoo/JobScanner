package com.team2.jobscanner.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.team2.jobscanner.dto.JobRoleDTO;
import com.team2.jobscanner.service.JobRoleService;

@CrossOrigin(origins = {"http://43.202.186.119","http://www.jobscanner.site" })
@RestController
public class JobRoleController {

    @Autowired
    private JobRoleService jobRoleService;

    @GetMapping("/jobrole")
    public JobRoleDTO getJobRoleByTitle(@RequestParam String jobtitle) {
        // jobTitle에 해당하는 JobRoleDTO를 반환
        return jobRoleService.getJobRoleByTitle(jobtitle);
    }
}



