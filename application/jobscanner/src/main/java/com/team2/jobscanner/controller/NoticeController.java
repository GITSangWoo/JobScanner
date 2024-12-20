package com.team2.jobscanner.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.team2.jobscanner.dto.NoticeDTO;
import com.team2.jobscanner.service.NoticeService;

@RestController
public class NoticeController {

    @Autowired NoticeService noticeService;

    @GetMapping("/notice")
    public List<NoticeDTO> getNoitceByJob(@RequestParam String jobtitle){
        return noticeService.getNoticebyjob(jobtitle);
    }
}
