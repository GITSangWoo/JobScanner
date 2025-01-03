package com.team2.jobscanner.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.team2.jobscanner.dto.RankCategoryDTO;
import com.team2.jobscanner.service.DailyRankService;

@CrossOrigin(origins = {"http://43.202.186.119","https://www.jobscanner.site" })
@RestController
public class DailyRankController {

    @Autowired
    private DailyRankService dailyRankService;

    // 직무와 카테고리에 맞는 기술 스택 순위를 반환하는 API
    @GetMapping("/dailyrank")
    public RankCategoryDTO getRanksByJobTitleAndCategory(@RequestParam String jobtitle, @RequestParam String category) {
        return dailyRankService.getRanksByJobTitleAndCategory(jobtitle, category);
    }
}

