package com.team2.jobscanner.repository;

import com.team2.jobscanner.entity.TechStack;
import com.team2.jobscanner.entity.TechStackBookmark;
import com.team2.jobscanner.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface TechStackBookmarkRepository extends JpaRepository<TechStackBookmark, Long> {
    List<TechStackBookmark> findByUser(User user);
    Optional<TechStackBookmark> findByUserAndTechStack(User user, TechStack techStack);
}

