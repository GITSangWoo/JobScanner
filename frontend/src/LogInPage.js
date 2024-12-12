import React from 'react';
import {useNavigate} from "react-router-dom";
import './LogInPage.css';

const LoginPage = () => {
    const navigate = useNavigate();
    const handleClick = () => {
        navigate("/", { replace: true }); // navigate 호출
        window.location.reload();
    };
    return (
        <div className="main-page">
            <div className="logo-container">
                <div className="logo" onClick={handleClick}>JobScanner</div>
            </div>
            <h1>로그인</h1>
            <div className="login-container">
                <div className="login-buttons">
                    <button className="login-button" onClick={() => window.location.href = '구글 OAuth 인증 URL'}>
                        구글로 로그인 하기
                    </button>
                    <button className="login-button" onClick={() => window.location.href = '네이버 OAuth 인증 URL'}>
                        네이버 로그인 하기
                    </button>
                    <button className="login-button" onClick={() => window.location.href = '카카오 OAuth 인증 URL'}>
                        카카오 로그인 하기
                    </button>
                </div>
                {/*<div className="sign-up-link">*/}
                {/*    아직 회원이 아니세요?*/}
                {/*    <a href="/sign-up" className="auth-button">회원가입</a>*/}
                {/*</div>*/}
            </div>
        </div>
    );
};

export default LoginPage;
