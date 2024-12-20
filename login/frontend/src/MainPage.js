import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from "chart.js";
import "./MainPage.css";

// Chart.js 설정
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const MainPage = () => {
    const [activeButton, setActiveButton] = useState(null); // 활성화된 버튼을 추적하는 상태
    const [isDropdownOpen, setIsDropdownOpen] = useState(false); // 더보기 드롭다운 상태
    const navigate = useNavigate();

    const handleClick = () => {
        navigate("/", { replace: true }); // navigate 호출
        window.location.reload();
    };

    const handleMypage = () => {
        navigate("/mypage");
    };

    const handleButtonClick = (button) => {
        if (activeButton === button) {
            setActiveButton(null); // 같은 버튼을 클릭하면 비활성화
        } else {
            setActiveButton(button); // 새 버튼 클릭 시 해당 버튼 활성화
        }
    };

    const navigateToTechStackDetails = (techStackName) => {
        // 기술 스택 이름만 전달
        navigate(`/details/${techStackName}`);
    };

    const navigateToJobSummary = () => {
        navigate("/job-summary"); // 기업 공고 요약 페이지로 이동
    };

    const toggleDropdown = () => {
        setIsDropdownOpen(!isDropdownOpen); // 더보기 버튼 토글
    };

    // 로그인 및 회원가입 페이지로 이동
    const handleLogin = () => {
        navigate("/login");  // 로그인 페이지로 이동
    };

    // const handleSignup = () => {
    //     navigate("/sign-up");  // 회원가입 페이지로 이동
    // };

    // 새로운 데이터셋: 직무별 주요업무, 자격요건, 우대조건
    const jobData = {
        "FE": {
            "desc": "웹을 개발하는 웹 개발 영역 중 사용자가 눈으로 보는 영역을 구축하고, 기능을 구현하는 개발자",
            "주요업무": ["React", "Vue.js", "JavaScript"],
            "자격요건": ["HTML", "CSS", "JavaScript", "React"],
            "우대조건": ["TypeScript", "Webpack", "ESLint"]
        },
        "BE": {
            "desc": "서버, 애플리케이션, 데이터베이스 등 백엔드 시스템을 개발하는 개발자",
            "주요업무": ["Spring Boot", "REST API", "MySQL"],
            "자격요건": ["Java", "Spring Boot", "MySQL", "PostgreSQL"],
            "우대조건": ["Docker", "Kubernetes", "AWS"]
        },
        "DE": {
            "desc": "데이터를 수집하고, 저장 및 처리 시스템을 구축하는 데이터 엔지니어",
            "주요업무": ["ETL", "Hadoop", "Apache Spark"],
            "자격요건": ["Python", "SQL", "NoSQL"],
            "우대조건": ["Airflow", "GCP", "Azure"]
        },
        "DA": {
            "desc": "데이터 분석 및 시각화를 통해 인사이트를 도출하는 데이터 분석가",
            "주요업무": ["Python", "R", "Power BI"],
            "자격요건": ["Python", "R", "SQL"],
            "우대조건": ["Tableau", "Power BI", "SAS"]
        },
        "MLE": {
            "desc": "머신러닝 알고리즘을 활용해 예측 및 모델링을 수행하는 머신러닝 엔지니어",
            "주요업무": ["TensorFlow", "PyTorch", "Scikit-learn"],
            "자격요건": ["Python", "TensorFlow", "PyTorch"],
            "우대조건": ["AWS SageMaker", "GCP AI Platform", "Hadoop"]
        }
    };

    const generateChartData = (role) => {
        const categories = ["주요업무", "자격요건", "우대조건"];
        const roleData = jobData[role];

        // 각 카테고리별 아이템 개수로 사용 빈도를 정의
        const frequencies = categories.map((category) => roleData[category].length);

        return {
            labels: categories, // x축 레이블은 카테고리
            datasets: [
                {
                    label: `${role} 직무의 공고 언급 빈도`,
                    data: frequencies, // y축 데이터는 각 카테고리의 빈도
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                },
            ],
        };
    };

    return (
        <div className="main-page">
            <div className="top-right-buttons">
                <button className="auth-button" onClick={handleLogin}>로그인</button>
                {/*<button className="auth-button" onClick={handleSignup}>회원가입</button>*/}
            </div>

            <div className="top-left-menu">
                <button className="menu-button" onClick={toggleDropdown}>⁝⁝⁝</button>
                <div className={`dropdown-menu ${isDropdownOpen ? "open" : ""}`}>
                    <button className="dropdown-item" onClick={handleClick}>기술 스택 순위</button>
                    <button className="dropdown-item" onClick={navigateToJobSummary}>채용 공고 요약</button>
                    <hr />
                    <button className="dropdown-item" onClick={handleMypage}>My Page</button>
                </div>
            </div>

            <div className="logo-container" onClick={handleClick}>
                <h1 className="logo">JobScanner</h1>
            </div>

            <div className="content">
                <p className="message1">직무별 기술 스택 순위 보기</p>
                <p className="message">원하는 직무를 선택해 주세요</p>
                <div className="toggle-buttons">
                    {Object.keys(jobData).map((role) => (
                        <button
                            key={role}
                            className={`toggle-button ${activeButton === role ? "active" : ""}`}
                            onClick={() => handleButtonClick(role)}
                        >
                            {role}
                        </button>
                    ))}
                </div>

                {activeButton && jobData[activeButton] && (
                    <div className="job-content">
                        <h3>{jobData[activeButton].desc}</h3>

                        <div className="job-table">
                            <table>
                                <thead>
                                <tr>
                                    <th>순위</th>
                                    <th>주요업무</th>
                                    <th>자격요건</th>
                                    <th>우대조건</th>
                                </tr>
                                </thead>
                                <tbody>
                                {jobData[activeButton]["주요업무"].map((item, index) => (
                                    <tr key={index}>
                                        <td>{index + 1}</td>
                                        {/* 순위 */}
                                        <td onClick={() => navigateToTechStackDetails(item)}>{item}</td>
                                        {/* 기술 스택 클릭 시 상세로 이동 */}
                                        <td onClick={() => navigateToTechStackDetails(jobData[activeButton]["자격요건"][index] || "-")}>
                                            {jobData[activeButton]["자격요건"][index] || "-"}
                                        </td>
                                        <td onClick={() => navigateToTechStackDetails(jobData[activeButton]["우대조건"][index] || "-")}>
                                            {jobData[activeButton]["우대조건"][index] || "-"}
                                        </td>
                                    </tr>
                                ))}
                                </tbody>
                            </table>
                        </div>


                        <div className="job-chart">
                            <h4>공고 언급 빈도 차트</h4>
                            <Bar
                                data={generateChartData(activeButton)}
                                options={{
                                    responsive: true,
                                    plugins: {
                                        title: {
                                            display: true,
                                            text: `${activeButton} 직무의 공고 언급 빈도`,
                                        },
                                    },
                                    scales: {
                                        x: {
                                            title: {
                                                display: true,
                                                text: '카테고리',
                                            },
                                        },
                                        y: {
                                            title: {
                                                display: true,
                                                text: '항목 개수',
                                            },
                                            min: 0,
                                        },
                                    },
                                }}
                            />
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MainPage;
