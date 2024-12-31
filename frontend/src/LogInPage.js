import React, { useState, useEffect } from 'react';
import './LogInPage.css';
import { useNavigate } from 'react-router-dom';

function KakaoLogin() {
  const [accessToken, setAccessToken] = useState('');
  const [refreshToken, setRefreshToken] = useState('');
  const [userInfo, setUserInfo] = useState(null);
  const navigate = useNavigate();

  const handleRedirect = () => {
    navigate("/", { replace: true });
    window.location.reload(); // 페이지 새로고침
  };

  // 카카오 API 초기화
  useEffect(() => {
    if (typeof window.Kakao !== 'undefined' && !window.Kakao.isInitialized()) {
      window.Kakao.init('9ae623834d6fbc0413f981285a8fa0d5'); // YOUR_APP_KEY
    }
  }, []); // 빈 배열로 컴포넌트 마운트 시 한 번만 실행

  // 카카오 로그인
  const kakaoLogin = () => {
    if (typeof window.Kakao === 'undefined') {
      console.error('카카오 SDK가 로드되지 않았습니다.');
      return;
    }

    window.Kakao.Auth.login({
      success: (authObj) => {
        setAccessToken(authObj.access_token);
        setRefreshToken(authObj.refresh_token);

        // 쿠키에 액세스 토큰 저장 (HTTP-only로 저장)
        document.cookie = `accessToken=${authObj.access_token}; path=/; HttpOnly; SameSite=None`;

        // 쿠키에 저장된 access token 확인 (디버깅용)
        checkAccessTokenInCookies();

        // 서버로 리프레시 토큰 전송
        sendTokensToServer(authObj.refresh_token);

        // 로그인 후 루트 페이지로 리디렉션
        handleRedirect();
      },
      fail: (err) => {
        console.error('로그인 실패:', err);
      },
    });
  };

  // 서버로 리프레시 토큰 전송
  const sendTokensToServer = (refreshToken) => {
    const kakaoTokenDTO = {
      refreshToken,
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
        alert('서버 요청 중 오류가 발생했습니다.');
      });
  };

  // 쿠키에서 액세스 토큰 확인하는 함수
  const checkAccessTokenInCookies = () => {
    const cookies = document.cookie.split(';');
    let accessTokenFound = false;

    // 쿠키에서 'accessToken'을 찾아서 확인
    cookies.forEach(cookie => {
      if (cookie.trim().startsWith('accessToken=')) {
        accessTokenFound = true;
      }
    });

    // 결과에 따라 알림 표시
    if (accessTokenFound) {
      alert('Access Token이 쿠키에 저장되었습니다.');
    } else {
      alert('Access Token이 쿠키에 저장되지 않았습니다.');
    }
  };

  // 유저 정보 가져오기
  const getUserInfo = () => {
    // 쿠키에서 액세스 토큰 가져오기
    const token = document.cookie.split(';').find(cookie => cookie.trim().startsWith('accessToken='));
    if (!token) {
      alert('먼저 카카오 로그인해주세요!');
      return;
    }
    const accessToken = token.split('=')[1];

    fetch('http://43.202.186.119:8972/user/profile', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${accessToken}`,
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
    </div>
  );
}

export default KakaoLogin;
