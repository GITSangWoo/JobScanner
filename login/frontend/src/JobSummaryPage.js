import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./JobSummaryPage.css";

const JobSummaryPage = () => {
    const [activeButton, setActiveButton] = useState(null);
    const [isBookmarked, setIsBookmarked] = useState(false);
    const [isLoggedIn, setIsLoggedIn] = useState(false); // 로그인 상태 추적
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const navigate = useNavigate();
    const [nickname, setNickname] = useState("Esther");

    // 페이지 이동을 처리하는 함수
    const handleClick = () => {
        navigate("/", { replace: true });
        window.location.reload();
    };

    const goToJobSummary = () => {
        navigate("/job-summary"); // 기업 공고 요약 페이지로 이동
        window.location.reload();
    };

    // 로그인 및 회원가입 페이지로 이동
    const handleLogin = () => {
        navigate("/login");  // 로그인 페이지로 이동
    };

    // const handleSignup = () => {
    //     navigate("/sign-up");  // 회원가입 페이지로 이동
    // };

    // 줄바꿈 처리 함수
    const formatTextWithLineBreaks = (text) => {
        // \n을 <br />로 변환한 후 배열로 반환
        return text.split("\n").map((line, index) => (
            <React.Fragment key={index}>
                {line}
                <br />
            </React.Fragment>
        ));
    };



    // 각 직무에 따른 채용 공고 데이터
    const jobDataByRole = {
        FE: [
            {
                id: 1,
                deadline: "2024-12-31",
                companyName: "ABC Corp",
                jobTitle: "Frontend Developer",
                mainTask: "- React 기반 웹 개발\n - 전반적인 프론트엔드 업무\n - 백엔드 팀과의 협업",
                qualifications: "- 2년 이상 경험",
                preferences: "- TypeScript 경험 우대",
                techStack: "- React\n- TypeScript\n- Redux",
            },
        ],
        BE: [
            {
                id: 2,
                deadline: "2025-01-15",
                companyName: "XYZ Ltd",
                jobTitle: "Backend Developer",
                mainTask: "Spring Boot API 설계",
                qualifications: "- 3년 이상 경험\n - Java, Spring Boot에 능숙하신 분",
                preferences: "- Docker 경험 우대\n- 석사 이상",
                techStack: "- Java\n- Spring Boot\n- Docker",
            },
        ],
        DE: [
            {
                id: 3,
                deadline: "상시",
                companyName: "samdul",
                jobTitle: "Data Engineer",
                mainTask: "파이프라인 설계",
                qualifications: "- 3년 이상 경험\n - Python, Pandas에 능숙하신 분",
                preferences: "- Kubernetes 경험 우대",
                techStack: "- Python\n- Pandas\n- Kubernetes",
            },
        ],
        DA: [
            {
                id: 4,
                deadline: "상시",
                companyName: "Samdul",
                jobTitle: "Data Analytics",
                mainTask: "데이터 분석",
                qualifications: "- 3년 이상 경험\n - Tableau에 능숙하신 분",
                preferences: "- Docker 경험 우대",
                techStack: "- Tableau\n- Docker",
            },
        ],
        MLE: [
            {
                id: 5,
                deadline: "2025-01-15",
                companyName: "Samdul",
                jobTitle: "Machine Learning Engineer",
                mainTask: "- 머신러닝 모델 설계 및 제작",
                qualifications: "- 3년 이상 경험\n - HuggingFace 써보신 분\n - 모델을 직접 만들어보신 분",
                preferences: "- Docker 경험 우대",
                techStack: "- HuggingFace\n- Docker",
            },
        ],
    };

    // 직무 버튼 클릭 시 활성화 처리
    const handleButtonClick = (button) => {
        setActiveButton((prev) => (prev === button ? null : button));
    };

    // 드롭다운 메뉴 열기/닫기 처리
    const toggleDropdown = () => {
        setIsDropdownOpen((prev) => !prev);
    };

    // 북마크 토글 처리
    const handleBookmark = (id) => {
        if (isLoggedIn) {
            setIsBookmarked(!isBookmarked); // 로그인된 상태에서 북마크 토글
        } else {
            alert("로그인 후 이용하실 수 있습니다..");
            navigate("/login");
        }
    };

    const handleMypage = () => {
        if (isLoggedIn) {
            navigate("/mypage"); // 로그인된 상태에서는 마이 페이지로 이동
        } else {
            alert("로그인 후 이용하실 수 있습니다.");
            navigate("/login"); // 로그인되지 않은 상태에서 클릭 시 로그인 페이지로 이동
        }
    };

    return (
        <div className="job-summary-page">
            <div className="top-right-buttons">
                {isLoggedIn ? (
                    <span className="welcome-message">{nickname}님 환영합니다!</span>
                ) : (
                    <>
                        <button className="auth-button" onClick={() => navigate("/auth/login")}>
                            로그인
                        </button>
                        {/*<button className="auth-button" onClick={() => navigate("/sign-up")}>*/}
                        {/*    회원가입*/}
                        {/*</button>*/}
                    </>
                )}
            </div>

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
                        <hr/>
                        <button className="dropdown-item" onClick={handleMypage}>My Page</button>
                    </div>
                )}
            </div>

            <div className="logo-container">
                <h1 className="logo" onClick={handleClick}>
                    JobScanner
                </h1>
            </div>

            <div className="content">
                <p className="message1">직무별 채용 공고 보기</p>
                <p className="message">원하는 직무를 선택해 주세요</p>
                <div className="toggle-buttons">
                    {["FE", "BE", "DE", "DA", "MLE"].map((role) => (
                        <button
                            key={role}
                            className={`toggle-button ${activeButton === role ? "active" : ""}`}
                            onClick={() => handleButtonClick(role)}
                        >
                            {role}
                        </button>
                    ))}
                </div>
            </div>

            {activeButton && jobDataByRole[activeButton].length > 0 && (
                <div className="table-container">
                    <table>
                        <thead>
                        <tr>
                            <th>마감일</th>
                            <th>회사 이름</th>
                            <th>공고 제목</th>
                            <th>주요 업무</th>
                            <th>자격 요건</th>
                            <th>우대 사항</th>
                            <th>기술 스택 목록</th>
                            <th>북마크</th>
                        </tr>
                        </thead>
                        <tbody>
                        {jobDataByRole[activeButton].map((job) => (
                            <tr key={job.id}>
                                <td>{job.deadline}</td>
                                <td>{job.companyName}</td>
                                <td>{job.jobTitle}</td>
                                <td className="pre-line">{formatTextWithLineBreaks(job.mainTask)}</td>
                                <td className="pre-line">{formatTextWithLineBreaks(job.qualifications)}</td>
                                <td className="pre-line">{formatTextWithLineBreaks(job.preferences)}</td>
                                <td className="pre-line">{formatTextWithLineBreaks(job.techStack)}</td>
                                <td>
                                        <span
                                            className={`bookmark-button ${isBookmarked ? "active" : ""}`}
                                            onClick={handleBookmark}
                                        >
                                            {isBookmarked ? "★" : "☆"}
                                        </span>
                                </td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default JobSummaryPage;
