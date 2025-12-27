# 🍎 AI Co-teacher: AI 학습 데이터 분석 대시보드
**컴퓨팅사고와 SW코딩 기말 프로젝트** **작성자:** 2021113295 영어영문학과 박한내  
**제출일:** 2025년 12월 27일

## 1. 프로젝트 개요 (Introduction)
본 프로젝트는 언어 교육 환경에서 발생하는 학생들의 다양한 학습 데이터(클릭 수, 퀴즈 점수, 상호작용, 학습 시간 등)를 실시간으로 수집, 분석 및 시각화합니다. 이를 통해 교사의 학생 관리 및 효율적인 교수 의사결정을 지원하는 전문적인 AI 학습 분석 도구를 제공하는 것이 목적입니다.

## 2. 핵심 교육학 알고리즘 (Pedagogical Logic)
명세서(SRS)에 정의된 교육학적 이론을 데이터 과학적으로 정교하게 수식화하여 구현하였습니다.

* **ZPD (Zone of Proximal Development)**: Vygotsky의 이론을 바탕으로 학생 점수의 평균($\mu$) $\pm$ 표준편차($\sigma$) 구간을 계산하여 학생별 적정 학습 난이도 구간을 시각화합니다.
* **VARK 모델**: 행동 데이터(클릭, 시간, 상호작용)를 정규화하여 시각(V), 청각(A), 읽기/쓰기(R), 운동(K) 학습 스타일을 점수제로 분류합니다.
* **SRL_Index (자기조절학습)**: Zimmerman의 이론에 따라 `(time_spent/120 + interactions + success) / 3` 공식을 통해 자율 학습 역량을 수치화합니다.
* **Growth Mindset**: Dweck의 성장형 사고방식 이론을 기반으로 노력(interactions)과 성취(success)의 상관관계를 분석하여 학생의 발전 가능성을 지표화합니다.

## 3. 주요 기능 (Key Features)

### 📊 실시간 대시보드 및 성과 분석 (FR2, UC-001)
* **KPI 카드**: 학생 수, 평균 성적, 평균 성장 마인드셋, 학습 성공률 등 핵심 지표를 요약 제공합니다.
* **ZPD 분석 차트**: Plotly를 활용하여 퀴즈 점수 분포를 표시하고, 계산된 ZPD 하한/상한선을 통해 적정 학습 구간 이탈 여부를 시각화합니다.

### 🚨 위험 학생 자동 감지 및 개입 (FR5, UC-002)
* **실시간 모니터링**: `quiz_score < 50` 또는 `SRL_Index < 0.3`인 학생을 시스템이 자동 감지하여 🚨고위험 플래그를 부여합니다.
* **산점도 분석**: 참여도(SRL) 대비 성적을 시각화하며, 점의 크기를 통해 개별 학생의 '성장 마인드셋' 수준을 동시에 파악할 수 있습니다.

### 🤖 AI 심층 예측 및 개인화 추천 (FR3, UC-003)
* **RandomForest 분석**: 앙상블 머신러닝 알고리즘을 통해 학습 성공 기여 요인을 분석하고, 전체 학생 데이터 중 어떤 특성이 성패에 큰 영향을 주었는지 시각화합니다.
* **개별 추이 분석**: 특정 학생 선택 시 **AI 기반 성공 예측 확률(%)**을 게이지 차트로 보여주며, 해당 학생의 성적 현황을 심층 분석합니다.
* **맞춤형 처방**: VARK 유형과 분석 지표를 결합하여 보충 자료 제공 혹은 심화 과제 권장 등 개인화된 피드백 메시지를 전송합니다.

## 4. 시스템 아키텍처 (Product Perspective)
* **기술 스택**: Python, Streamlit, Scikit-learn, Plotly
* **데이터 흐름**: 웹 브라우저 → Streamlit 서버 → Python 백엔드 → 머신러닝 모델 분석

## 5. 실행 및 배포 (How to Run)
1. **라이브러리 설치**: `pip install streamlit pandas numpy plotly scikit-learn`
2. **대시보드 실행**: `streamlit run app.py`
3. **실시간 대시보드 주소**: [AI Co-teacher 라이브 서비스 바로가기](https://ai-co-teacher-v3-vtnocrr4brtpyappedof7pc.streamlit.app/)

## 📂 데이터 입력 명세 (CSV Header Specification)
본 시스템은 CSV 파일 업로드를 통해 데이터를 관리하며, 다음 헤더 구조를 준수해야 합니다.

| 컬럼명 | 데이터 타입 | 설명 | 관련 지표 |
| :--- | :--- | :--- | :--- |
| **`student_id`** | String | 학생 고유 식별 코드 | 학생 관리 |
| **`quiz_score`** | Integer | 퀴즈 성적 (0~100) | ZPD, 위험 감지 |
| **`clicks`** | Integer | 시스템 내 클릭 횟수 | VARK 진단 |
| **`time_spent`** | Integer | 학습 체류 시간 (분) | SRL 지수 산출 |
| **`interactions`** | Integer | 능동적 상호작용 횟수 | 성장 마인드셋 |
| **`success`** | Boolean | 학습 성공 여부 (1/0) | AI 모델 학습 |

## 6. 참고 문헌 (References)
* Vygotsky, L. S. (1978). *Mind in society*.
* Dweck, C. S. (2006). *Mindset: The new psychology of success*.
* Zimmerman, B. J. (2002). *Becoming a self-regulated learner*.
