import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "./TechStackDetailsPage.css"; // CSS 파일을 import
import Cookies from 'js-cookie';

const TechStackDetailsPage = () => {
    const navigate = useNavigate();
    const [isDropdownOpen, setIsDropdownOpen] = useState(false); // 더보기 드롭다운 상태
    const { techStackName } = useParams(); // URL에서 techStackName만 받기
    const [techStack, setTechStack] = useState(null);
    const [isBookmarked, setIsBookmarked] = useState(false);
    const [nickname, setNickname] = useState(""); // 사용자 닉네임 상태

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
                    const response = await fetch("/auth/user", {
                        headers: { Authorization: `Bearer ${Cookies.get('access_token')}` },
                    });
                    if (response.ok) {
                        const data = await response.json();
                        setNickname(data.nickname || "사용자"); // 닉네임 설정
                    }
                } catch (error) {
                    console.error("Error fetching user data:", error);
                }
            };
            fetchUserData();
        }
    }, []);

    const fetchTechStackDetails = async () => {
        try {
            const response = await fetch(`/techstack?techName=${techStackName}`);
            const data = await response.json();
            
            if (response.ok) {
                // 데이터를 매핑하여 구조화
                const transformedData = {
                    techName: data.tech_name || "정보 없음",
                    description: data.description || "설명이 없습니다.",
                    youtubeLink: data.youtubelink || "",
                    bookLink: data.booklink || "",
                    docsLink: data.docslink || "",
                };
                setTechStack(transformedData);
            } else {
                console.error("Error fetching tech stack data:", data);
                setTechStack(null);
            }
        } catch (error) {
            console.error("Error fetching tech stack details:", error);
            setTechStack(null);
        }
    };

    useEffect(() => {
        fetchTechStackDetails(); // 컴포넌트 마운트 시 기술 스택 정보 가져오기
    }, [techStackName]);

    const handleClick = () => {
        navigate("/", { replace: true }); // navigate 호출
        window.location.reload();
    };

    const toggleDropdown = () => {
        setIsDropdownOpen(!isDropdownOpen); // 더보기 버튼 토글
    };

    const handleLogin = () => {
        navigate("/login");
    };

    const goToJobSummary = () => {
        navigate("/job-summary"); // 기업 공고 요약 페이지로 이동
    };

    // 북마크 토글 처리
    const handleBookmark = () => {
        if (checkLoginStatus()) {
            setIsBookmarked(!isBookmarked); // 북마크 상태 토글
        } else {
            alert("로그인 후 이용하실 수 있습니다.");
            navigate("/login");
        }
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

    if (!techStack) {
        return <p>해당 기술 스택 정보를 찾을 수 없습니다.</p>;
    }

    return (
        <div className="tech-stack-details">
            {/* 상단 로고와 메뉴 */}
            <header className="header">
                <div className="logo-container" onClick={handleClick}>
                    <h1 className="logo">JobScanner</h1>
                </div>

                {/* 로그인/회원가입 버튼 */}
                <div className="top-right-buttons">
                    {checkLoginStatus() ? (
                        <span className="welcome-message">{nickname}님 환영합니다!</span>
                    ) : (
                        <button className="auth-button" onClick={handleLogin}>
                            로그인
                        </button>
                    )}
                </div>

                {/* 더보기 메뉴 */}
                <div className="top-left-menu">
                    <button className="menu-button" onClick={toggleDropdown}>
                        ⁝⁝⁝
                    </button>
                    <div className={`dropdown-menu ${isDropdownOpen ? "open" : ""}`}>
                        <button className="dropdown-item" onClick={handleClick}>기술 스택 순위</button>
                        <button className="dropdown-item" onClick={goToJobSummary}>채용 공고 요약</button>
                        <hr />
                        <button className="dropdown-item" onClick={handleMypage}>My Page</button>
                    </div>
                </div>
            </header>

            {/* 기술 스택 상세 정보 */}
            <div className="tech-stack-content">
                {/* 언어 이름 */}
                <h1 className="tech-stack-language">
                    {techStack.techName} {/* API에서 받아온 기술 스택 이름 */}
                </h1>

                {/* 북마크 버튼 */}
                <div className="bookmark-container">
                    <button
                        className={`bookmark-button ${isBookmarked ? "active" : ""}`}
                        onClick={handleBookmark}
                    >
                        {isBookmarked ? "★" : "☆"}
                    </button>
                </div>

                {/* 설명 */}
                <h2>설명</h2>
                <p>{techStack.description}</p>

                {/* 유튜브 링크 */}
                <h2>유튜브 링크</h2>
                {techStack.youtubeLink ? (
                    <a
                        href={techStack.youtubeLink}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        바로가기
                    </a>
                ) : (
                    <p>링크가 없습니다.</p>
                )}

                {/* 도서 링크 */}
                <h2>도서 링크</h2>
                {techStack.bookLink ? (
                    <a
                        href={techStack.bookLink}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        바로가기
                    </a>
                ) : (
                    <p>링크가 없습니다.</p>
                )}

                {/* 공식 문서 */}
                <h2>공식 문서</h2>
                {techStack.docsLink ? (
                    <a
                        href={techStack.docsLink}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
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
