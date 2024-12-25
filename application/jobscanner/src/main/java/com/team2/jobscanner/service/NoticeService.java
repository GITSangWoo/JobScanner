package com.team2.jobscanner.service;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.team2.jobscanner.dto.NoticeDTO;
import com.team2.jobscanner.repository.NoticeRepository;
import com.team2.jobscanner.entity.Notice;

@Service
public class NoticeService {

    @Autowired 
    private NoticeRepository noticeRepository;

    public List<NoticeDTO> getNoticebyjob(String jobRoles){
        List<Notice> notices = noticeRepository.findByJobRoles_JobTitleOrderByDueTypeAscDueDateAsc(jobRoles);
        List<NoticeDTO> noticeDTOlList = notices.stream()
            .map(notice -> new NoticeDTO(
            notice.getDueType(),
            notice.getDueDate(),
            notice.getCompany(),
            notice.getPostTitle(),
            notice.getResponsibility(),
            notice.getQualification(),
            notice.getPreferential(),
            notice.getTotTech()
            ))
            .collect(Collectors.toList());



        return noticeDTOlList;
    }

    
}
