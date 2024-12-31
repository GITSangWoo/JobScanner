import { useEffect } from "react";

const LoginHandler = () => {
  const code = new URL(window.location.href).searchParams.get("code");

  useEffect(() => {
    fetch(`http://localhost:8972/auth/login/kakao?code=${code}`, {
      method: "GET",  // POST에서 GET으로 변경
      headers: {
        "Content-Type": "application/json",  // 기본적으로 GET은 body를 사용하지 않음
      },
      credentials: "include",  // 쿠키와 자격증명 포함
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        console.log(data.result.user_id);
        console.log(data.result.jwt);
      })
      .catch((error) => {
        console.error("오류 발생", error);
      });
  }, []);

  return <div>로그인 처리 중...</div>;
};

export default LoginHandler;
