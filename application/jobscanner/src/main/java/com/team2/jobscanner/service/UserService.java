package com.team2.jobscanner.service;

import com.team2.jobscanner.dto.NoticeDTO;
import com.team2.jobscanner.dto.TechStackDTO;
import com.team2.jobscanner.dto.UserDTO;
import com.team2.jobscanner.entity.User;
import com.team2.jobscanner.repository.NoticeBookmarkRepository;
import com.team2.jobscanner.repository.TechStackBookmarkRepository;
import com.team2.jobscanner.repository.UserRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class UserService {
    private final UserRepository userRepository;
    private final TechStackBookmarkRepository techStackBookmarkRepository;
    private final NoticeBookmarkRepository noticeBookmarkRepository;

    // 기존 사용자 조회 또는 새 사용자 생성
    public User findOrCreateUser(String oauthProvider, String email, String name) {
        // Email과 oauthProvider로 기존 사용자 검색
        Optional<User> existingUser = userRepository.findByEmailAndOauthProvider(email,oauthProvider);

        // 기존 사용자 있으면 반환, 없으면 새로 등록
        // 새 사용자 등록
        return existingUser.orElseGet(() -> registerUser(email, name, oauthProvider));
    }

    // 새 사용자 등록
    public User registerUser(String email, String name, String oauthProvider) {
        User user = new User();
        user.setEmail(email);
        user.setName(name);
        user.setOauthProvider(oauthProvider);
        return userRepository.save(user);  // 새 사용자 저장 후 반환
    }
    // 이메일로 사용자 찾기
    public User findUserByEmail(String email) {
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));
    }

    public UserService(UserRepository userRepository,
                       TechStackBookmarkRepository techStackBookmarkRepository,
                       NoticeBookmarkRepository noticeBookmarkRepository) {
        this.userRepository = userRepository;
        this.techStackBookmarkRepository = techStackBookmarkRepository;
        this.noticeBookmarkRepository = noticeBookmarkRepository;
    }

    public UserDTO getUserProfile(String email) {
        User user = findUserByEmail(email);  // 이메일로 사용자 조회

        List<TechStackDTO> techStackDTOs = techStackBookmarkRepository.findByUser(user).stream()
                .map(bookmark -> new TechStackDTO(
                        bookmark.getTechStack().getTechName(),
                        bookmark.getTechStack().getTechDescription(),
                        bookmark.getTechStack().getYoutubeLink(),
                        bookmark.getTechStack().getBookLink(),
                        bookmark.getTechStack().getDocsLink()
                )).collect(Collectors.toList());

        List<NoticeDTO> noticeDTOs = noticeBookmarkRepository.findByUser(user).stream()
                .map(bookmark -> new NoticeDTO(
                        bookmark.getNotice().getDueType(),
                        bookmark.getNotice().getDueDate(),
                        bookmark.getNotice().getCompany(),
                        bookmark.getNotice().getPostTitle(),
                        bookmark.getNotice().getResponsibility(),
                        bookmark.getNotice().getQualification(),
                        bookmark.getNotice().getPreferential(),
                        bookmark.getNotice().getTotTech()
                ))
                .collect(Collectors.toList());

        return new UserDTO(user.getEmail(), user.getName(), techStackDTOs, noticeDTOs);
    }
}

