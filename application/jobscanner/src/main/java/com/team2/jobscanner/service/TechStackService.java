package com.team2.jobscanner.service;

import com.team2.jobscanner.dto.TechStackDTO;
import com.team2.jobscanner.entity.TechStack;
import com.team2.jobscanner.repository.TechStackRepository;
import org.springframework.stereotype.Service;

@Service
public class TechStackService {

    private final TechStackRepository techStackRepository;

    public TechStackService(TechStackRepository techStackRepository) {
        this.techStackRepository = techStackRepository;
    }

    public TechStackDTO getTechDetails(String techName) {
        TechStack techStack = techStackRepository.findByTechName(techName);

        // DTO로 변환
        return new TechStackDTO(
                techStack.getTechName(),          // 기술 이름
                techStack.getTechDescription(),   // 기술 설명
                techStack.getYoutubeLink(),       // 유튜브 링크
                techStack.getBookLink(),          // 도서 링크
                techStack.getDocsLink(),          // 공식 문서 링크
                techStack.getAuditTime().getUpdateTime().toString() // 업데이트 시간
        );
    }
}