package com.team2.jobscanner.dto;

import lombok.Getter;
import java.util.List;
import java.util.stream.Collectors;

@Getter
public class UserDTO {
    private final String email;
    private final String name;
    private final List<TechStackDTO> techStackBookmarks;
    private final List<NoticeDTO> noticeBookmarks;

    public UserDTO(String email, String name, List<TechStackDTO> techStackBookmarks, List<NoticeDTO> noticeBookmarks) {
        this.email = email;
        this.name = name;
        this.techStackBookmarks = techStackBookmarks.stream()
                .map(techStack -> new TechStackDTO(techStack.getTech_name(),techStack.getDescription(),techStack.getYoutube_link(),techStack.getBook_link(),techStack.getDocs_link()))
                .collect(Collectors.toList());
        this.noticeBookmarks = noticeBookmarks.stream()
                .map(notice -> new NoticeDTO(notice.getNoticeid(),notice.getDuetype(),notice.getDuedate(),notice.getCompany(),notice.getPosttitle(),notice.getResponsibility(),notice.getQualification(),notice.getPreferential(), notice.getTottech(),notice.getOrgurl()))
                .collect(Collectors.toList());
    }
    // Getter, Setter
}

