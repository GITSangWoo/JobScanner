import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "./TechStackDetailsPage.css"; // CSS 파일을 import
import Cookies from 'js-cookie';
import axios from 'axios';
import { getLinkPreview } from "link-preview-js";


const TechStackDetailsPage = () => {
    const navigate = useNavigate();
    const { techStackName } = useParams(); // URL에서 techStackName만 받기
    const [techStack, setTechStack] = useState(null);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [isBookmarked, setIsBookmarked] = useState(false); // 북마크 상태
    const [nickname, setNickname] = useState(""); // 사용자 닉네임 상태
    const [linkPreviews, setLinkPreviews] = useState({}); // 링크 미리보기 상태
    const handleClick = () => {
        navigate("/", { replace: true });
        window.location.reload();
    };
    // YouTube 썸네일 URL을 가져오는 함수
    const getYouTubeThumbnailUrl = (url) => {
        if (!url) return null;
        const videoId = url.split("v=")[1];
        return `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
    };

    // 로그인 상태 확인 함수
    const checkLoginStatus = () => {
        const accessToken = Cookies.get('access_token');
        return !!accessToken; // 토큰이 있으면 true, 없으면 false
    };

    // 사용자 정보를 가져오는 함수
    useEffect(() => {
        if (checkLoginStatus()) {
            const fetchUserData = async () => {
                try {
                    const response = await fetch("/user/profile", {
                        headers: { Authorization: `Bearer ${Cookies.get('access_token')}` },
                    });
                    if (response.ok) {
                        const data = await response.json();
                        setNickname(data.name || "사용자"); // 닉네임 설정
                    }
                } catch (error) {
                    console.error("Error fetching user data:", error);
                }
            };
            fetchUserData();
        }
    }, []);

    useEffect(() => {
        axios.get(`/techstack?techName=${techStackName}`)
            .then(response => {
                const data = response.data;
                console.log("Received data:", data); // 데이터 출력
    
                setTechStack({
                    techName: data.tech_name, // 'tech_name' -> 'techName'으로 수정
                    description: data.description,
                    youtubeLink: data.youtubelink,
                    bookLink: data.booklink,
                    docsLink: data.docslink
                });
    
                // 링크 미리보기 가져오기
                const links = [
                    data.youtubelink,
                    data.booklink,
                    data.docslink
                ];
                links.forEach(link => {
                    if (link) {
                        getLinkPreview(link)
                            .then(data => {
                                setLinkPreviews(prevState => ({
                                    ...prevState,
                                    [link]: data
                                }));
                            })
                            .catch(error => {
                                console.error("Error fetching link preview:", error);
                            });
                    }
                });
            })
            .catch(error => {
                console.error("Error fetching tech stack data:", error);
            });
    }, [techStackName]);
    

        // 드롭다운 메뉴 열기/닫기 처리
        const toggleDropdown = () => {
            setIsDropdownOpen((prev) => !prev);
        };
    
        const goToJobSummary = () => {
            navigate("/job-summary"); // 기업 공고 요약 페이지로 이동
            window.location.reload();
        };
    
        // My Page 이동 처리
        const handleMypage = () => {
            if (checkLoginStatus()) {
                navigate("/mypage");
            } else {
                alert("로그인 후 이용하실 수 있습니다.");
                navigate("/login");
            }
        };

    const handleBookmark = async (techName) => {
        if (!checkLoginStatus()) {
          alert("로그인 후 이용하실 수 있습니다.");
          navigate("/login");
          return;
        }
      
        const accessToken = Cookies.get('access_token');

        // techName이 객체라면, techName.techName 값을 추출
        if (typeof techName === 'object' && techName !== null) {
            techName = techName.techName || '';  // techName 객체에서 'techName' 속성 가져오기
        }

        // techName이 빈 값일 경우 처리
        if (!techName) {
            alert("기술 스택 이름을 입력해주세요.");
            return;
        }

        console.log("Sending techName:", techName);  // techName이 올바르게 설정되었는지 확인

        try {
            const response = await axios.post(
                'http://43.202.186.119:8972/user/bookmark/tech', // 서버의 URL
                { techName }, // 요청 본문을 비워둡니다.
                {
                    headers: { Authorization: `Bearer ${accessToken}` }, // Authorization 헤더 추가
                }
            );
            alert(response.data); // 서버 응답 메시지 표시
        } catch (error) {
            if (error.response) {
                // 응답이 있는 경우
                alert('북마크 추가 실패: ' + error.response.data.message || error.response.data);
            } else {
                // 응답이 없는 경우
                alert('서버에 연결할 수 없습니다. 다시 시도해주세요.');
            }
        }
    };

    if (!techStack) {
        return <p>해당 기술 스택 정보를 찾을 수 없습니다.</p>;
    }

    return (
        <div className="tech-stack-details">
            <header className="header">
                <div className="logo-container" onClick={() => navigate("/", { replace: true })}>
                    <h1 className="logo">JobScanner</h1>
                </div>

                <div className="top-right-buttons">
                    {checkLoginStatus() ? (
                        <span className="welcome-message">{nickname}님 환영합니다!</span>
                    ) : (
                        <button className="auth-button" onClick={() => navigate("/login")}>
                            로그인
                        </button>
                    )}
                </div>
            </header>

            <div className="top-left-menu">
                <button className="menu-button" onClick={toggleDropdown}>
                    ⁝⁝⁝
                </button>
                {isDropdownOpen && (
                    <div className="dropdown-menu open">
                        <button className="dropdown-item" onClick={handleClick}>
                            기술 스택 순위
                        </button>
                        <button className="dropdown-item" onClick={goToJobSummary}>
                            채용 공고 요약
                        </button>
                        <hr />
                        <button className="dropdown-item" onClick={handleMypage}>
                            My Page
                        </button>
                    </div>
                )}
            </div>

            <div className="tech-stack-content">
                <h1 className="tech-stack-language">{techStack.techName}</h1>

                <div className="bookmark-container">
                    <button
                        className={`bookmark-button ${isBookmarked ? "active" : ""}`}
                        onClick={handleBookmark}
                    >
                        {isBookmarked ? "★" : "☆"}
                    </button>
                </div>

                <h2>설명</h2>
                <p>{techStack.description || "상세 설명이 없습니다."}</p>

                {techStack.youtubeLink && (
                    <div>
                        <h2>유튜브 링크</h2>
                        <a href={techStack.youtubeLink} target="_blank" rel="noopener noreferrer">
                            <img
                                src={getYouTubeThumbnailUrl(techStack.youtubeLink)}
                                alt="YouTube Thumbnail"
                                className="youtube-thumbnail"
                            />
                        </a>
                    </div>
                )}

                <h2>도서 링크</h2>
                {techStack.bookLink ? (
                    <a href={techStack.bookLink} target="_blank" rel="noopener noreferrer">
                        바로가기
                    </a>
                ) : (
                    <p>링크가 없습니다.</p>
                )}

                <h2>공식 문서</h2>
                {techStack.docsLink ? (
                    <a href={techStack.docsLink} target="_blank" rel="noopener noreferrer">
                        바로가기
                    </a>
                ) : (
                    <p>링크가 없습니다.</p>
                )}
            </div>
        </div>
    );
};

export default TechStackDetailsPage;
