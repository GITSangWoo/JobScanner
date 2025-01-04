import React, { useState, useEffect } from 'react';
import './LogInPage.css';
import { useNavigate } from 'react-router-dom';
import { Cookies } from 'react-cookie';

function KakaoLogin() {
  const [accessToken, setAccessToken] = useState('');
  const [refreshToken, setRefreshToken] = useState('');
  const [userInfo, setUserInfo] = useState(null);
  const navigate = useNavigate();
  const cookies = new Cookies();

  const handleRedirect = () => {
    navigate("/", { replace: true });
    window.location.reload(); // 페이지 새로고침
  };

  // 쿠키에 값을 설정하는 함수
  const setCookie = (name, value, days = 7) => {
    cookies.set(name, value, { path: '/', maxAge: days * 24 * 60 * 60 });
  };

  // 쿠키에서 값을 가져오는 함수
  const getCookie = (name) => {
    return cookies.get(name);
  };

  // 카카오 API 초기화
  useEffect(() => {
    if (typeof window.Kakao !== 'undefined' && !window.Kakao.isInitialized()) {
      window.Kakao.init('9ae623834d6fbc0413f981285a8fa0d5'); // YOUR_APP_KEY
    }
  }, []);

  // 카카오 로그인
  const kakaoLogin = () => {
    if (typeof window.Kakao === 'undefined') {
      console.error('카카오 SDK가 로드되지 않았습니다.');
      return;
    }

    window.Kakao.Auth.login({
      success: (authObj) => {
        // 액세스 토큰과 리프레시 토큰을 상태로 저장
        const accessToken = authObj.access_token;
        const refreshToken = authObj.refresh_token;

        // 액세스 토큰을 쿠키에 저장
        setCookie('access_token', accessToken);

        // 쿠키에 저장된 access token 확인 (디버깅용)
        const token = getCookie('access_token');
        console.log('쿠키에서 가져온 Access Token:', token);

        // 서버로 액세스 토큰과 리프레시 토큰을 전송
        sendTokensToServer(accessToken, refreshToken);

        // 로그인 후 루트 페이지로 리디렉션
        handleRedirect();
      },
      fail: (err) => {
        console.error('로그인 실패:', err);
      },
    });
  };

  // 서버로 액세스 토큰과 리프레시 토큰을 전송
  const sendTokensToServer = (accessToken, refreshToken) => {
    const kakaoTokenDTO = {
      accessToken,  // 액세스 토큰 추가
      refreshToken, // 리프레시 토큰
    };

    fetch('http://43.202.186.119:8972/login/kakao', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // 쿠키를 포함하는 요청
      body: JSON.stringify(kakaoTokenDTO),
    })
        .then((response) => response.json())
        .then((data) => {
          alert(data.message || '로그인 성공');
        })
        .catch((error) => {
          console.error('서버 요청 에러:', error);
          // alert('서버 요청 중 오류가 발생했습니다.');
        });
  };

  // 유저 정보 가져오기
  const getUserInfo = () => {
    // 쿠키에서 액세스 토큰 가져오기
    const token = getCookie('access_token');
    if (!token) {
      alert('먼저 카카오 로그인해주세요!');
      return;
    }

    fetch('http://43.202.186.119:8972/user/profile', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
        .then((response) => response.json())
        .then((data) => {
          setUserInfo(data); // 유저 정보 상태 저장
        })
        .catch((error) => {
          console.error('유저 정보 가져오기 실패:', error);
        });
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
              <button onClick={kakaoLogin}>
                <img src="/image/kakao.png" alt="Kakao Login" style={{ width: "200px", height: "auto" }} />
              </button>
            </React.Fragment>
          </div>
        </div>

        {/* 로그인 후 유저 정보를 보여주는 부분 */}
        {userInfo && (
            <div className="user-info">
              <h3>유저 정보</h3>
              <pre>{JSON.stringify(userInfo, null, 2)}</pre>
            </div>
        )}
      </div>
  );
}

export default KakaoLogin;

