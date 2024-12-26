import { useEffect } from "react";
import axios from "axios";

const LoginHandler = () => {
  const code = new URL(window.location.href).searchParams.get("code");

  useEffect(() => {
    const kakaoLogin = async () => {
      if (code) {
        try {
          const response = await axios.post(
            '/auth/login/kakao',  // 백엔드에 요청 보내기
            { code }  // 요청 본문에 code 포함
          );
          console.log("Login successful:", response.data);
          // 백엔드에서 반환한 로그인 성공 데이터 처리
        } catch (error) {
          console.error("Login error:", error);
        }
      } else {
        console.error("No authorization code received.");
      }
    };
    kakaoLogin();
  }, [code]);

  return <div>로그인 처리 중...</div>;
};

export default LoginHandler;
