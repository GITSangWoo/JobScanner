import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "./TechStackDetailsPage.css"; // CSS 파일을 import

const TechStackDetailsPage = () => {
    const navigate = useNavigate();
    const [isDropdownOpen, setIsDropdownOpen] = useState(false); // 더보기 드롭다운 상태
    const { role, category, techStackName } = useParams(); // URL에서 role, category, techStackName 받기
    const [techStack, setTechStack] = useState(null);
    const [isBookmarked, setIsBookmarked] = useState(false);
    const [isLoggedIn, setIsLoggedIn] = useState(false); // 로그인 상태 추적

    const handleClick = () => {
        navigate("/", { replace: true }); // navigate 호출
        window.location.reload();
    };

    const toggleDropdown = () => {
        setIsDropdownOpen(!isDropdownOpen); // 더보기 버튼 토글
    };

    const handleLogin = () => {
        navigate("/auth/login");
    };

    const handleSignup = () => {
        navigate("/sign-up");
    };

    const goToJobSummary = () => {
        navigate("/job-summary"); // 기업 공고 요약 페이지로 이동
    };

    useEffect(() => {
        // 기술 스택 정보를 가져오는 로직
        console.log("Fetching tech stack for:", role, category, techStackName);  // 디버깅용 로그
        const techStackData = getTechStackDetails(role, category, techStackName);
        setTechStack(techStackData);
    }, [role, category, techStackName]);

    const handleBookmark = () => {
        if (isLoggedIn) {
            setIsBookmarked(!isBookmarked); // 로그인된 상태에서 북마크 토글
        } else {
            alert("로그인 후 이용하실 수 있습니다..");
            navigate("/auth/login");
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
                    <button className="auth-button" onClick={handleLogin}>
                        로그인
                    </button>
                    <button className="auth-button" onClick={handleSignup}>
                        회원가입
                    </button>
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
                        <button className="dropdown-item">My Page</button>
                    </div>
                </div>
            </header>

            {/* 기술 스택 상세 정보 */}
            <div className="tech-stack-content">
                {/* 언어 이름 */}
                <h1 className="tech-stack-language">
                    {techStack.language}
                </h1>

                {/* 북마크 버튼 - 설명 영역 안으로 이동 */}
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
                <p>
                    {techStack.description || "상세 설명이 없습니다."}
                </p>

                {/* 유튜브 링크 */}
                <h2>유튜브 링크</h2>
                {techStack.youtubeLink ? (
                    <a
                        href={techStack.youtubeLink}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        {techStack.youtubeLink}
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
                        {techStack.bookLink}
                    </a>
                ) : (
                    <p>링크가 없습니다.</p>
                )}

                {/* 공식 문서 */}
                <h2>공식 문서</h2>
                {techStack.documentationLink ? (
                    <a
                        href={techStack.documentationLink}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        {techStack.documentationLink}
                    </a>
                ) : (
                    <p>링크가 없습니다.</p>
                )}
            </div>

        </div>
    );
};

// 기술 스택 세부 정보를 가져오는 함수
const getTechStackDetails = (role, category, techStackName) => {
    // 여기에 모든 기술 스택 데이터 정의
    const techStackData = {
        FE: {
            Language: {
                JavaScript: {
                    language: "JavaScript",
                    description: "JavaScript는 웹 개발에서 많이 사용되는 언어입니다.",
                    youtubeLink: "https://youtu.be/PkZNo7MFNFg?si=QhxbcVEyFrd5vqYT",
                    bookLink: "https://www.yes24.com/Product/Goods/139913428",
                    documentationLink: "https://developer.mozilla.org/ko/docs/Web/JavaScript"
                },
                TypeScript: {
                    language: "TypeScript",
                    description: "TypeScript는 JavaScript의 상위 집합으로, 타입을 추가한 언어입니다.",
                    youtubeLink: "https://youtu.be/k5E2AVpwsko?si=17bLHGGE-U5V5PQ6",
                    bookLink: "https://www.yes24.com/Product/Goods/136740163",
                    documentationLink: "https://www.typescriptlang.org/docs/"
                },
            },
        },
        BE: {
            Language: {
                Java: {
                    language: "Java",
                    description: "Java는 강력한 객체 지향 언어입니다.",
                    youtubeLink: "https://youtu.be/yRpLlJmRo2w?si=Qkn4kSCX5EObmi_U",
                    bookLink: "https://www.yes24.com/Product/Goods/136263729",
                    documentationLink: "https://docs.oracle.com/en/java/"
                },
            },
        },
        DE: {
            Framework: {
                Pandas: {
                    language: "Pandas",
                    description: "Pandas는 데이터 분석을 위한 라이브러리입니다.",
                    youtubeLink: "https://youtu.be/kWiCuklohdY?si=2aT1lFL-Ynh56ln8",
                    bookLink: "https://www.yes24.com/Product/Goods/115330064",
                    documentationLink: "https://pandas.pydata.org/"
                },
            },
        },
    };

    // 해당 role, category, techStackName에 맞는 데이터 반환
    return techStackData[role]?.[category]?.[techStackName] || null;
};

export default TechStackDetailsPage;
