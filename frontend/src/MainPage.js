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
    const [isLoggedIn, setIsLoggedIn] = useState(false); // 로그인 상태
    const [isTableVisible, setIsTableVisible] = useState(true); // 테이블과 차트 전환을 위한 상태
    const navigate = useNavigate();

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

    const handleLogin = () => {
        alert("로그인 화면으로 이동합니다.");
    };

    const handleSignup = () => {
        alert("회원가입 화면으로 이동합니다.");
    };

    const goToJobSummary = () => {
        navigate("/job-summary"); // 기업 공고 요약 페이지로 이동
    };

    const techStackData = {
        "FE": {
            "desc": "웹을 개발하는 웹 개발 영역 중 사용자가 눈으로 보는 영역을 구축하고, 기능을 구현하는 개발자",
            "Language": [
                "JavaScript",
                "TypeScript",
                "Python"
            ],
            "Framework": [
                "React",
                "Vue.js",
                "Angular"
            ],
            "Tools": [
                "Webpack",
                "Babel",
                "Git"
            ],
            "Database": [
                "MongoDB",
                "PostgreSQL",
                "MySQL"
            ]
        },
        "BE": {
            "desc": "서버, 애플리케이션, 데이터베이스 등 백엔드 시스템을 개발하는 개발자",
            "Language": [
                "Java",
                "Python",
                "JavaScript"
            ],
            "Framework": [
                "Spring Boot",
                "Django",
                "Node.js"
            ],
            "Tools": [
                "Maven",
                "PyCharm",
                "Nodemon"
            ],
            "Database": [
                "Oracle",
                "MySQL",
                "MongoDB"
            ]
        },
        "DE": {
            "desc": "데이터를 분석하고, 예측 모델을 구축하는 데이터 엔지니어",
            "Language": [
                "Python",
                "R",
                "SQL"
            ],
            "Framework": [
                "Pandas",
                "Shiny",
                "Apache Spark"
            ],
            "Tools": [
                "Jupyter",
                "RStudio",
                "Tableau"
            ],
            "Database": [
                "Hadoop",
                "PostgreSQL",
                "MySQL"
            ]
        },
        "DA": {
            "desc": "데이터 분석 및 시각화를 통해 인사이트를 도출하는 데이터 분석가",
            "Language": [
                "Python",
                "R",
                "SQL"
            ],
            "Framework": [
                "Pandas",
                "Shiny",
                "Apache Spark"
            ],
            "Tools": [
                "Jupyter",
                "RStudio",
                "Tableau"
            ],
            "Database": [
                "PostgreSQL",
                "MySQL",
                "Oracle"
            ]
        },
        "MLE": {
            "desc": "머신러닝 알고리즘을 활용해 예측 및 모델링을 수행하는 머신러닝 엔지니어",
            "Language": [
                "Python",
                "R",
                "Java"
            ],
            "Framework": [
                "TensorFlow",
                "caret",
                "Deeplearning4j"
            ],
            "Tools": [
                "Jupyter",
                "RStudio",
                "Eclipse"
            ],
            "Database": [
                "Hadoop",
                "PostgreSQL",
                "MySQL"
            ]
        }
    };

    const generateChartData = (role) => {
        const techStack = techStackData[role];
        const languages = techStack.Language;

        // 예시로 랜덤 사용 빈도를 생성
        const usageFrequencies = languages.map(() => Math.floor(Math.random() * 100));

        return {
            labels: languages, // x축 레이블은 기술 스택 항목
            datasets: [
                {
                    label: `${role} 직무의 기술 스택 사용 빈도`,
                    data: usageFrequencies, // y축 데이터는 각 기술의 사용 빈도
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

                {activeButton && techStackData[activeButton] && (
                    <div className="tech-stack-content">
                        <h3>{techStackData[activeButton].desc}</h3>

                        <div className="tech-stack-table">
                            <table>
                                <thead>
                                <tr>
                                    <th>Language</th>
                                    <th>Framework</th>
                                    <th>Tools</th>
                                    <th>Database</th>
                                </tr>
                                </thead>
                                <tbody>
                                {techStackData[activeButton] && (
                                    <>
                                        {techStackData[activeButton].Language.map((item, index) => (
                                            <tr key={index}>
                                                <td>
                                                    <button
                                                        className="tech-stack-button"
                                                        onClick={() => navigateToTechStackDetails(activeButton, 'Language', item)}
                                                    >
                                                        {item}
                                                    </button>
                                                </td>
                                                <td>
                                                    <button
                                                        className="tech-stack-button"
                                                        onClick={() => navigateToTechStackDetails(activeButton, 'Framework', techStackData[activeButton].Framework[index])}
                                                    >
                                                        {techStackData[activeButton].Framework[index]}
                                                    </button>
                                                </td>
                                                <td>
                                                    <button
                                                        className="tech-stack-button"
                                                        onClick={() => navigateToTechStackDetails(activeButton, 'Tools', techStackData[activeButton].Tools[index])}
                                                    >
                                                        {techStackData[activeButton].Tools[index]}
                                                    </button>
                                                </td>
                                                <td>
                                                    <button
                                                        className="tech-stack-button"
                                                        onClick={() => navigateToTechStackDetails(activeButton, 'Database', techStackData[activeButton].Database[index])}
                                                    >
                                                        {techStackData[activeButton].Database[index]}
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </>
                                )}
                                </tbody>
                            </table>
                        </div>


                        <div className="tech-stack-chart">
                            <h4>기술 스택 순위 차트</h4>
                            <Bar
                                data={generateChartData(activeButton)}
                                options={{
                                    responsive: true,
                                    plugins: {
                                        title: {
                                            display: true,
                                            text: `${activeButton} 직무의 기술 스택 사용 빈도`,
                                        },
                                    },
                                    scales: {
                                        x: {
                                            title: {
                                                display: true,
                                                text: 'Language',
                                            },
                                        },
                                        y: {
                                            title: {
                                                display: true,
                                                text: 'Usage Frequency (%)',
                                            },
                                            min: 0,
                                            max: 100, // 최대값 100으로 설정
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
