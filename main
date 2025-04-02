import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import plotly.graph_objects as go

# 데이터 로드
def load_data():
    file_path = "/mnt/data/data.xlsx"
    df = pd.read_excel(file_path)
    df.columns = df.iloc[0]  # 첫 번째 행을 컬럼으로 설정
    df = df[1:].reset_index(drop=True)  # 첫 번째 행 제거
    return df

def get_refund_amount(df, course_name, refund_date):
    # 강좌 정보 찾기
    course = df[df['주민자치센터 프로그램'] == course_name].iloc[0]
    class_day = course['요일']  # 강좌 요일
    fee = float(course['수강료'])  # 수강료
    
    # 해당 월과 요일에 따른 환불 비율 결정
    month = refund_date.month
    weekday_count = {4: 4, 5: 4, 6: 4}  # 각 월의 해당 요일 개수 (예제 기준)
    passed_classes = refund_date.day // 7  # 대략적인 진행된 수업 주차 계산
    
    if passed_classes == 0:
        refund_key = f"{month}월 1/3이하"
    elif passed_classes == 1:
        refund_key = f"{month}월 1/2이하"
    else:
        refund_key = f"{month}월 1/2초과"
    
    refund_amount = float(course[refund_key])
    return refund_amount

def generate_calendar(month, class_day):
    days = list(calendar.Calendar().itermonthdays(2025, month))
    weekdays = [calendar.day_abbr[(i % 7)] for i in range(len(days))]
    colors = ['#FFC0CB' if calendar.day_name[i % 7] == class_day else '#FFFFFF' for i in range(len(days))]
    
    fig = go.Figure(data=[go.Table(
        header=dict(values=[f"{month}월"], align='center', fill_color='lightgrey'),
        cells=dict(values=[days], align='center', fill_color=colors)
    )])
    return fig

# Streamlit UI
st.title("💰 강좌 환불 계산기")

df = load_data()
courses = df['주민자치센터 프로그램'].dropna().unique()
selected_course = st.selectbox("강좌명을 선택하세요:", courses)
refund_date = st.date_input("환불 요청 날짜를 선택하세요:", datetime.today())

if selected_course:
    class_day = df[df['주민자치센터 프로그램'] == selected_course]['요일'].values[0]
    st.subheader(f"📅 {selected_course}의 수업 요일: {class_day}")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.plotly_chart(generate_calendar(4, class_day), use_container_width=True)
    with col2:
        st.plotly_chart(generate_calendar(5, class_day), use_container_width=True)
    with col3:
        st.plotly_chart(generate_calendar(6, class_day), use_container_width=True)

if st.button("환불액 계산"):
    refund_amount = get_refund_amount(df, selected_course, refund_date)
    st.success(f"📢 환불액: {refund_amount:,.0f} 원")
