import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const OauthRedirectPage = () => {
    const navigate = useNavigate();

    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8972';

    // URL에서 토큰을 가져와서 로컬 스토리지에 저장하고 홈으로 리다이렉션
    useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');
        
        if (token) {
            localStorage.setItem('jwtToken', token); // JWT 토큰 로컬 스토리지에 저장
            navigate('/'); // 홈 페이지로 이동
        } else {
            console.error('No token found in URL');
            navigate('/login'); // 로그인 페이지로 리다이렉트
        }
    }, [navigate]);

    return (
        <div>
            <h1>Redirecting...</h1>
        </div>
    );
};

export default OauthRedirectPage;
