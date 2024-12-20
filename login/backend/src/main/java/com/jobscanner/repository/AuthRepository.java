package com.jobscanner.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.jobscanner.domain.Auth;

import java.util.Optional;;


@Repository
public interface AuthRepository extends JpaRepository<Auth, Long> {
    Optional<Auth> findByUserId(Long userId); // userId로 auth 정보 찾기
}
