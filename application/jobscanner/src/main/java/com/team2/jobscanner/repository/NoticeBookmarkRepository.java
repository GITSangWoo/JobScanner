package com.team2.jobscanner.repository;

import com.team2.jobscanner.entity.Notice;
import com.team2.jobscanner.entity.NoticeBookmark;
import com.team2.jobscanner.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface NoticeBookmarkRepository extends JpaRepository<NoticeBookmark, Long> {
    List<NoticeBookmark> findByUser(User user);
    Optional<NoticeBookmark> findByUserAndNotice(User user, Notice notice);
}
