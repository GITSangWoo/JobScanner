package com.team2.jobscanner.repository;

import com.team2.jobscanner.entity.Auth;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;


@Repository
public interface AuthRepository extends JpaRepository<Auth, Long> {
    Auth findByUserId(Long userId);  // userId로 Auth 정보 찾기
}
