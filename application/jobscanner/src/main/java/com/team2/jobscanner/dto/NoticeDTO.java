package com.team2.jobscanner.dto;

import java.time.LocalDate;

import lombok.Getter;

@Getter
public class NoticeDTO {
    private Long notice_id;
    private String duetype;
    private LocalDate duedate ;
    private String company;
    private String posttitle;
    private String responsibility;
    private String qualification;
    private String preferential;
    private String tottech;

    public NoticeDTO(Long noticeid, String duetype,LocalDate duedate, String company, String posttitle, String responsibility, String qualification, String preferential, String tottech){
        this.notice_id = noticeid;
        this.duetype = duetype;
        this.duedate = duedate;
        this.company = company;
        this.posttitle = posttitle;
        this.responsibility = responsibility;
        this.qualification = qualification;
        this.preferential = preferential;
        this.tottech = tottech;
    }

}
