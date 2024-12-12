import React from 'react';
import {useNavigate} from "react-router-dom";
import './SignUpPage.css';

const SignUpPage = () => {
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
            <h1>회원가입</h1>
            <div className="signup-container">
                <div className="signup-buttons">
                    <button className="signup-button" onClick={() => window.location.href = '구글 OAuth 인증 URL'}>
                        구글로 회원가입 하기
                    </button>
                    <button className="signup-button" onClick={() => window.location.href = '네이버 OAuth 인증 URL'}>
                        네이버로 회원가입 하기
                    </button>
                    <button className="signup-button" onClick={() => window.location.href = '카카오 OAuth 인증 URL'}>
                        카카오로 회원가입 하기
                    </button>
                </div>
                <div className="login-link">
                    이미 회원이세요?
                    <a href="/login" className="auth-button">로그인</a>
                </div>
            </div>
        </div>
    );
};

export default SignUpPage;
