import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from "chart.js";
import "./MainPage.css";
import Cookies from 'js-cookie';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);


const MainPage = () => {
    const [activeButton, setActiveButton] = useState(null);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [sortedData, setSortedData] = useState([]);
    const [isTableVisible, setIsTableVisible] = useState(true); // 테이블과 차트 전환을 위한 상태   
    const [jobData, setJobData] = useState({
        responsibility: [],
        qualification: [],
        preferential: [],
    });
    const categories = ["total", "qualification", "preferential"];
    const [jobTitles] = useState(["BE", "FE", "DE", "DA", "MLE"]);
    const navigate = useNavigate();
    const [categoryData, setCategoryData] = useState({});
    const [nickname, setNickname] = useState(""); // 사용자 닉네임 상태
    const [jobDescription, setJobDescription] = useState(""); // job description 상태

    // useEffect(() => {
    //     // console.log("Updated jobData:", jobData);
    // }, [jobData]);
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

    const fetchDataForCategory = async (jobtitle, category) => {
        try {
            const response = await axios.get(`/dailyrank?jobtitle=${jobtitle}&category=${category}`);
            return response.data;
        } catch (error) {
            // console.error(`Error fetching ${category} data`, error);
            return null;
        }
    };

    const fetchDataForDescription = async (jobtitle) => {
        try {
            const response = await axios.get(`/jobrole?jobtitle=${jobtitle}`);
            // 서버에서 데이터를 성공적으로 받았다면, 반환
            return response.data;
        } catch (error) {
            console.error('Error fetching job role data:', error);
            // 에러 발생 시 적절한 값을 반환하거나 에러를 다시 던짐
            throw error;
        }
    };

    const fetchDataForAllCategories = async (jobtitle) => {
        const categories = ["responsibility", "qualification", "preferential"];
        const newJobData = {};

        for (const category of categories) {
            const data = await fetchDataForCategory(jobtitle, category);
            newJobData[category] = data?.ranks || [];
        }

        // console.log("Fetched job data for all categories:", newJobData);
        setJobData(newJobData);
    };

    const handleButtonClick = async (button) => {
        if (activeButton === button) {
            // 버튼이 이미 활성화된 경우 상태 초기화
            setActiveButton(null);
            setJobData({ responsibility: [], qualification: [], preferential: [] });
            setJobDescription(""); // JobDescription 초기화
        } else {
            // 새로운 버튼 클릭 시
            setActiveButton(button);
            fetchDataForAllCategories(button);
    
            // JobDescription 가져오기
            try {
                const data = await fetchDataForDescription(button); // API 호출
                if (data) {
                    setJobDescription(data.roleDescription); // 설명 업데이트
                } else {
                    setJobDescription("Failed to fetch job description."); // 실패 시 메시지
                }
            } catch (error) {
                console.error("Error fetching job description:", error);
                setJobDescription("Error fetching job description."); // 에러 시 메시지
            }
        }
    };
    

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
            <div className="top-right-buttons">
                {checkLoginStatus() ? (
                    <span className="welcome-message">{nickname}님 환영합니다!</span>
                ) : (
                    <button className="auth-button" onClick={handleLogin}>
                        로그인
                    </button>
                )}
            </div>

            <div className="top-left-menu">
                <button className="menu-button" onClick={toggleDropdown}>
                    ⁝⁝⁝
                </button>
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

            <div className="logo-container" onClick={handleClick}>
                <h1 className="logo">JobScanner</h1>
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
                    </div>
                )}

                {/* 직무 테이블 */}
                {activeButton && (
                    <div className="job-tables">
                        {["responsibility", "qualification", "preferential"].map((cat) => (
                            <div key={cat} className="main-table-container">
                                <h3>
                                    {cat === "responsibility"
                                        ? "주요업무"
                                        : cat === "qualification"
                                        ? "자격요건"
                                        : "우대조건"}
                                </h3>
                                <table>
                                    <thead>
                                        <tr>
                                            <th>순위</th>
                                            <th>
                                                {cat === "responsibility"
                                                    ? "주요업무"
                                                    : cat === "qualification"
                                                    ? "자격요건"
                                                    : "우대조건"}
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {jobData[cat]?.map((item, index) => (
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
                        ))}
                    </div>
                )}
                {activeButton && categories.map((category) => (
                    <div key={category} className="tech-stack-category">
                        <h4>{`${category} 카테고리`}</h4>
                        {categoryData[category] ? (
                            <div className="tech-stack-chart">
                                <Bar
                                    data={categoryData[category]}
                                    options={{
                                        responsive: true,
                                        plugins: {
                                            title: {
                                                display: true,
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
                        ) : (
                            <p>데이터를 불러오는 중...</p>
                        )}
                    </div>
                ))}

            </div>
        </div>
    );
};

export default MainPage;
