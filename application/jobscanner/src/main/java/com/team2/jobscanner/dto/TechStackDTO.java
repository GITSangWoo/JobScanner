package com.team2.jobscanner.dto;

import com.fasterxml.jackson.annotation.JsonPropertyOrder;

@JsonPropertyOrder({ "tech_name", "description", "youtube_link", "book_link", "docs_link", "updated_time" })
public class TechStackDTO {

    private String tech_name;
    private String description;
    private String youtube_link;
    private String book_link;
    private String docs_link;
    private String updated_time;

    // 생성자
    public TechStackDTO(String techName, String techDescription, String youtubeLink, String bookLink, String docsLink, String updatedTime) {
        this.tech_name = techName;
        this.description = techDescription;
        this.youtube_link = youtubeLink;
        this.book_link = bookLink;
        this.docs_link = docsLink;
        this.updated_time = updatedTime;
    }

    // Getter 메서드
    public String getTech_name() {
        return tech_name;
    }

    public String getDescription() {
        return description;
    }

    public String getYoutube_link() {
        return youtube_link;
    }

    public String getBook_link() {
        return book_link;
    }

    public String getDocs_link() {
        return docs_link;
    }

    public String getUpdated_time() {
        return updated_time;
    }
}