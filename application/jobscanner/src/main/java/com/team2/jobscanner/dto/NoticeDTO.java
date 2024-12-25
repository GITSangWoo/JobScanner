package com.team2.jobscanner.dto;

import java.time.LocalDate;

import lombok.Getter;

@Getter
public class NoticeDTO {
    private final String duetype;
    private final LocalDate duedate ;
    private final String company;
    private final String posttitle;
    private final String responsibility;
    private final String qualification;
    private final String preferential;
    private final String tottech;

    public NoticeDTO(String duetype,LocalDate duedate, String company, String posttitle, String responsibility, String qualification, String preferential, String tottech){
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
