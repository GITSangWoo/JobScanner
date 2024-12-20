package com.team2.jobscanner.dto;

import lombok.Getter;

@Getter
public class RankDTO {
    private String techName;  // 기술 스택 이름
    private int count;        // 해당 기술 스택의 count

    public RankDTO(String techName, int count) {
        this.techName = techName;
        this.count = count;
    }
}
