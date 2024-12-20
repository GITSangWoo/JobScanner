import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleLogin } from "@react-oauth/google";
import { GoogleOAuthProvider } from "@react-oauth/google";
import KakaoLogin from "react-kakao-login";
import './LogInPage.css';

const LoginPage = () => {
    const navigate = useNavigate();
    const [jwtToken, setJwtToken] = useState(localStorage.getItem('jwtToken')); // 로컬 스토리지에서 JWT 토큰 불러오기

    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8972';

    const handleRedirect = () => {
        navigate("/", { replace: true });
        window.location.reload(); // 페이지 새로고침
    };

    // 로그인 후 사용자 데이터 가져오기
    const fetchUserData = (token, provider) => {
        fetch(`${BACKEND_URL}/auth/login/${provider}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch user data');
                }
                return response.json();
            })
            .then(data => {
                console.log('User data:', data);
            })
            .catch(error => console.error('Error fetching user data:', error));
    };

    // JWT 토큰 저장
    const saveJwtToken = (token) => {
        try {
            localStorage.setItem('jwtToken', token);
            setJwtToken(token); // 상태 업데이트
        } catch (error) {
            console.error('Error saving JWT token:', error);
        }
    };

    // URL에서 JWT 토큰 확인
    const getJwtTokenFromUrl = () => {
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');
        if (token) {
            saveJwtToken(token); // 토큰 저장
            navigate('/'); // 홈 페이지로 이동
        }
    };

    useEffect(() => {
        if (jwtToken) {
            console.log("JWT Token exists, no default fetch request.");
        } else {
            getJwtTokenFromUrl(); // URL에서 JWT 토큰 확인
        }
    }, [jwtToken]);

    const kakaoClientId = '9ae623834d6fbc0413f981285a8fa0d5';

    const kakaoOnSuccess = async (data) => {
        const idToken = data.response.access_token;  // 카카오에서 받은 엑세스 토큰
        const provider = 'kakao'; // 카카오 로그인 provider 설정
        saveJwtToken(idToken); // JWT 토큰 저장
        fetchUserData(idToken, provider); // 사용자 데이터 가져오기
    };

    const kakaoOnFailure = (error) => {
        console.log(error);
    };

    const googleOnSuccess = (res) => {
        if (res.credential) {
            const provider = 'google'; // 구글 로그인 provider 설정
            saveJwtToken(res.credential); // JWT 토큰 저장
            fetchUserData(res.credential, provider); // 사용자 데이터 가져오기
        }
    };

    return (
        <div className="main-page">
            <div className="logo-container">
                <div className="logo" onClick={handleRedirect}>JobScanner</div>
            </div>
            <h1>로그인</h1>
            <div className="login-container">
                <div className="login-buttons">
                    <GoogleOAuthProvider clientId="794316202103-0khiaob0cj1ukqe7pqgehsfqhssjs2o3.apps.googleusercontent.com">
                        <GoogleLogin
                            onSuccess={googleOnSuccess}
                            onFailure={(err) => console.error('Google login failed:', err)}
                        />
                    </GoogleOAuthProvider>
                    <KakaoLogin
                        token={kakaoClientId}
                        onSuccess={kakaoOnSuccess}
                        onFail={kakaoOnFailure}
                    />
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
