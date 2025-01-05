import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import './MyPage.css';
import Cookies from 'js-cookie';

const MyPage = () => {
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [nickname, setNickname] = useState("");
    const [email, setEmail] = useState("");
    const [techStackBookmarks, setTechStackBookmarks] = useState([]);
    const [noticeBookmarks, setNoticeBookmarks] = useState([]);
    const [activeToggle, setActiveToggle] = useState('tech');
    const [bookmarks, setBookmarks] = useState([]); // 초기 북마크 상태
    const navigate = useNavigate();

    // 로그인 상태 확인 함수
    const checkLoginStatus = () => {
        const accessToken = Cookies.get('access_token');
        return !!accessToken; // 토큰이 있으면 true, 없으면 false
    };

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

    const toggleBookmark = async (item, type) => {
        try {
            let response;
            const token = Cookies.get('access_token');
            
            if (type === 'job') {
                response = await fetch("/user/bookmark/notice", {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: new URLSearchParams({ noticeId: item.noticeid })
                });
            } else if (type === 'tech') {
                response = await fetch("/user/bookmark/tech", {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: new URLSearchParams({ techName: item.tech_name })
                });
            }
    
            if (response.ok) {
                const message = await response.text();
                console.log(message);  // 성공 메시지 출력
                
                // 북마크 삭제 및 추가 로직 수정
                setBookmarks(prevBookmarks => {
                    const isItemBookmarked = type === 'job'
                        ? prevBookmarks.some(bookmark => bookmark.noticeid === item.noticeid)
                        : prevBookmarks.some(bookmark => bookmark.tech_name === item.tech_name);
    
                    if (isItemBookmarked) {
                        // 삭제하려는 북마크가 이미 있을 경우 제거
                        return prevBookmarks.filter(bookmark => 
                            type === 'job' ? bookmark.noticeid !== item.noticeid : bookmark.tech_name !== item.tech_name
                        );
                    } else {
                        // 북마크가 없으면 추가
                        return [...prevBookmarks, item];
                    }
                });
            } else {
                alert("북마크 처리 중 오류가 발생했습니다.");
            }
        } catch (error) {
            console.error("북마크 추가/삭제 오류:", error);
        }
    };

    useEffect(() => {
        // 카카오 SDK 초기화 및 리디렉션 URL 저장
        if (typeof window.Kakao !== 'undefined' && !window.Kakao.isInitialized()) {
            window.Kakao.init('9ae623834d6fbc0413f981285a8fa0d5'); // YOUR_APP_KEY
        }

        // 로그인 요청 이전에 있던 페이지 URL을 sessionStorage에 저장
        const redirectUrl = window.location.pathname;  // 현재 페이지의 경로
        console.log("Storing redirect URL:", redirectUrl);
        sessionStorage.setItem('redirectUrl', redirectUrl);  // 세션 스토리지에 저장
    }, []);
    

    useEffect(() => {
        if (checkLoginStatus()) {
            const fetchUserData = async () => {
                try {
                    const response = await fetch("/user/profile", {
                        headers: {
                            Authorization: `Bearer ${Cookies.get('access_token')}`,
                        },
                    });
    
                    if (response.ok) {
                        const data = await response.json();
                        setNickname(data.name || "사용자");
                        setEmail(data.email || "이메일 없음");
                        setTechStackBookmarks(data.techStackBookmarks || []); // 기술 스택 북마크
                        setNoticeBookmarks(data.noticeBookmarks || []); // 채용 공고 북마크
                        setBookmarks([...data.techStackBookmarks, ...data.noticeBookmarks]); // 북마크 상태 업데이트
                    }
                } catch (error) {
                    console.error("유저 데이터 가져오기 오류:", error);
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
                        <p>Email: {email}</p>
                        <p>Name: {nickname}</p>
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
                            채용 공고
                        </button>
                    </div>

                    {/* 기술 스택 테이블 */}
{/* 기술 스택 테이블 */}
{activeToggle === 'tech' && (
    <div>
        {techStackBookmarks.length === 0 ? (
            <p>저장된 북마크가 없습니다.</p>
        ) : (
            <table>
                <thead>
                    <tr>
                        <th>기술 스택</th>
                        <th>북마크</th>
                    </tr>
                </thead>
                <tbody>
                    {techStackBookmarks.map((tech, index) => (
                        <tr key={index}>
                            <td>
                                <a href={tech.docslink} target="_blank" rel="noopener noreferrer">
                                    {tech.tech_name}
                                </a>
                                <p>{tech.description}</p>
                            </td>
                            <td>
                                <button
                                    onClick={() => toggleBookmark(tech, 'tech')}
                                    className={`mypage-bookmark-button ${
                                        bookmarks.some((bookmark) => bookmark.tech_name === tech.tech_name)
                                            ? 'bookmarked'
                                            : ''
                                    }`}
                                >
                                    {bookmarks.some((bookmark) => bookmark.tech_name === tech.tech_name)
                                        ? '북마크 삭제'
                                        : '북마크 추가'}
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        )}
    </div>
)}

{/* 채용 공고 테이블 */}
{activeToggle === 'job' && (
    <div>
        {noticeBookmarks.length === 0 ? (
            <p>저장된 북마크가 없습니다.</p>
        ) : (
            <table>
                <thead>
                    <tr>
                        <th>회사명</th>
                        <th>공고 제목</th>
                        <th>상세보기</th>
                        <th>북마크</th>
                    </tr>
                </thead>
                <tbody>
                    {noticeBookmarks.map((job) => (
                        <tr key={job.noticeid}>
                            <td>{job.company}</td>
                            <td>
                                <a href={job.orgurl} target="_blank" rel="noopener noreferrer">
                                    {job.posttitle}
                                </a>
                            </td>
                            <td>{job.responsibility}</td>
                            <td>
                                <button
                                    onClick={() => toggleBookmark(job, 'job')}
                                    className={`mypage-bookmark-button ${
                                        bookmarks.some((bookmark) => bookmark.noticeid === job.noticeid)
                                            ? 'bookmarked'
                                            : ''
                                    }`}
                                >
                                    {bookmarks.some((bookmark) => bookmark.noticeid === job.noticeid)
                                        ? '북마크 삭제'
                                        : '북마크 추가'}
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        )}
    </div>
)}

                </div>
            </div>
        </div>
    );
};

export default MyPage;
