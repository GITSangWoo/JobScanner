// auth.js
import Cookies from 'js-cookie';

// 로그인 성공 후 호출되는 함수
export const handleLoginSuccess = (accessToken) => {
  // Access token을 쿠키에 저장
  Cookies.set('access_token', accessToken, { expires: 1, path: '/' });
};

// 로그인 상태 체크 함수
export const checkLoginStatus = () => {
  const accessToken = Cookies.get('access_token');
  return accessToken ? true : false;  // 토큰이 있으면 로그인 상태
};

// 로그아웃 함수
export const handleLogout = () => {
  Cookies.remove('access_token');
  Cookies.remove('refresh_token');
};
