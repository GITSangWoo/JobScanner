import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './LogInPage.css';
import { KAKAO_AUTH_URL } from './KakaoOAuth';
import axios from 'axios';

const LoginPage = () => {
    const navigate = useNavigate();
    // const [jwtToken, setJwtToken] = useState(localStorage.getItem('jwtToken')); // 로컬 스토리지에서 JWT 토큰 불러오기

    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8972';

    const handleRedirect = () => {
        navigate("/", { replace: true });
        window.location.reload(); // 페이지 새로고침
    };

    // JWT 토큰 저장
    // const saveJwtToken = (token) => {
    //     try {
    //         localStorage.setItem('jwtToken', token);
    //         setJwtToken(token); // 상태 업데이트
    //     } catch (error) {
    //         console.error('Error saving JWT token:', error);
    //     }
    // };

    // // 카카오 로그인 후 리디렉션을 처리
    // const getJwtTokenFromUrl = () => {
    //     const urlParams = new URLSearchParams(window.location.search);
    //     const token = urlParams.get('token');
    //     if (token) {
    //         saveJwtToken(token); // 토큰 저장
    //         navigate('/'); // 홈 페이지로 이동
    //     }
    // };

    // // 사용자 데이터 가져오기 (JWT 토큰을 사용하여)
    // const fetchUserData = (token) => {
    //     axios.post(`${BACKEND_URL}/auth/login/kakao`, {}, {  // POST 방식으로 요청
    //         headers: {
    //             'Authorization': `Bearer ${token}`,
    //         }
    //     })
    //     .then(response => {
    //         console.log('User data:', response.data);  // 받은 사용자 데이터 로그 찍기
    //     })
    //     .catch(error => console.error('Error fetching user data:', error));
    // };

    // useEffect(() => {
    //     if (jwtToken) {
    //         console.log("JWT Token exists, no default fetch request.");
    //         fetchUserData(jwtToken); // JWT 토큰을 사용하여 사용자 데이터 요청
    //     } else {
    //         getJwtTokenFromUrl(); // URL에서 JWT 토큰 확인
    //     }

    //     // 카카오 로그인 후 리디렉션을 처리
    //     const code = new URL(window.location.href).searchParams.get("code");
    //     if (code) {
    //         // 백엔드로 `code` 보내기 (POST 요청 사용)
    //         axios.post('/auth/login/kakao', {
    //             code: code,  // 요청 본문에 code 포함
    //         })
    //         .then(response => {
    //             // 응답 받으면 JWT 토큰 저장
    //             console.log("Login successful:", response);
    //             saveJwtToken(response.data.token); // 응답에서 받은 토큰을 저장
    //             navigate("/"); // 로그인 후 홈 페이지로 이동
    //         })
    //         .catch(error => {
    //             console.error("Kakao login failed:", error);
    //         });
    //     }
    // }, [jwtToken, navigate]);

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
