import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./JobSummaryPage.css";

const JobSummaryPage = () => {
    const [activeButton, setActiveButton] = useState(null);
    const [jobData, setJobData] = useState([]); // 채용 공고 데이터를 저장할 상태
    const [isBookmarked, setIsBookmarked] = useState(false);
    const [isLoggedIn, setIsLoggedIn] = useState(false); // 로그인 상태 추적
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const navigate = useNavigate();
    const [currentPage, setCurrentPage] = useState(1); // 현재 페이지 상태
    const [itemsPerPage] = useState(20); // 한 페이지에 표시할 항목 수
    const [jobTitles] = useState(["BE", "FE", "DE", "DA", "MLE"]);
    const [nickname, setNickname] = useState("Esther");

    // 현재 페이지에 해당하는 데이터만 추출
    const indexOfLastJob = currentPage * itemsPerPage;
    const indexOfFirstJob = indexOfLastJob - itemsPerPage;
    const currentJobs = jobData.slice(indexOfFirstJob, indexOfLastJob);

    // 페이지 변경 처리 함수
    const paginate = (pageNumber) => setCurrentPage(pageNumber);

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

    // 직무 버튼 클릭 시 활성화 처리
    const handleButtonClick = (role) => {
        setActiveButton((prev) => (prev === role ? null : role));
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

    const fetchJobData = async (role) => {
        try {
            const response = await fetch(`/notice?jobtitle=${role}`);
            const data = await response.json();
            if (response.ok) {
                // 데이터 구조를 채용 공고에 맞게 변환
                const transformedData = data.map((job) => ({
                    id: job.notice_id,
                    deadline: job.duetype === "날짜" ? job.duedate : "상시채용", // 마감일 처리
                    companyName: job.company,
                    jobTitle: job.posttitle,
                    mainTask: job.responsibility || "상세 미제공", // 책임이 없으면 기본값 설정
                    qualifications: job.qualification || "상세 미제공", // 자격 요건이 없으면 기본값 설정
                    preferences: job.preferential || "상세 미제공", // 우대 사항이 없으면 기본값 설정
                    techStack: job.tottech || "기술 스택 미제공", // 기술 스택이 없으면 기본값 설정
                }));
                setJobData(transformedData); // 변환된 데이터를 상태에 저장
            } else {
                console.error("Error fetching job data:", data);
                setJobData([]);
            }
        } catch (error) {
            console.error("Error fetching job data:", error);
            setJobData([]);
        }
    };

    // 직무가 선택되었을 때 공고 데이터를 가져오기
    useEffect(() => {
        if (activeButton) {
            fetchJobData(activeButton);
        }
    }, [activeButton]);

    // 페이지네이션 버튼 생성
    const pageNumbers = [];
    const totalPages = Math.ceil(jobData.length / itemsPerPage);

    for (let i = 1; i <= totalPages; i++) {
        pageNumbers.push(i);
    }

    // 10페이지 단위로 끊어서 표시
    const paginateRangeStart = Math.floor((currentPage - 1) / 10) * 10 + 1;
    const paginateRangeEnd = Math.min(paginateRangeStart + 9, totalPages);

    const visiblePageNumbers = pageNumbers.slice(paginateRangeStart - 1, paginateRangeEnd);

    return (
        <div className="job-summary-page">
            <div className="top-right-buttons">
                {isLoggedIn ? (
                    <span className="welcome-message">{nickname}님 환영합니다!</span>
                ) : (
                    <button className="auth-button" onClick={() => navigate("/auth/login")}>
                        로그인
                    </button>
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
                        <hr />
                        <button className="dropdown-item" onClick={handleMypage}>
                            My Page
                        </button>
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
                    {jobTitles.map((role) => (
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

            {activeButton && jobData.length > 0 && (
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
                            {currentJobs.map((job) => (
                                <tr key={job.id}>
                                    <td>{job.deadline}</td>
                                    <td>{job.companyName}</td>
                                    <td>{job.jobTitle}</td>
                                    <td className="pre-line">{job.mainTask}</td>
                                    <td className="pre-line">{job.qualifications}</td>
                                    <td className="pre-line">{job.preferences}</td>
                                    <td className="pre-line">{job.techStack}</td>
                                    <td>
                                        <span
                                            className={`bookmark-button ${isBookmarked ? "active" : ""}`}
                                            onClick={() => handleBookmark(job.id)}
                                        >
                                            {isBookmarked ? "★" : "☆"}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    <div className="pagination">
                        <button
                            onClick={() => paginate(1)}
                            className="page-button"
                            disabled={currentPage === 1}
                        >
                            &laquo;
                        </button>
                        <button
                            onClick={() => paginate(Math.max(currentPage - 1, 1))}
                            className="page-button"
                            disabled={currentPage === 1}
                        >
                            &lt;
                        </button>
                        {visiblePageNumbers.map((number) => (
                            <button
                                key={number}
                                onClick={() => paginate(number)}
                                className={`page-button ${currentPage === number ? "active" : ""}`}
                            >
                                {number}
                            </button>
                        ))}
                        <button
                            onClick={() => paginate(Math.min(currentPage + 1, totalPages))}
                            className="page-button"
                            disabled={currentPage === totalPages}
                        >
                            &gt;
                        </button>
                        <button
                            onClick={() => paginate(totalPages)}
                            className="page-button"
                            disabled={currentPage === totalPages}
                        >
                            &raquo;
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default JobSummaryPage;
