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
    const [isBookmarked, setIsBookmarked] = useState(false); // 북마크 상태
    const [nickname, setNickname] = useState(""); // 사용자 닉네임 상태
    const [linkPreviews, setLinkPreviews] = useState({}); // 링크 미리보기 상태

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

    // 기술 스택 정보 가져오기
    useEffect(() => {
        axios.get(`/techstack?techName=${techStackName}`)
            .then(response => {
                const data = response.data;
                setTechStack({
                    techName: data.tech_name,
                    description: data.description,
                    youtubeLink: data.youtube_link,
                    bookLink: data.book_link,
                    documentationLink: data.docs_link
                });

                // 링크 미리보기 가져오기
                const links = [
                    data.youtube_link,
                    data.book_link,
                    data.docs_link
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

    const handleBookmark = async () => {
        if (checkLoginStatus()) {
            const accessToken = Cookies.get('access_token');
            try {
                // POST 요청을 통해 북마크 추가
                const response = await axios.post(
                    'http://43.202.186.119:8972/user/bookmark/tech',  // 서버 URL
                    { techName: techStackName },  // 전송할 데이터
                    {
                        headers: {
                            "Authorization": `Bearer ${accessToken}`  // Authorization 헤더
                        }
                    }
                );
                alert(response.data);  // 'Bookmark added successfully' 또는 'Bookmark removed successfully' 메시지
                setIsBookmarked(!isBookmarked); // 북마크 상태 토글
            } catch (error) {
                console.error("북마크 추가 실패:", error);
                alert('북마크 추가 실패: ' + error);
            }
        } else {
            alert("로그인 후 이용하실 수 있습니다.");
            navigate("/login");
        }
    };

    const getYouTubeThumbnailUrl = (url) => {
        if (!url) return null;
        const videoId = url.split("v=")[1];
        return `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
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
                {techStack.documentationLink ? (
                    <a href={techStack.documentationLink} target="_blank" rel="noopener noreferrer">
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
