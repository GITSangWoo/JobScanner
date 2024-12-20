package com.team2.jobscanner.dto;

import java.util.List;

import lombok.Getter;

@Getter
public class RankCategoryDTO {
    private String jobtitle;  // 직무 이름
    private String category;  // 카테고리 이름
    private List<RankDTO> ranks;  // 해당 카테고리의 기술 스택 순위 리스트

    public RankCategoryDTO(String jobtitle, String category, List<RankDTO> ranks) {
        this.jobtitle = jobtitle;
        this.category = category;
        this.ranks = ranks;
    }
}