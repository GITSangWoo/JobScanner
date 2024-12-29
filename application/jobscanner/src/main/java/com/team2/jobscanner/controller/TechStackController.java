package com.team2.jobscanner.controller;

import com.team2.jobscanner.dto.TechStackDTO;
import com.team2.jobscanner.entity.TechStack;
import com.team2.jobscanner.service.TechStackService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@CrossOrigin(origins = "http://43.202.186.119")
@RestController
@RequestMapping("/techstack")
public class TechStackController {

    private final TechStackService techStackService;

    public TechStackController(TechStackService techStackService) {
        this.techStackService = techStackService;
    }

    @GetMapping("/all")
    public ResponseEntity<List<TechStack>> getAllTechStacks() {
        try {
            List<TechStack> techStacks = techStackService.getAllTechStacks();
            return ResponseEntity.ok(techStacks);  // 기술 목록 반환
        } catch (Exception e) {
            return ResponseEntity.status(500).body(null);  // 에러 처리
        }
    }

    @GetMapping
    public TechStackDTO getTechDetails(@RequestParam String techName) {
        return techStackService.getTechDetails(techName);
    }
}