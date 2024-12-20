package com.team2.jobscanner.repository;

import com.team2.jobscanner.entity.TechStack;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface TechStackRepository extends JpaRepository<TechStack, String> {
    TechStack findByTechName(String techName);
}