![venom](https://capsule-render.vercel.app/api?type=venom&height=200&text=JobScanner&fontSize=40&color=100:ff7f00,100:87ceeb&stroke=ffffff&fontFamily=Comic%20Sans%20MS)

---

## 🫂 Team
| **이름**     | **GitHub URL**                                | **책임**                                                                 |
|--------------|-----------------------------------------------|--------------------------------------------------------------------------|
| **김도현**   | [바로가기](https://github.com/rlaehgus97)     | 애플리케이션 관리 및 유지보수<br>형상 관리 및 배포 문제 해결<br>Docker, Airflow<br>브랜치 전략 수립 |
| **김동욱**   | [바로가기](https://github.com/DONGUK777)      | 백엔드 개발<br>데이터 전처리<br>기술 사전 및 스택 뽑아오기                  |
| **이상우**   | [바로가기](https://github.com/GITSangWoo)     | 기술적 문제 해결 및 방향 설정<br>시스템 아키텍처 설계 및 리뷰<br>백엔드 개발<br>OCR(이미지 텍스트 변환) |
| **이상훈**   | [바로가기](https://github.com/hun0219)        | 팀원들의 애로 사항 논의<br>애자일 프로세스 적용<br>Docker, Airflow<br>크롤링 코드 통합 |
| **조하영**   | [바로가기](https://github.com/EstherCho-7)    | 프로젝트 일정 및 리소스 관리<br>프로젝트 진행 상황 모니터링<br>프론트엔드 개발<br>ERD 작성 |

<br/>

### 🛠️사용된 기술 스택
---
![최종발표용-011](https://github.com/user-attachments/assets/680e1e39-8c8f-4ddf-8dca-1e5f2e249c16)

<br/>

### 🗓️ 전체 프로젝트 일정
> **프로젝트 일정 : 2024년 12월 14일 ~ 2024년 1월 6일(총 24일)**

<br/>

## 목차
 1. [📚프로젝트 개요](#프로젝트-개요)
 2. [📋요구사항 정의서](#요구사항-정의서)
 3. [📅개발 일정](#개발-일정)
 4. [⚙주요 기능](#주요-기능)
 5. [🏗️시스템 아키텍처](#시스템-아키텍처)
 6. [🌐환경 구성](#환경-구성)
 7. [✅테스트 결과](#테스트-결과)
 8. [⌨트러블 슈팅 및 PR](#트러블-슈팅-및-PR)
 9. [🔄KPT 회고](#KPT-회고)
10. [🔍최종 검토 및 개선](#최종-검토-및-개선)

<br/>

## 📚프로젝트 개요

### JobScanner 취업 준비의 스마트 솔루션

이 프로젝트는 여러러 채용 공고 사이트의 정보를 크롤링하여 다양한 인사이트(직군별 핵심 키워드 순위, 기술 정보 제공, 직무 소개, 채용 공고 요약)를 제공하여 SW 개발 입문/취업에 실질적인 도움을 주는 것이 목표입니다.

---

### 프로젝트 시나리오
**[목적]**
> Kubernetes에서 Prometheus와 Grafana를 사용하여 Docker 웹 서버의 CPU 사용량을 모니터링하고, 자동 및 수동 스케일링을 통해 부하에 유연하게 대응하는 시스템 구축.

**[구성요소]**
> - Step.1 (요구사항)
> **Docker 웹 서버**: CPU 부하를 발생시킬 웹 서버 Docker 컨테이너
> **Node Exporter**: Docker 컨테이너의 CPU 정보를 받아오기 위한 Exporter
> **Prometheus**: Kubernetes 클러스터와 애플리케이션의 메트릭 수집
> **Grafana**: Prometheus 메트릭을 기반으로 시각화 및 모니터링
> **Streamlit 관리자 페이지**: 예상 부하 증가 시 수동 스케일링을 지원하는 관리 기능

> - Step.2 (최종 프로젝트 환경 구성)
> **AirFlow**: 파이널 프로젝트에서 크롤링 한 데이터를 ETL 하기 위한 프레임 워크
> **Spark**: 파이널 프로젝트에서 생길 대용량 데이터를 병렬 처리 하기 위한 프레임 워크 
> **Spark 모니터링**: Grafana를 활용한 Spark 모니터링
> **Spark Auto Scale Out**: CPU 제한에 따른 Warker Auto Scale Out

**[주요 기능]**
> 웹 서버에 부하를 주어 CPU 사용량 변화 모니터링
> Grafana 대시보드를 통해 CPU 사용량을 시각화
> 이벤트 대비를 위한 수동 스케일 업/다운 기능이 있는 관리자 페이지 제공

<br/>

### 📋요구사항 정의서
---
#### 1. 기능적 요구사항

| **요구사항 ID**     | **구분**            | **요구사항 설명**                                  | **중요도** | **구현 상태** |
|---------------------|---------------------|--------------------------------------------------|------------|---------------|
| **FR-01**           | 모니터링            | 웹의 CPU 사용량 모니터링, Grafana에서 시각화 | **🔴 높음**       | **✅ 완료**          |
| **FR-02**           | 자동 스케일링       | CPU 사용량 초과 시 자동으로 스케일 업/다운     | **🔴 높음**       | **✅ 완료**          |
| **FR-03**           | 수동 스케일링       | Streamlit 페이지에서 수동 스케일링               | **🟡 중간**       | **✅ 완료**          |
| **FR-04**           | 부하 테스트         | Docker Compose로 서버 부하 테스트               | **🟡 중간**       | **✅ 완료**          |
| **FR-05**           | 데이터 수집 및 변환 | AirFlow가 정상 실행 가능                        | **🟡 중간**       | **✅ 완료**        |
| **FR-06**           | 데이터 분산 처리    | Spark 모니터링 및 Manual Scale In/Out               | **🔴 높음**       | **✅ 완료**        |

#### 2. 비기능적 요구사항

| **요구사항 ID**     | **구분**     | **요구사항 설명**                                 | **중요도** | **구현 상태** |
|---------------------|--------------|--------------------------------------------------|------------|---------------|
| **NFR-01**          | 성능         | 웹 서버 부하 발생 시 성능 저하 없이 작동          | **🔴 높음**       | **✅ 완료**          |
| **NFR-02**          | 확장성       | 웹 서버는 트래픽 증가 시 자동 스케일링되어야 함  | **🔴 높음**       | **✅ 완료**          |
| **NFR-03**          | 안정성       | 스케일링 기능이 정상 동작, 장애 발생 시 서비스 중단 X | **🔴 높음**       | **✅ 완료**          |

#### 3. 제약 사항

| **요구사항 ID**    | **구분**      | **요구사항 설명**                             | **중요도** | **구현 상태** |
|--------------------|---------------|-----------------------------------------------|------------|---------------|
| **CR-01**          | 기술 스택     | Kubernetes, Prometheus, Grafana 사용         | **🔴 높음**       | **✅ 완료**          |
| **CR-02**          | 환경 설정     | 로컬 및 클라우드(Kubernetes) 환경에서 동작    | **🔴 높음**       | **✅ 완료**          |

#### 4. 구현 상태

| **구분**       | **구현 상태**         | **설명**                                |
|----------------|-----------------------|-----------------------------------------|
| **✅ 완료**       | 전체 시스템           | 모든 기능 정상 동작                    |
| **✅ 완료**       | 스케일링              | 자동/수동 스케일링 완료                 |
| **✅ 완료**       | 부하 테스트           | 정상 동작                              |
| **✅ 완료**       | 데이터 수집 및 변환   | Airflow 도커 실행 완료                  |
| **✅ 완료**       | 데이터 분산 처리      | Spark 도커 실행 완료                   |
| **✅ 완료**     | Spark 모니터링        | Grafana 모니터링 완료                |
| **✅ 완료**     | Spark Worker Manual Scale in/out | Manual Scale In/Out 완료            |

<br/>

### 📅개발 일정
---
- [Git Hub 칸반보드](https://github.com/orgs/DE32FinalTeam2/projects/4/views/1?layout=roadmap)

<br/>

### ⚙주요 기능
---
#### 1. Kubernetes 상의 Prometheus 및 Grafana 배포
   - Kubernetes 클러스터에 Prometheus와 Grafana를 배포하여 웹 서버의 CPU 사용량을 수집하고 대시보드에서 실시간으로 확인합니다.

#### 2. Docker 웹 서버 배포 및 부하 테스트
   - Docker Compose로 웹 서버를 실행하고, 부하 테스트를 통해 CPU 사용량 변화를 관찰합니다.

#### 3. 자동 및 수동 스케일링
   - **자동 스케일링**: CPU 사용량이 설정된 임계치를 넘으면 서버가 자동으로 스케일 업됩니다.
   - **수동 스케일링**: 관리자 페이지에서 필요에 따라 수동으로 서버 스케일 업/다운을 조정할 수 있습니다.

<br/>

### 🏗️시스템 아키텍처
---
![image](https://github.com/user-attachments/assets/5d35abed-b4a5-4c5f-aee8-60cdabac13ae)

<br/>

### 🌐환경 구성
---
#### Team_repository clone
```bash
$ git clone git@github.com:DE32FinalTeam2/FourthProject.git
```

### Airflow 실행
```bash
$ cd airflow

$ docker compose up -d
```


### java 웹 실행
```bash
# minikube 실행

$ minikube start

$ kubectl apply -f java-deployment.yaml

$ minikube service java-service --url
```

#### Spark/Exporter/Prometheus/Grafana 실행
```bash
# 해당 docker-compose.yaml이 있는 디렉토리로 이동

# FourthProject 기준

$ cd moni

$ docker compose up -d
```

#### 그 이후 진행사항
```bash 
# FourthProject 기준

$ pip install .

$ streamlit run src/fourthproject/main.py

# streamlit web 접속 (http://localhost:8501)

# manual scale In/Out
```

### 번외/테스트
```bash
# 부하 테스트

$ ab -t <테스트 지속 시간(s)> -c <동시 요청 수> http://localhost:8949/
```


<br/>

### ✅테스트 결과
---
![image](https://github.com/user-attachments/assets/89fee6a8-c9cd-4f3c-a0ed-b5f75c83c0dc)
---
![image](https://github.com/user-attachments/assets/a8e05d27-193c-4bf0-9d2d-80621262c06a)
---
![image](https://github.com/user-attachments/assets/ee2f11c3-466a-4559-8abc-4fd74630a7e7)
---
![image](https://github.com/user-attachments/assets/29f56c0d-66c1-4a15-9dc3-03cef04b8e9e)

<br/>

## ⌨트러블 슈팅 및 PR
- [[Dev 0.1.0] 우선 구현해야 할거 정리](https://github.com/DE32FinalTeam2/FourthProject/pull/1)
- [Release 0.1.0](https://github.com/DE32FinalTeam2/FourthProject/pull/2)
- [Streamlit cpu 사용량, 메모리 사용량, 네트워크 대역폭 사용량 차트](https://github.com/DE32FinalTeam2/FourthProject/pull/3)
- [1차 작업물 통합하기](https://github.com/DE32FinalTeam2/FourthProject/pull/4)


<br/>

# 🔄KPT 회고

## 김동욱
<details>
<summary>KEEP</summary>
<div>
<figure align="center">
  <p>1. 업무 분담이 확실하게 이루어졌다.</p>
  <p>2. 이전에 수업했던 내용들을 종합하여 복습할 수 있었다.</p>
  <p>3. 최종 프로젝트에서 설계될 구조를 미리 학습할 수 있었다.</p>
 </figure>
</div>
</details>

<details>
<summary>PROBLEM</summary>
<div>
<figure align="center">
  <p>아직 kubenetes, prometheus, exporter에 대한 이해가 부족해서 공부하면서 프로젝트를 진행하려니 시간이 다소 소모되었다.</p>
 </figure>
</div>
</details>


<details>
<summary>TRY</summary>
<div>
<figure align="center">
  <p>Grafana를 활용하여 Spark 지표를 모니터링 및 시각화 하도록 개선해야겠다.</p>
 </figure>
</div>
</details>

## 김도현
<details>
<summary>KEEP</summary>
<div>
<figure align="center">
  <p>목표와 해야할 일을 정해놓고 분업화가 원할하게 된 것</p>
 </figure>
</div>
</details>

<details>
<summary>PROBELM</summary>
<div>
<figure align="center">
  <p>프로메테우스나 exporter에 대한 이해가 부족해 팀원이 자신이 한 일을 설명해주어도 이해하는데 시간이 걸림</p>
 </figure>
</div>
</details>

<details>
<summary>TRY</summary>
<div>
<figure align="center">
  <p>컨테이너의 메모리 사용률이나 컨테이너의 네트워크 대역폭을 읽어올 수 있는 방법이 있다고 생각함.</p>
  <p>단순히 네트워크 대역폭 최대치나 메모리 용량 metric을 상수로 받아오는 것 보다는 컨테이너의 각 리소스 metric을 실제로 읽어오는 방식을 시도하고 싶음</p>
 </figure>
</div>
</details>

## 이상우
<details>
<summary>KEEP</summary>
<div>
<figure align="center">
  <p>1. 저번 프로젝트 보다 공유도 잘되고 분업도 잘된것 같다.</p>
  <p>2. 프로젝트를 진행하는 중에 JAM이 걸리지 않아서 프로젝트 완성속도나 프로세스 진행면에서 발전된 형태를 보였다.</p>
  <p>3. 최종 프로젝트를 대비해서 미리 체험해봐야할 오류를 경험한 듯한 느낌이다 .</p>
 </figure>
</div>
</details>

<details>
<summary>PROBLEM</summary>
<div>
<figure align="center">
  <p>1. 내가 일에 참여한 시간에 비해서 내 퍼포먼스가 좀 별로였다.</p>
  <p>2. 아직 새로운 영역의 기술을 사용하거나 기존 사용하던 기술에 조금 더 발전된 테크닉을 적용시키는데 어려움이 있는 것 같다.</p>
 </figure>
</div>
</details>

<details>
<summary>TRY</summary>
<div>
<figure align="center">
  <p>1. 사람이 빠져도 진행될 수 있는 팀을 구현하기 위해서 일정을 프로젝트 적용 (기술 + 태스크) 병렬형태로 짜봤으면 좋겠다.</p>
  <p>업무 진행상황, 어려움을 겪고있는 상황이나 진행이 잘 되지 않는 상황을 ISSUE로 적극적으로 공유해봤으면 좋겠다.</p>
 </figure>
</div>
</details>

## 이상훈
<details>
<summary>KEEP</summary>
<div>
<figure align="center">
   <p>분업이 잘된 느낌이고 공유가 잘됐다.</p>
 </figure>
</div>
</details>

<details>
<summary>PROBLEM</summary>
<div>
<figure align="center">
  <p>spark 등 툴에 대한 정확한 이해도가 부족해서 트러블 슈팅시간이 좀 걸렸다.</p>
  <p>전반적으로 학습이 더 필요하다는 느낌을 많이 받았다.</p>
 </figure>
</div>
</details>

<details>
<summary>TRY</summary>
<div>
<figure align="center">
  <p>전체적인 아키텍처를 사용하고자 하는 기술을 더해 구상할 수 있는 능력을 많이 길러야겠다.</p>
 </figure>
</div>
</details>

## 조하영
<details>
<summary>KEEP</summary>
<div>
<figure align="center">
  <p> 새로 배운 것을 프로젝트에 적용해본다는 점에서 의미 깊었다.</p>
 </figure>
</div>
</details>

<details>
<summary>PROBLEM</summary>
<div>
<figure align="center">
  <p> 코드에서의 문제가 없었으나 실행이 되지 않는 이유를 코드에서만 찾는 경향이 있다.</p>
 </figure>
</div>
</details>

<details>
<summary>TRY</summary>
<div>
<figure align="center">
  <p> 문법 이슈 외에 다른 환경설정 사항들도 고려해볼 것</p>
 </figure>
</div>
</details>

<br/>

## 🔍최종 검토 및 개선

### 1. **Spark 모니터링 (완료)**

- **Grafana 대시보드 개선**: Spark 성능 지표 추가 및 대시보드 개선
- **알림 시스템 설정**: 성능 이상 발생 시 알림 받도록 설정
- **클러스터 상태 모니터링**: 각 노드 상태 실시간 추적

---

### 2. **Spark Worker Manual Scale In/Out (완료)**

- **CPU 사용량에 따른 수동 Warker 스케일링 구현**
- **스케일링 정책 설정**: 임계치 확인 및 수동 스케일 아웃

---

### 3. **기타 개선/추가 사항**

- **에러 핸들링 및 로깅 개선**: 장애 시 알림 및 로그 기록
- **부하 테스트 환경 개선**: 다양한 시나리오 테스트 추가
- **CI/CD 파이프라인 설정**: 자동 배포 파이프라인 추가


