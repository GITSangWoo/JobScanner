package com.team2.jobscanner.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.team2.jobscanner.entity.Notice;


@Repository
public interface NoticeRepository extends JpaRepository<Notice, Long> {
    // List<Notice> findByJobRoles_JobTitleOrderByDueTypeAscDueDateAsc(String jobTitle);
    @Query("SELECT n FROM Notice n WHERE n.jobRoles.jobTitle = :jobTitle " +
           "AND (n.dueDate IS NULL OR n.dueDate >= CURRENT_DATE) " +
           "ORDER BY n.dueType ASC, n.dueDate ASC")
    List<Notice> findByJobRoles_JobTitleAndDueDateIsNullOrDueDateAfterOrderByDueTypeAscDueDateAsc(@Param("jobTitle") String jobTitle);
}
