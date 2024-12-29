package com.team2.jobscanner.service;

import com.team2.jobscanner.dto.TechStackDTO;
import com.team2.jobscanner.entity.TechStack;
import com.team2.jobscanner.repository.TechStackRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class TechStackService {

    private final TechStackRepository techStackRepository;

    public TechStackService(TechStackRepository techStackRepository) {
        this.techStackRepository = techStackRepository;
    }

    public TechStackDTO getTechDetails(String techName) {
        TechStack techStack = techStackRepository.findByTechName(techName);
        // 엔티티에서 DTO로 변환
        return convertToDTO(techStack);
    }

    public List<TechStackDTO> getAllTechStacks() {
        List<TechStack> techStacks = techStackRepository.findAll();
        // 엔티티에서 DTO로 변환
        return techStacks.stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    private TechStackDTO convertToDTO(TechStack techStack) {
        return new TechStackDTO(
                techStack.getTechName(),
                techStack.getTechDescription(),
                techStack.getYoutubeLink(),
                techStack.getBookLink(),
                techStack.getDocsLink()
        );
    }
}