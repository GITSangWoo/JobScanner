package com.team2.jobscanner.repository;

import com.team2.jobscanner.entity.TechStack;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TechStackRepository extends JpaRepository<TechStack, String> {
    TechStack findByTechName(String techName);
    List<TechStack> findAll();  // 모든 기술 목록을 반환하는 메서드
}