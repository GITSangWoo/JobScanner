package com.team2.jobscanner.dto;

import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import lombok.Getter;

@Getter
public class TechStackDTO {

    private final String tech_name;
    private final String description;
    private final String youtube_link;
    private final String book_link;
    private final String docs_link;

    // 생성자
    public TechStackDTO(String techName, String techDescription, String youtubeLink, String bookLink, String docsLink) {
        this.tech_name = techName;
        this.description = techDescription;
        this.youtube_link = youtubeLink;
        this.book_link = bookLink;
        this.docs_link = docsLink;
    }
}
