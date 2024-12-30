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
    public List<TechStackDTO> getAllTechStacks() {
        return techStackService.getAllTechStacks();
    }

    @GetMapping
    public TechStackDTO getTechDetails(@RequestParam String techName) {
        return techStackService.getTechDetails(techName);
    }
}