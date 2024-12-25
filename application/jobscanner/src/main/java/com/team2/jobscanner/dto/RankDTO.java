package com.team2.jobscanner.dto;

import lombok.Getter;

@Getter
public class RankDTO {
    private final String techName;  // 기술 스택 이름
    private final int count;        // 해당 기술 스택의 count

    public RankDTO(String techName, int count) {
        this.techName = techName;
        this.count = count;
    }
}
