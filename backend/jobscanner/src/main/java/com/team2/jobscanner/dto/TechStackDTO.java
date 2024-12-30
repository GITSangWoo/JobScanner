package com.team2.jobscanner.dto;

import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import lombok.Getter;

@Getter
public class TechStackDTO {

    private final String tech_name;
    private final String description;
    private final String youtubelink;
    private final String booklink;
    private final String docslink;

    // 생성자
    public TechStackDTO(String techName, String techDescription, String youtubeLink, String bookLink, String docsLink) {
        this.tech_name = techName;
        this.description = techDescription;
        this.youtubelink = youtubeLink;
        this.booklink = bookLink;
        this.docslink = docsLink;
    }
}
