package com.team2.jobscanner.repository;

import com.team2.jobscanner.entity.DailyRank;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface JobRepository extends JpaRepository<DailyRank, Long> {

    
}
