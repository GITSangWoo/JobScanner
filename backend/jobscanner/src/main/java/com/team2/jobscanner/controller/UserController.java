package com.team2.jobscanner.controller;

import com.team2.jobscanner.dto.UserDTO;
import com.team2.jobscanner.entity.User;
import com.team2.jobscanner.service.UserService;

import java.util.Map;

import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

// @CrossOrigin(origins = "http://43.202.186.119", allowedHeaders = "*", methods = {RequestMethod.GET, RequestMethod.POST})
@CrossOrigin(origins = "http://43.202.186.119")
@RestController
@RequestMapping("/user")
public class UserController {

    private final UserService userService;

    // 생성자 주입 방식
    public UserController(UserService userService) {
        this.userService = userService;
    }

    // 프로필 정보 제공
    @GetMapping("/profile")
    public ResponseEntity<?> getProfile(@RequestHeader(value = HttpHeaders.AUTHORIZATION) String authorization) {
        try {
            // Authorization 헤더에서 "Bearer " 부분을 제거하고 액세스 토큰만 추출
            String accessToken = authorization.substring(7);  // "Bearer "가 7글자이므로 이를 제외한 부분이 토큰입니다.

            // 액세스 토큰을 해석하여 사용자 정보를 조회
            User user = userService.getUserInfoFromAccessToken(accessToken);

            if (user == null) {
                // 액세스 토큰이 만료되었으면 리프레시 토큰으로 새 액세스 토큰 발급
                String refreshToken = userService.getRefreshTokenByUserId(user.getId());
                String newAccessToken = userService.refreshAccessToken(refreshToken);

                if (newAccessToken != null) {
                    // 새 액세스 토큰을 응답에 포함시켜 전달
                    return ResponseEntity.ok(newAccessToken);
                } else {
                    // 리프레시 토큰도 만료되었으면 재로그인 요청
                    return ResponseEntity.status(401).body("Re-login required");
                }
            }

            // 유저 정보 반환
            UserDTO userDTO = userService.getUserProfile(user.getEmail());
            return ResponseEntity.ok(userDTO);
        } catch (Exception e) {
            // 액세스 토큰을 통한 사용자 정보 조회 실패
            return ResponseEntity.status(500).body("Internal Server Error");
        }
    }

    @PostMapping("/bookmark/notice")
    public ResponseEntity<?> addOrRemoveBookmark(@RequestHeader("Authorization") String authorization,
                                                 @RequestParam Long noticeId) {
        try {
            // 액세스 토큰에서 유저 정보 추출
            String accessToken = authorization.substring(7);  // "Bearer "를 제외한 토큰
            boolean isAdded = userService.addOrRemoveNoticeBookmark(accessToken, noticeId);
            return ResponseEntity.ok(isAdded ? "북마크가 성공적으로 추가됐어요" : "북마크가 성공적으로 해제됐어요");
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Error processing bookmark");
        }
    }

    // @PostMapping("/bookmark/tech")
    // public ResponseEntity<?> addOrRemoveTechStackBookmark(@RequestHeader("Authorization") String authorization,
    //                                                       @RequestParam String techName) {
    //     try {
    //         String accessToken = authorization.substring(7);  // "Bearer "를 제외한 토큰
    //         boolean isAdded = userService.addOrRemoveTechStackBookmark(accessToken, techName);
    //         return ResponseEntity.ok(isAdded ? "기술 스택이 성공적으로 북마크되었습니다." : "기술 스택 북마크가 성공적으로 해제되었습니다.");
    //     } catch (Exception e) {
    //         return ResponseEntity.status(500).body("기술 스택 북마크 처리 중 오류가 발생했습니다.");
    //     }
    // }
    @PostMapping("/bookmark/tech")
    public ResponseEntity<?> addOrRemoveTechStackBookmark(@RequestHeader("Authorization") String authorization,
                                                            @RequestBody Map<String, String> techData) {
            try {
                String accessToken = authorization.substring(7);  // "Bearer "를 제외한 토큰
                String techName = techData.get("techName");  // techName을 Map에서 가져오기
                boolean isAdded = userService.addOrRemoveTechStackBookmark(accessToken, techName);
                return ResponseEntity.ok(isAdded ? "기술 스택이 성공적으로 북마크되었습니다." : "기술 스택 북마크가 성공적으로 해제되었습니다.");
            } catch (Exception e) {
                return ResponseEntity.status(500).body("기술 스택 북마크 처리 중 오류가 발생했습니다.");
            }
        }


}


