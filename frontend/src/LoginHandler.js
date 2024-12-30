import { useEffect } from "react";
import axios from "axios";

const LoginHandler = () => {
  const code = new URL(window.location.href).searchParams.get("code");
  const headers ={
    "Content-Type": "application/x-www-form-urlencoded",
  }

  // useEffect(() => {
  //   const kakaoLogin = async () => {
  //     if (code) {
  //       try {
  //         const backend_url="http://localhost:8972";
  //         const response = await axios.post(
  //           `${backend_url}/auth/login/kakao`,  // 백엔드에 요청 보내기
  //           { code }  // 요청 본문에 code 포함
  //         );
  //         console.log("Login successful:", response.data);
  //         // 백엔드에서 반환한 로그인 성공 데이터 처리
  //       } catch (error) {
  //         console.error("Login error:", error);
  //       }
  //     } else {
  //       console.error("No authorization code received.");
  //     }
  //   };
  //   kakaoLogin();
  // }, [code]);

  useEffect(() => {
    fetch(`http://localhost:8972/auth/login/kakao?code=${code}`, {
      method: "POST", // 
      headers: headers,
      credentials: "include",
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        console.log(data.result.user_id);
        console.log(data.result.jwt);
      })
      .catch((error) => {
        console.error("오류 발생", error); //
      });
  }, []);

  return <div>로그인 처리 중...</div>;
};

export default LoginHandler;
