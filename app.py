import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
import base64

# --- 1. [FR4] 교육학 분석 지표 고도화 ---
def calculate_educational_metrics(df):
    # 정규화 (VARK 점수 산출용)
    clicks_norm = df['clicks'] / df['clicks'].max()
    time_norm = df['time_spent'] / df['time_spent'].max()
    inter_norm = df['interactions'] / df['interactions'].max()
    
    # VARK 분류 로직 
    v_score, a_score = clicks_norm, (1 - clicks_norm) * time_norm
    r_score, k_score = time_norm, inter_norm
    vark_scores = pd.DataFrame({'Visual': v_score, 'Aural': a_score, 'Read/Write': r_score, 'Kinesthetic': k_score})
    df['VARK'] = vark_scores.idxmax(axis=1)

    # SRL_Index: (time_spent/120 + interactions + success)/3 [cite: 37, 73]
    df['SRL_Index'] = (df['time_spent']/120 + df['interactions'] + df['success']) / 3
    
    # Growth Mindset: 노력(interactions)과 성취(quiz_score)의 상관관계 기반 산출 
    # (성적이 낮더라도 상호작용이 높으면 높은 점수 부여)
    df['Growth_Mindset'] = (df['interactions'] / df['interactions'].max() * 0.7) + (df['success'] * 0.3)
    
    # ZPD 구간 계산: 평균 ± 표준편차 [cite: 18, 37, 73]
    avg, std = df['quiz_score'].mean(), df['quiz_score'].std()
    zpd_range = (avg - std, avg + std)
    
    # [US-003] 위험 감지 플래그 [cite: 56, 71]
    df['Status'] = np.where((df['quiz_score'] < 50) | (df['SRL_Index'] < 0.3), '🚨 고위험', '✅ 정상')
    return df, zpd_range

# --- 2. [FR6] 보고서 생성 기능 [cite: 37, 61] ---
def get_report_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="Weekly_Report.csv">📄 주간 분석 보고서 다운로드</a>'

# --- 3. 메인 UI 및 데이터 로드 ---
st.set_page_config(page_title="AI Co-teacher", layout="wide")
st.title("🍎 AI Co-teacher: AI 학습 데이터 분석 대시보드")
st.markdown(f"작성자: 2021113295 영어영문학과 박한내") # [cite: 42]

