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
        }
    } catch (error) {
        console.error("카카오 API 호출 오류:", error);
        cookies.remove("access_token", { path: "/" }); // 오류 발생 시 토큰 삭제
    }
};

function App() {
    const cookies = new Cookies();

    // 페이지가 로드될 때마다 액세스 토큰 만료 여부를 확인
    useEffect(() => {
        const accessToken = cookies.get("access_token");
        if (accessToken) {
            checkAccessTokenExpiry(accessToken, cookies); // 액세스 토큰 만료 여부 확인
        } else {
            console.log("액세스 토큰이 존재하지 않습니다.");
        }
    }, [cookies]);

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
