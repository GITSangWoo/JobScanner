import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleLogin } from "@react-oauth/google";
import { GoogleOAuthProvider } from "@react-oauth/google";
import KakaoLogin from "react-kakao-login";
// import NaverLogin from "react-naver-login"; // Naver Login 패키지 주석 처리
import './LogInPage.css';

const LoginPage = () => {
    const navigate = useNavigate();
    const [jwtToken, setJwtToken] = useState(localStorage.getItem('jwtToken')); // 로컬 스토리지에서 JWT 토큰 불러오기

    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8972';

    const handleRedirect = () => {
        navigate("/", { replace: true });
        window.location.reload(); // 페이지 새로고침
    };

    const fetchUserData = (token) => {
        fetch(`${BACKEND_URL}/user`, {
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

    const saveJwtToken = (token) => {
        try {
            localStorage.setItem('jwtToken', token);
            setJwtToken(token); // 상태 업데이트
        } catch (error) {
            console.error('Error saving JWT token:', error);
        }
    };

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
            fetchUserData(jwtToken); // JWT 토큰이 있으면 사용자 데이터 가져오기
        } else {
            getJwtTokenFromUrl(); // URL에서 JWT 토큰 확인
        }
    }, [jwtToken]);

    const kakaoClientId = '9ae623834d6fbc0413f981285a8fa0d5';
    const kakaoOnSuccess = async (data) => {
        const idToken = data.response.access_token;  // 카카오에서 받은 엑세스 토큰
        fetch(`${BACKEND_URL}/auth/login/kakao?code=${idToken}`)
            .then(response => response.json())
            .then(data => {
                saveJwtToken(data.token); // JWT 토큰 저장
                fetchUserData(data.token); // 사용자 데이터 가져오기
            })
            .catch(error => console.error('Kakao login error:', error));
    };
    const kakaoOnFailure = (error) => {
        console.log(error);
    };

    const googleOnSuccess = (res) => {
        if (res.credential) {
            fetch(`${BACKEND_URL}/auth/login/google?code=${res.credential}`)
                .then(response => response.json())
                .then(data => {
                    saveJwtToken(data.token); // JWT 토큰 저장
                    fetchUserData(data.token); // 사용자 데이터 가져오기
                })
                .catch(error => console.error('Google login error:', error));
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
                        <GoogleLogin onSuccess={googleOnSuccess} onFailure={(err) => console.error('Google login failed:', err)} />
                    </GoogleOAuthProvider>

                    {/* NaverLogin 관련 코드 주석 처리 */}
                    {/* 
                    <NaverLogin
                        clientId="your-naver-client-id"
                        callbackUrl={`${BACKEND_URL}/login/oauth2/authorization/naver`}
                        onSuccess={naverOnSuccess}
                        onFailure={(err) => console.error('Naver login failed:', err)}
                        render={(props) => <button className="login-button" onClick={props.onClick}>네이버로 로그인 하기</button>}
                    />
                    */}

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
