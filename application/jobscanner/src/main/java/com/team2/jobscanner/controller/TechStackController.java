package com.team2.jobscanner.controller;

import com.team2.jobscanner.dto.TechStackDTO;
import com.team2.jobscanner.service.TechStackService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/techstack")
public class TechStackController {

    private final TechStackService techStackService;

    public TechStackController(TechStackService techStackService) {
        this.techStackService = techStackService;
    }

    @GetMapping
    public TechStackDTO getTechDetails(@RequestParam String techName) {
        return techStackService.getTechDetails(techName);
    }
}