import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import './MyPage.css';
import Cookies from 'js-cookie';

const MyPage = () => {
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [nickname, setNickname] = useState("");
    const [activeToggle, setActiveToggle] = useState('tech');
    const [bookmarks, setBookmarks] = useState([]); // 초기 북마크 상태
    const [techStackData, setTechStackData] = useState([]); // 기술 스택 상태
    const [jobSummaryData, setJobSummaryData] = useState([]); // 공고 요약 상태
    const navigate = useNavigate();

    // 로그인 상태 확인 함수
    const checkLoginStatus = () => {
        const accessToken = Cookies.get('access_token');
        return !!accessToken; // 토큰이 있으면 true, 없으면 false
    };

    useEffect(() => {
        // 초기 데이터 로드 및 북마크 초기화
        const initialTechStackData = ['React'];
        const initialJobSummaryData = [
            {
                id: 1,
                deadline: '2024-12-31',
                company: 'Company A',
                title: 'Software Engineer',
                tasks: 'Develop features',
                requirements: 'Java, Spring',
                preferences: 'React, Docker',
                techStack: ['Java', 'Spring', 'React']
            },
            // {
            //     id: 2,
            //     deadline: '2024-12-15',
            //     company: 'Company B',
            //     title: 'Backend Developer',
            //     tasks: 'Develop backend services',
            //     requirements: 'Node.js, MongoDB',
            //     preferences: 'Docker, Kubernetes',
            //     techStack: ['Node.js', 'MongoDB', 'Docker']
            // }
        ];

        setTechStackData(initialTechStackData);
        setJobSummaryData(initialJobSummaryData);

        // 예시로 기본적으로 몇 개의 항목을 북마크에 추가
        setBookmarks(['React', 1]); // 'React'와 id=1인 공고를 초기 북마크로 설정
    }, []);

    const handleClick = () => {
        navigate("/", { replace: true });
        window.location.reload();
    };

    const toggleDropdown = () => {
        setIsDropdownOpen(!isDropdownOpen);
    };

    const goToJobSummary = () => {
        navigate("/job-summary");
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

    const toggleTab = (tab) => {
        setActiveToggle(tab);
    };

    const toggleBookmark = (item) => {
        setBookmarks(prevBookmarks => {
            if (prevBookmarks.includes(item)) {
                // 북마크가 이미 존재하면 삭제
                return prevBookmarks.filter(bookmark => bookmark !== item);
            } else {
                // 북마크가 없으면 추가
                return [...prevBookmarks, item];
            }
        });

        // 데이터 동기화: 북마크 삭제 시 상태에서 데이터도 제거
        if (typeof item === "string") {
            setTechStackData(prevData => prevData.filter(tech => tech !== item));
        } else if (typeof item === "number") {
            setJobSummaryData(prevData => prevData.filter(job => job.id !== item));
        }
    };

    // 사용자 정보를 가져오는 함수
    useEffect(() => {
        if (checkLoginStatus()) {
            // 예: API 호출로 사용자 정보를 가져온다고 가정
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
    

    return (
        <div className="my-page">
            <div className="top-right-buttons">
                {checkLoginStatus() ? (
                    <span className="welcome-message">{nickname}님 환영합니다!</span>
                ) : (
                    <button className="auth-button" onClick={() => navigate("/login")}>
                        로그인
                    </button>
                )}
            </div>

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

            <div className="logo-container" onClick={handleClick}>
                <h1 className="logo">JobScanner</h1>
            </div>

            <div className="user-info">
                <div className="social-login-info">
                    <div className="social-login-info-box">
                        소셜 로그인 계정 정보가 들어갈 예정
                    </div>
                </div>

                <div className="bookmark-list">
                    <h3>북마크 목록</h3>
                    <div className="bookmark-toggle-buttons">
                        <button
                            className={`bookmark-toggle-button ${activeToggle === 'tech' ? 'active' : ''}`}
                            onClick={() => toggleTab('tech')}
                        >
                            기술 스택
                        </button>
                        <button
                            className={`bookmark-toggle-button ${activeToggle === 'job' ? 'active' : ''}`}
                            onClick={() => toggleTab('job')}
                        >
                            공고 요약
                        </button>
                    </div>

                    {/* 기술 스택 테이블 */}
                    {activeToggle === 'tech' && (
                        <table>
                            <thead>
                            <tr>
                                <th>기술 스택</th>
                                <th>북마크</th>
                            </tr>
                            </thead>
                            <tbody>
                            {techStackData.map((tech, index) => (
                                <tr key={index}>
                                    <td>{tech}</td>
                                    <td>
                                        <button
                                            onClick={() => toggleBookmark(tech)}
                                            className={`mypage-bookmark-button ${bookmarks.includes(tech) ? 'bookmarked' : ''}`}
                                        >
                                            {bookmarks.includes(tech) ? '북마크 삭제' : '북마크 추가'}
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    )}

                    {/* 공고 요약 테이블 */}
                    {activeToggle === 'job' && (
                        <table>
                            <thead>
                            <tr>
                                <th>마감일</th>
                                <th>회사명</th>
                                <th>공고 제목</th>
                                <th>주요 업무</th>
                                <th>자격 요건</th>
                                <th>우대 조건</th>
                                <th>기술 스택</th>
                                <th>북마크</th>
                            </tr>
                            </thead>
                            <tbody>
                            {jobSummaryData.map((job) => (
                                <tr key={job.id}>
                                    <td>{job.deadline}</td>
                                    <td>{job.company}</td>
                                    <td>{job.title}</td>
                                    <td>{job.tasks}</td>
                                    <td>{job.requirements}</td>
                                    <td>{job.preferences}</td>
                                    <td>{job.techStack.join(', ')}</td>
                                    <td>
                                        <button
                                            onClick={() => toggleBookmark(job.id)} // job.id는 공고의 고유 id
                                            className={`mypage-bookmark-button ${bookmarks.includes(job.id) ? 'bookmarked' : ''}`}
                                        >
                                            {bookmarks.includes(job.id) ? '북마크 삭제' : '북마크 추가'}
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MyPage;
