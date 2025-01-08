package com.team2.jobscanner.repository;

import com.team2.jobscanner.entity.DailyRank;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface DailyRankRepository extends JpaRepository<DailyRank, Long> {
    List<DailyRank> findALLByJobTitleAndCategoryOrderByCountDesc(String jobTitle, String category);
}