package com.jobscanner.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import com.jobscanner.domain.Member;

import java.util.Optional;

public interface MemberRepository extends JpaRepository<Member, Long> {
    Optional<Member> findByEmailAndProvider(String email, String provider);
}