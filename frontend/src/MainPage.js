import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from "chart.js";
import "./MainPage.css";
import axios from "axios"; // axios 임포트

// Chart.js 설정
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const MainPage = () => {
    const [activeButton, setActiveButton] = useState(null); // 활성화된 버튼을 추적하는 상태
    const [sortedData, setSortedData] = useState([]);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false); // 더보기 드롭다운 상태
    const [isLoggedIn, setIsLoggedIn] = useState(false); // 로그인 상태
    const [isTableVisible, setIsTableVisible] = useState(true); // 테이블과 차트 전환을 위한 상태
    const navigate = useNavigate();

    const categories = ["total", "qualification", "preferential"];
    const [categoryData, setCategoryData] = useState({});

    useEffect(() => {
        if (activeButton) {
            // JPA로부터 데이터 받아오기
            categories.forEach(category => {
                axios.get(`/dailyrank?jobtitle=${activeButton}&category=${category}`)
                    .then(response => {
                        const data = response.data.ranks;
                        if (data) {
                            const sorted = data.sort((a, b) => b.count - a.count).slice(0, 7); // count 기준 내림차순 정렬 후 상위 7개 선택
                            const labels = data.map(item => item.techName);
                            const counts = data.map(item => item.count);

                            setSortedData(sorted);

                            setCategoryData(prevData => ({
                                ...prevData,
                                [category]: {
                                    labels,
                                    datasets: [
                                        {
                                            label: `${activeButton} 직무의 ${category} 카테고리 기술 스택 사용 빈도`,
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
    
    const handleClick = () => {
        navigate("/", { replace: true }); // navigate 호출
        window.location.reload();
    };

    const handleButtonClick = (button) => {
        if (activeButton === button) {
            setActiveButton(null); // 같은 버튼을 클릭하면 비활성화
        } else {
            setActiveButton(button); // 새 버튼 클릭 시 해당 버튼 활성화
        }
    };

    const navigateToTechStackDetails = (role, category, techStackName) => {
        // URL 파라미터로 role, category, techStackName 전달
        navigate(`/tech-stack-details/${role}/${category}/${techStackName}`);
    };

    const toggleDropdown = () => {
        setIsDropdownOpen(!isDropdownOpen); // 더보기 버튼 토글
    };

    // 로그인 및 회원가입 페이지로 이동
    const handleLogin = () => {
        navigate("/auth/login");  // 로그인 페이지로 이동
    };

    const handleSignup = () => {
        navigate("/sign-up");  // 회원가입 페이지로 이동
    };

    const goToJobSummary = () => {
        navigate("/job-summary"); // 기업 공고 요약 페이지로 이동
    };

    return (
        <div className="main-page">
            <div className="top-right-buttons">
                <button className="auth-button" onClick={handleLogin}>
                    로그인
                </button>
                <button className="auth-button" onClick={handleSignup}>
                    회원가입
                </button>
            </div>

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

            <div className="logo-container" onClick={handleClick}>
                <h1 className="logo">JobScanner</h1>
            </div>

            <div className="content">
                <p className="message1">직무별 기술 스택 순위 보기</p>
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

                {activeButton && (
                    <div className="tech-stack-content">
                        <h3>{`${activeButton} 직무의 기술 스택 사용 빈도`}</h3>

                        {categories.map(category => (
                            <div key={category} className="tech-stack-category">
                                <h4>{`${category} 카테고리`}</h4>
                                
                                <div className="tech-stack-table">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Role</th>
                                                {sortedData.map((_, index) => (
                                                    <th key={index}>{`Rank ${index + 1}`}</th>
                                                ))}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>{activeButton}</td>
                                                {sortedData.map((item, index) => (
                                                    <td key={index}>
                                                        <button
                                                            className="tech-stack-button"
                                                            onClick={() => navigateToTechStackDetails(activeButton, category, item.techName)}
                                                        >
                                                            {item.techName}
                                                        </button>
                                                    </td>
                                                ))}
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>

                                {categoryData[category] && (
                                    <div className="tech-stack-chart">
                                        <Bar
                                            data={categoryData[category]}
                                            options={{
                                                responsive: true,
                                                plugins: {
                                                    title: {
                                                        display: true,
                                                        text: `${activeButton} 직무의 ${category} 카테고리 기술 스택 사용 빈도`,
                                                    },
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
                                                    },
                                                },
                                            }}
                                        />
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default MainPage;
