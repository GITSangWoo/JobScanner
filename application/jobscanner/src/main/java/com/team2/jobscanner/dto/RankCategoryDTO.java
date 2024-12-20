package com.team2.jobscanner.dto;

import java.util.List;

import lombok.Getter;

@Getter
public class RankCategoryDTO {
    private String jobTitle;  // 직무 이름
    private String category;  // 카테고리 이름
    private List<RankDTO> ranks;  // 해당 카테고리의 기술 스택 순위 리스트

    public RankCategoryDTO(String jobTitle, String category, List<RankDTO> ranks) {
        this.jobTitle = jobTitle;
        this.category = category;
        this.ranks = ranks;
    }
}