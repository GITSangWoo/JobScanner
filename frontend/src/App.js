// import React from "react";
// import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
// import MainPage from "./MainPage"; // 메인 페이지 컴포넌트
// import JobSummaryPage from "./JobSummaryPage"; // 기업 공고 요약 페이지 컴포넌트
// import TechStackDetailsPage from "./TechStackDetailsPage"; // TechStackDetailsPage 컴포넌트 임포트
// import LoginPage from "./LogInPage";
// // import OauthRedirectPage from "./OauthRedirectPage";
// import MyPage from "./MyPage";
// import LoginHandler from "./LoginHandler";
//
// function App() {
//     return (
//         <Router>
//             <Routes>
//                 <Route path="/" element={<MainPage />} /> {/* 메인 페이지 */}
//                 <Route path="/details/:techStackName" element={<TechStackDetailsPage />} />
//                 {/* <Route path="/oauth/redirect" component={OauthRedirectPage} /> */}
//                 <Route path="/job-summary" element={<JobSummaryPage />} /> {/* 기업 공고 요약 */}
//                 <Route path="/login" element={<LoginPage />} />
//                 <Route path="/mypage" element={<MyPage />} />
//                 <Route path="/auth/login/kakao" element={<LoginHandler />} //당신이 redirect_url에 맞춰 꾸밀 컴포넌트
//                 />
//             </Routes>
//         </Router>
//     );
// }
//
// export default App;


import React, { useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import { Cookies } from "react-cookie";
import MainPage from "./MainPage"; // 메인 페이지 컴포넌트
import JobSummaryPage from "./JobSummaryPage"; // 기업 공고 요약 페이지 컴포넌트
import TechStackDetailsPage from "./TechStackDetailsPage"; // TechStackDetailsPage 컴포넌트 임포트
import LoginPage from "./LogInPage";
import MyPage from "./MyPage";
import LoginHandler from "./LoginHandler";

// 쿠키에서 액세스 토큰을 확인하고 만료된 경우 쿠키 삭제하는 함수
const checkAccessTokenExpiry = async (accessToken, cookies) => {
    const url = "https://kapi.kakao.com/v2/user/me";

    try {
        const response = await fetch(url, {
            method: "GET",
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });

        if (response.status === 401) {
            // 만약 토큰이 만료되었다면
            console.log("액세스 토큰이 만료되었습니다.");
            cookies.remove("access_token", { path: "/" }); // 만료된 토큰 삭제
            // 세션에 저장된 리디렉션 URL을 읽어서 해당 URL로 리디렉션
            const redirectUrl = sessionStorage.getItem("redirectUrl") || "/"; // 기본값은 메인 페이지
            navigate(redirectUrl); // 저장된 URL로 리디렉션
        }
    } catch (error) {
        console.error("카카오 API 호출 오류:", error);
        cookies.remove("access_token", { path: "/" }); // 오류 발생 시 토큰 삭제
        // 세션에 저장된 리디렉션 URL을 읽어서 해당 URL로 리디렉션
        const redirectUrl = sessionStorage.getItem("redirectUrl") || "/";
        navigate(redirectUrl); // 저장된 URL로 리디렉션
    }
};

function App() {
    const cookies = new Cookies();
    const navigate = useNavigate();

    // 페이지가 로드될 때마다 액세스 토큰 만료 여부를 확인
    useEffect(() => {
        const accessToken = cookies.get("access_token");

        // 사용자가 페이지를 처음 로드할 때 리디렉션할 URL을 sessionStorage에 저장
        sessionStorage.setItem("redirectUrl", window.location.pathname);

        if (accessToken) {
            checkAccessTokenExpiry(accessToken, cookies,navigate); // 액세스 토큰 만료 여부 확인
        } else {
            // 로그인 상태만 해제하고, 로그인 페이지로 리디렉션하지 않음
            cookies.remove("access_token", { path: "/" });
            navigate(window.location.pathname); // 현재 페이지에 그대로 남음
        }
    }, [cookies,navigate]);

    return (
        <Router>
            <Routes>
                <Route path="/" element={<MainPage />} /> {/* 메인 페이지 */}
                <Route path="/details/:techStackName" element={<TechStackDetailsPage />} />
                <Route path="/job-summary" element={<JobSummaryPage />} /> {/* 기업 공고 요약 */}
                <Route path="/login" element={<LoginPage />} />
                <Route path="/mypage" element={<MyPage />} />
                <Route path="/auth/login/kakao" element={<LoginHandler />} />
            </Routes>
        </Router>
    );
}

export default App;
