import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import MainPage from "./MainPage"; // 메인 페이지 컴포넌트
import JobSummaryPage from "./JobSummaryPage"; // 기업 공고 요약 페이지 컴포넌트
import TechStackDetailsPage from "./TechStackDetailsPage"; // TechStackDetailsPage 컴포넌트 임포트
import LoginPage from "./LogInPage";
// import OauthRedirectPage from "./OauthRedirectPage";
import MyPage from "./MyPage";
import LoginHandler from "./LoginHandler";

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<MainPage />} /> {/* 메인 페이지 */}
                <Route path="/details/:techStackName" element={<TechStackDetailsPage />} />
                {/* <Route path="/oauth/redirect" component={OauthRedirectPage} /> */}
                <Route path="/job-summary" element={<JobSummaryPage />} /> {/* 기업 공고 요약 */}
                <Route path="/login" element={<LoginPage />} />
                <Route path="/mypage" element={<MyPage />} />
                <Route path="/auth/login/kakao" element={<LoginHandler />} //당신이 redirect_url에 맞춰 꾸밀 컴포넌트
                />
            </Routes>
        </Router>
    );
}

export default App;
