import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from "chart.js";
import "./MainPage.css";
import Cookies from 'js-cookie';
import ReactTooltip from 'react-tooltip';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const getCategoryNameInKorean = (category) => {
    const categoryNames = {
        responsibility: "주요업무",
        qualification: "자격요건",
        preferential: "우대조건",
        total: "전체"
    };
    return categoryNames[category] || category;
};

const MainPage = () => {
    const [activeButton, setActiveButton] = useState(null);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [sortedData, setSortedData] = useState([]);
    const [isTableVisible, setIsTableVisible] = useState(true);
    const [jobData, setJobData] = useState({
        responsibility: [],
        qualification: [],
        preferential: [],
        total: []
    });
    const categories = ["total", "responsibility", "qualification", "preferential"];
    const [jobTitles] = useState(["BE", "FE", "DE", "DA", "MLE"]);
    const navigate = useNavigate();
    const [categoryData, setCategoryData] = useState({});
    const [nickname, setNickname] = useState("");
    const [jobDescription, setJobDescription] = useState("");

    useEffect(() => {
        if (typeof window.Kakao !== 'undefined' && !window.Kakao.isInitialized()) {
            window.Kakao.init('9ae623834d6fbc0413f981285a8fa0d5'); // YOUR_APP_KEY
        }

        // 로그인 요청 이전에 있던 페이지 URL을 sessionStorage에 저장
        const redirectUrl = window.location.pathname;  // 현재 페이지의 경로
        console.log("Storing redirect URL:", redirectUrl);
        sessionStorage.setItem('redirectUrl', redirectUrl);  // 세션 스토리지에 저장
    }, []);

    useEffect(() => {
        setActiveButton("BE");
        fetchDataForAllCategories("BE");
        fetchDataForDescription("BE").then(data => {
            if (data) {
                setJobDescription(data.roleDescription);
            } else {
                setJobDescription("Failed to fetch job description.");
            }
        }).catch(error => {
            console.error("Error fetching job description:", error);
            setJobDescription("Error fetching job description.");
        });
    }, []);
    

    useEffect(() => {
        if (activeButton) {
            categories.forEach(category => {
                axios.get(`/dailyrank?jobtitle=${activeButton}&category=${category}`)
                    .then(response => {
                        const data = response.data.ranks;
                        if (data) {
                            const sorted = data.sort((a, b) => b.count - a.count).slice(0, 7);
                            const labels = data.map(item => item.techName);
                            const counts = data.map(item => item.count);

                            setSortedData(sorted);

                            setCategoryData(prevData => ({
                                ...prevData,
                                [category]: {
                                    labels,
                                    datasets: [
                                        {
                                            label: `${activeButton} 직무의 ${getCategoryNameInKorean(category)} 기술 스택 사용 빈도`,
                                            data: counts,
                                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                                            borderColor: 'rgba(75, 192, 192, 1)',
                                            borderWidth: 1,
                                        },
                                    ],
                                }
                            }));
                        }
                    })
                    .catch(error => {
                        console.error("Error fetching data:", error);
                    });
            });
        }
    }, [activeButton]);
    
    // 로그인 상태 확인 함수
    const checkLoginStatus = () => {
        const accessToken = Cookies.get('access_token');
        return !!accessToken; // 토큰이 있으면 true, 없으면 false
    };
    

    // 사용자 정보를 가져오는 함수
    useEffect(() => {
        if (checkLoginStatus()) {
            // 예: API 호출로 사용자 정보를 가져온다고 가정
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

    const fetchDataForCategory = async (jobtitle, category) => {
        try {
            const response = await axios.get(`/dailyrank?jobtitle=${jobtitle}&category=${category}`);
            return response.data;
        } catch (error) {
            return null;
        }
    };

    const fetchDataForDescription = async (jobtitle) => {
        try {
            const response = await axios.get(`http://43.202.186.119:8972/jobrole?jobtitle=${jobtitle}`);
            console.log("API 응답 데이터:", response.data); // 디버깅 코드 추가
            return response.data;
        } catch (error) {
            console.error('Error fetching job role data:', error);
            return null; //수정한거거
        }
    };

    const fetchDataForAllCategories = async (jobtitle) => {
        const categories = ["total", "responsibility", "qualification", "preferential"];
        const newJobData = {};

        for (const category of categories) {
            const data = await fetchDataForCategory(jobtitle, category);
            newJobData[category] = data?.ranks || [];
        }

        setJobData(newJobData);
    };

    const handleButtonClick = async (button) => {
        if (activeButton === button) {
            // 활성화된 버튼 클릭 시 아무 변화 없게 처리
            return;
        }
    
        // 다른 버튼이 클릭되었을 경우 처리
        setActiveButton(button);
        fetchDataForAllCategories(button);
    
        try {
            const data = await fetchDataForDescription(button);
            if (data) {
                setJobDescription(data.roleDescription);
            } else {
                setJobDescription("Failed to fetch job description.");
            }
        } catch (error) {
            console.error("Error fetching job description:", error);
            setJobDescription("Error fetching job description.");
        }
    };

    useEffect(() => {
        console.log("activeButton:", activeButton);
        console.log("jobDescription:", jobDescription);
    }, [activeButton, jobDescription]);

    const handleClick = () => {
        navigate("/", { replace: true });
        window.location.reload();
    };

    const handleMypage = () => {
        if (checkLoginStatus()) {
            navigate("/mypage");
        } else {
            alert("로그인 후 이용하실 수 있습니다.");
            navigate("/login");
        }
    };

    const navigateToTechStackDetails = (techStackName) => {
        navigate(`/details/${techStackName}`);
    };

    const navigateToJobSummary = () => {
        navigate("/job-summary");
    };

    const toggleDropdown = () => {
        setIsDropdownOpen(!isDropdownOpen);
    };

    const handleLogin = () => {
        navigate("/login");
    };

    return (
        <div className="main-page">
            <div className="top-left-menu">
                <button className="menu-button" onClick={toggleDropdown}>
                    ⁝⁝⁝
                </button>
                <span className="header-logo">JobScanner</span>
                <div className={`dropdown-menu ${isDropdownOpen ? "open" : ""}`}>
                    <button className="dropdown-item" onClick={handleClick}>
                        기술 스택 순위
                    </button>
                    <button className="dropdown-item" onClick={navigateToJobSummary}>
                        채용 공고 요약
                    </button>
                    <hr />
                    <button className="dropdown-item" onClick={handleMypage}>
                        My Page
                    </button>
                </div>
            </div>
            <div className="header-right">
                <div className="top-right-buttons">
                    {checkLoginStatus() ? (
                        <span className="welcome-message">{nickname}님 환영합니다!</span>
                    ) : (
                        <button className="auth-button" onClick={handleLogin}>
                            로그인
                        </button>
                    )}
                </div>
            </div>
            <hr className="header-divider" />
            <div className="logo-container-large">
                <h1 className="logo-large">JobScanner</h1>
            </div>
            <div className="content">
                <p className="message1">직무별 기술 스택 순위 보기</p>
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

                {/* 직무 설명 */}
                {activeButton && jobDescription && (
                    <div className="job-description">
                        <h3>직무 설명</h3>
                        <p>{jobDescription}</p>
                        <span data-tip="각 기술 스택을 클릭하면 기술스택 설명상세 페이지로 넘어갑니다" className="info-icon">ℹ️</span>
                        <ReactTooltip place="top" type="dark" effect="solid"/>
                    </div>
                )}

                {/* 직무 테이블 및 차트 */}
                {activeButton && categories.map((category) => (
                    <div key={category} className="category-section">
                        <div className="main-table-container">
                            <h3>{getCategoryNameInKorean(category)}</h3>
                            <table className="main-table">
                                <thead className="main-table">
                                    <tr>
                                        <th>순위</th>
                                        <th>{getCategoryNameInKorean(category)}</th>
                                    </tr>
                                </thead>
                                <tbody className="main-table">
                                    {jobData[category]?.map((item, index) => (
                                        <tr key={index}>
                                            <td>{index + 1}</td>
                                            <td onClick={() => navigateToTechStackDetails(item.techName)}>
                                                {item.techName}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        <div className="tech-stack-chart">
                            {categoryData[category] ? (
                                <Bar
                                    data={categoryData[category]}
                                    options={{
                                        responsive: true,
                                        plugins: {
                                            title: {
                                                display: true,
                                            },
                                            legend: {
                                                onClick: (e) => e.stopPropagation()
                                            }
                                        },
                                        scales: {
                                            x: {
                                                title: {
                                                    display: true,
                                                    text: 'Tech Stack',
                                                },
                                            },
                                            y: {
                                                title: {
                                                    display: true,
                                                    text: 'Count',
                                                },
                                                min: 0,
                                                ticks: {
                                                    callback: function(value) {
                                                        if (Number.isInteger(value)) {
                                                            return value;
                                                        }
                                                    }
                                                }
                                            },
                                        },
                                    }}
                                />
                            ) : (
                                <p>데이터를 불러오는 중...</p>
                            )}
                        </div>
                    </div>
                ))}

            </div>
        </div>
    );
};

export default MainPage;
