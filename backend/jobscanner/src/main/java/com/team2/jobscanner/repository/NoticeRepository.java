package com.team2.jobscanner.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.team2.jobscanner.entity.Notice;


@Repository
public interface NoticeRepository extends JpaRepository<Notice, Long> {
    List<Notice> findByJobRoles_JobTitleOrderByDueTypeAscDueDateAsc(String jobTitle);
}