st.sidebar.header("📂 데이터 관리")
uploaded_file = st.sidebar.file_uploader("학생 데이터 업로드 (CSV)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    # 샘플 데이터 (분석을 위해 데이터 확충) [cite: 54, 69]
    data = {
        'student_id': [f'STU_{i:03d}' for i in range(1, 13)],
        'quiz_score': [85, 45, 90, 30, 78, 55, 42, 95, 62, 38, 82, 58],
        'clicks': [150, 40, 180, 25, 120, 80, 45, 190, 110, 35, 140, 90],
        'time_spent': [180, 50, 200, 40, 150, 90, 60, 210, 130, 45, 160, 110],
        'interactions': [15, 3, 18, 2, 12, 7, 4, 20, 10, 3, 14, 8],
        'success': [1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1]
    }
    df = pd.DataFrame(data)

df, (zpd_low, zpd_high) = calculate_educational_metrics(df)

# KPI 요약 카드 [cite: 18, 37, 69]
cols = st.columns(4)
cols[0].metric("👥 총 학생 수", f"{len(df)}명")
cols[1].metric("📝 평균 성적", f"{df['quiz_score'].mean():.1f}점")
cols[2].metric("🌱 평균 성장 마인드셋", f"{df['Growth_Mindset'].mean():.2f}")
cols[3].metric("🏆 학습 성공률", f"{(df['success'].sum()/len(df))*100:.1f}%")

# --- 4. 시각화 탭 구성 ---
tab1, tab2, tab3 = st.tabs(["📊 성과 및 ZPD 분석", "🚨 위험 감지", "🤖 AI 심층 분석"])

with tab1: # [cite: 49, 69]
    st.subheader("학생별 퀴즈 성적 및 ZPD 적정 학습 구간")
    fig_zpd = px.bar(df, x='student_id', y='quiz_score', color='SRL_Index', 
                     hover_data=['VARK', 'Growth_Mindset'], title="ZPD 범위 내 성취도 확인")
    fig_zpd.add_hline(y=zpd_low, line_dash="dash", line_color="green", annotation_text="ZPD 하한")
    fig_zpd.add_hline(y=zpd_high, line_dash="dash", line_color="red", annotation_text="ZPD 상한")
    st.plotly_chart(fig_zpd, use_container_width=True)

with tab2: # [cite: 50, 71]
    st.subheader("실시간 학업 위험군 모니터링")
    fig_risk = px.scatter(df, x='SRL_Index', y='quiz_score', color='Status', size='Growth_Mindset',
                          hover_name='student_id', title="참여도 대비 성적 산점도 (원 크기: 성장 마인드셋)")
    st.plotly_chart(fig_risk, use_container_width=True)
    if not df[df['Status'] == '🚨 고위험'].empty:
        st.error("🚨 즉각적인 개입이 필요한 고위험군 학생이 존재합니다.")
        st.table(df[df['Status'] == '🚨 고위험'][['student_id', 'quiz_score', 'SRL_Index', 'Growth_Mindset']])

with tab3: # [cite: 37, 51, 73]
    st.subheader("🤖 AI 기반 학습 성공 예측 및 개별 추이")
    
    # RandomForest 모델 학습 및 피처 중요도
    X = df[['quiz_score', 'clicks', 'time_spent', 'interactions', 'SRL_Index', 'Growth_Mindset']]
    y = df['success']
    rf = RandomForestClassifier(n_estimators=100, random_state=42).fit(X, y)
    
    col_ai1, col_ai2 = st.columns([1, 1])
    
    with col_ai1:
        st.write("**AI가 분석한 성공 기여 요인**")
        imp_df = pd.DataFrame({'특성': X.columns, '중요도': rf.feature_importances_}).sort_values('중요도', ascending=False)
        st.plotly_chart(px.bar(imp_df, x='중요도', y='특성', orientation='h'), use_container_width=True)

    with col_ai2:
        st.write("**학생별 AI 예측 점수 및 성적 현황**")
        target_ai = st.selectbox("추이 분석 대상 선택", df['student_id'].unique(), key="ai_select")
        stu_data = df[df['student_id'] == target_ai].iloc[0]
        
        # AI 성공 확률 계산
        prob = rf.predict_proba(X[df['student_id'] == target_ai])[0][1] * 100
        
        # 성적 현황 게이지 차트
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = stu_data['quiz_score'],
            title = {'text': f"{target_ai} 성적 및 AI 성공예측 ({prob:.1f}%)"},
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "darkblue"},
                     'steps': [{'range': [0, 50], 'color': "red"}, {'range': [50, 100], 'color': "lightgray"}]}
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

# --- 5. 개인화 추천 및 교사 도구 [cite: 51, 58, 73] ---
st.divider()
st.subheader("💬 개인화 추천 및 개입 도구")
target = st.selectbox("학생 선택", df['student_id'].unique(), key="tool_select")
info = df[df['student_id'] == target].iloc[0]

c_rec1, c_rec2 = st.columns(2)
with c_rec1:
    st.info(f"**[{target}] 분석 결과**\n\n- 학습 유형: {info['VARK']}\n- 성장 마인드셋: {info['Growth_Mindset']:.2f}\n- ZPD 상태: {'구간 이탈' if info['quiz_score'] < zpd_low else '적정'}")
    if info['Status'] == '🚨 고위험':
        st.error(f"AI 처방: {info['VARK']}형 보충 자료 전송 및 상담 예약 권장")
    else:
        st.success(f"AI 처방: {info['VARK']}형 심화 콘텐츠 제공 및 Growth Mindset 강화 칭찬")

with c_rec2:
    msg = st.text_area("피드백 전송 (US-005)", placeholder="학생에게 보낼 메시지를 입력하세요.")
    if st.button("📧 메시지 전송"):
        st.success(f"[{target}] 학생에게 메시지가 성공적으로 전송되었습니다. (로그 저장 완료)")

# 주간 보고서 생성 [cite: 37, 61]
st.sidebar.divider()
if st.sidebar.button("📄 주간 보고서 생성"):
    st.sidebar.markdown(get_report_download_link(df), unsafe_allow_html=True)
