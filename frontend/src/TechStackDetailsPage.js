import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "./TechStackDetailsPage.css"; // CSS 파일을 import
import axios from "axios"; // axios 임포트

const PROXY_URL = "http://localhost:9000/";

const fetchLinkPreview = async (url) => {
    try {
        const response = await axios.get(`${PROXY_URL}${url}`);
        return response.data;
    } catch (error) {
        console.error("Error fetching link preview:", error);
        throw error;
    }
};

const TechStackDetailsPage = () => {
    const navigate = useNavigate();
    const [isDropdownOpen, setIsDropdownOpen] = useState(false); // 더보기 드롭다운 상태
    const { techStackName } = useParams(); // URL에서 techStackName 받기
    const [techStack, setTechStack] = useState(null);
    const [isBookmarked, setIsBookmarked] = useState(false);
    const [isLoggedIn, setIsLoggedIn] = useState(false); // 로그인 상태 추적
    const [linkPreviews, setLinkPreviews] = useState({}); // 링크 미리보기 상태

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
        axios.get(`/techstack?techName=${techStackName}`)
            .then(response => {
                console.log(response.data); // 응답 데이터 확인
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
                        fetchLinkPreview(link)
                            .then(data => {
                                console.log(data); // 링크 미리보기 데이터 확인
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

    useEffect(() => {
        console.log(linkPreviews); // 상태 업데이트 확인
    }, [linkPreviews]);

    const handleBookmark = () => {
        if (isLoggedIn) {
            setIsBookmarked(!isBookmarked); // 로그인된 상태에서 북마크 토글
        } else {
            alert("로그인 후 이용하실 수 있습니다.");
            navigate("/auth/login");
        }
    };

    if (!techStack) {
        return <p>해당 기술 스택 정보를 찾을 수 없습니다.</p>;
    }

    const renderLinkPreview = (link) => {
        const preview = linkPreviews[link];
        if (!preview) return null;

        return (
            <div className="link-preview-card" key={link}>
                <a href={link} target="_blank" rel="noopener noreferrer">
                    <div className="link-preview-thumbnail">
                        <img src={preview.images[0]} alt="Preview" />
                    </div>
                    <div className="link-preview-content">
                        <h3>{preview.title}</h3>
                        <p>{preview.description}</p>
                    </div>
                </a>
            </div>
        );
    };

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
                    {techStack.techName}
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
                    renderLinkPreview(techStack.youtubeLink)
                ) : (
                    <p>링크가 없습니다.</p>
                )}

                {/* 도서 링크 */}
                <h2>도서 링크</h2>
                {techStack.bookLink ? (
                    renderLinkPreview(techStack.bookLink)
                ) : (
                    <p>링크가 없습니다.</p>
                )}

                {/* 공식 문서 */}
                <h2>공식 문서</h2>
                {techStack.documentationLink ? (
                    renderLinkPreview(techStack.documentationLink)
                ) : (
                    <p>링크가 없습니다.</p>
                )}
            </div>
        </div>
    );
};

export default TechStackDetailsPage;
