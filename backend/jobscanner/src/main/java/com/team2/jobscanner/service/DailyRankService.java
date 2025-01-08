package com.team2.jobscanner.service;


import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.team2.jobscanner.dto.RankCategoryDTO;
import com.team2.jobscanner.dto.RankDTO;
import com.team2.jobscanner.entity.DailyRank;
import com.team2.jobscanner.repository.DailyRankRepository;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class DailyRankService {

    @Autowired
    private DailyRankRepository dailyRankRepository;

    // 직무와 카테고리별로 기술 스택 순위를 반환
    public RankCategoryDTO getRanksByJobTitleAndCategory(String jobTitle, String category) {
        // 해당 jobTitle과 category에 맞는 데이터 가져오기
        List<DailyRank> dailyRanks = dailyRankRepository.findALLByJobTitleAndCategoryOrderByCountDesc(jobTitle,category);

        // RankDTO 리스트로 변환
        List<RankDTO> rankDTOList = dailyRanks.stream()
            .map(dailyRank -> new RankDTO(
                dailyRank.getTechStack().getTechName(),
                dailyRank.getCount()
            ))
            .collect(Collectors.toList());

        // RankCategoryDTO로 반환
        return new RankCategoryDTO(jobTitle, category, rankDTOList);
    }
}

