import React, { useState } from 'react';
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
  React.useEffect(() => {
    if (!window.Kakao.isInitialized()) {
      window.Kakao.init('9ae623834d6fbc0413f981285a8fa0d5'); // YOUR_APP_KEY
    }
  }, []);

  // 카카오 로그인
  const kakaoLogin = () => {
    window.Kakao.Auth.login({
      success: (authObj) => {
        console.log('로그인 성공:', authObj);
        setAccessToken(authObj.access_token);
        setRefreshToken(authObj.refresh_token);

        // 세션에 액세스 토큰 저장
        sessionStorage.setItem('accessToken', authObj.access_token);

        // 서버로 토큰 전송
        sendTokensToServer(authObj.access_token, authObj.refresh_token);
      },
      fail: (err) => {
        console.error('로그인 실패:', err);
      },
    });
  };

  // 서버로 토큰 전송
  const sendTokensToServer = (accessToken, refreshToken) => {
    const kakaoTokenDTO = {
      accessToken,
      refreshToken,
    };

    fetch('http://43.202.186.119:8973/login/kakao', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(kakaoTokenDTO),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('서버 응답:', data);
        alert(data.message || '로그인 성공');
      })
      .catch((error) => {
        console.error('서버 요청 에러:', error);
        alert('서버 요청 중 오류가 발생했습니다.');
      });
  };

  // 유저 정보 가져오기
  const getUserInfo = () => {
    if (!accessToken) {
      alert('먼저 카카오 로그인해주세요!');
      return;
    }

    fetch('http://43.202.186.119:8973/user/profile', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('유저 정보:', data);
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
                    <button
                        onClick={kakaoLogin}
                    >
                        <img src="/image/kakao.png" alt="Kakao Login" style={{ width: "200px", height: "auto" }} />
                    </button>
                </React.Fragment>
            </div>
        </div>
    </div>
);
}

export default KakaoLogin;
