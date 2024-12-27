import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './LogInPage.css';
import { KAKAO_AUTH_URL } from './KakaoOAuth';
import axios from 'axios';
import { handleLoginSuccess } from './auth'; // auth.js에서 함수 가져오기

const LoginPage = () => {
    const navigate = useNavigate();
    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8972';

    const handleRedirect = () => {
        navigate("/", { replace: true });
        window.location.reload(); // 페이지 새로고침
    };

    useEffect(() => {
        // URL에서 인가 코드 확인
        const code = new URL(window.location.href).searchParams.get("code");
        if (code) {
            // 백엔드로 인가 코드 전달하여 Access Token 받기
            axios
                .post(`${BACKEND_URL}/auth/login/kakao`, { code }) // 인가 코드를 요청 본문에 포함
                .then(response => {
                    const { accessToken } = response.data; // 백엔드에서 반환한 Access Token
                    console.log("Access Token:", accessToken);

                    // Access Token을 쿠키에 저장
                    handleLoginSuccess(accessToken);

                    // 사용자 데이터를 가져오거나 추가 작업 수행
                    fetchUserData(accessToken);

                    // 홈 페이지로 리디렉션
                    navigate("/");
                })
                .catch(error => {
                    console.error("Kakao login failed:", error);
                });
        }
    }, [navigate, BACKEND_URL]);

    // 사용자 데이터를 가져오는 함수
    const fetchUserData = (accessToken) => {
        axios
            .get(`${BACKEND_URL}/user/me`, {
                headers: { Authorization: `Bearer ${accessToken}` },
            })
            .then(response => {
                console.log("User data:", response.data); // 사용자 데이터 출력
            })
            .catch(error => console.error("Error fetching user data:", error));
    };

    return (
        <div className="main-page">
            <div className="logo-container">
                <div className="logo" onClick={handleRedirect}>JobScanner</div>
            </div>
            <h1>로그인</h1>
            <div className="login-container">
                <div className="login-buttons">
                    <React.Fragment>
                        <button
                            onClick={() => {
                                window.location.href = KAKAO_AUTH_URL;
                            }}
                            style={{ border: "none", background: "none", padding: 0 }}
                        >
                            <img src="/image/kakao.png" alt="Kakao Login" style={{ width: "200px", height: "auto" }} />
                        </button>
                    </React.Fragment>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
