import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./MainPage.css";
import Cookies from 'js-cookie';

const MainPage = () => {
    const [activeButton, setActiveButton] = useState(null);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [jobData, setJobData] = useState({
        responsibility: [],
        qualification: [],
        preferential: [],
    });
    const [jobTitles] = useState(["BE", "FE", "DE", "DA", "MLE"]);
    const navigate = useNavigate();
    const [nickname, setNickname] = useState(""); // 사용자 닉네임 상태

    // useEffect(() => {
    //     // console.log("Updated jobData:", jobData);
    // }, [jobData]);
    
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

    const handleButtonClick = (button) => {
        if (activeButton === button) {
            setActiveButton(null);
            setJobData({ responsibility: [], qualification: [], preferential: [] });
        } else {
            setActiveButton(button);
            fetchDataForAllCategories(button);
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
            </div>
        </div>
    );
};

export default MainPage;
