import streamlit as st
import pandas as pd
import locale
from datetime import datetime, timedelta

import calendar
import plotly.figure_factory as ff
import plotly.graph_objects as go

# 로케일 설정 (한글 월/요일 표시)
locale.setlocale(locale.LC_TIME, "ko_KR.UTF-8")

# 데이터 로드 함수
def load_data():
    file_path = "C:/Users/hyunji/Documents/playground/refund_app/data2.xlsx"
    df = pd.read_excel(file_path)
    df.columns = df.iloc[0]  # 첫 번째 행을 컬럼으로 설정
    df = df[1:].reset_index(drop=True)  # 첫 번째 행 제거
    df = df.set_index('주민자치센터 프로그램')  # 강좌명을 인덱스로 설정
    return df

# 특정 달의 특정 요일 개수 계산 함수
def count_weekday_in_month(year, month, weekday):
    count = 0
    date = datetime(year, month, 1)
    while date.month == month:
        if date.weekday() == weekday:  # 0=월요일, 6=일요일
            count += 1
        date += timedelta(days=1)
    return count

def generate_html_table(refund_df):
    table_html = f"""
    <style>
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 16px;
            text-align: center;
            margin-top: 10px;
        }}
        th {{
            background-color: #f2f2f2;
            padding: 10px;
            border: 1px solid #ddd;
        }}
        td {{
            padding: 10px;
            border: 1px solid #ddd;
        }}
        .highlight {{
            font-weight: bold;
        }}
        .highlight2 {{
            font-weight: bold;
            color: #d9534f;  /* 강조 색상 (붉은 계열) */
            background-color: #fee7bd;  /* 노란색 배경 */
        }}
    </style>
    <table>
        <tr>
            <th>강좌명</th> <th>요일</th> <th>총 횟수</th> <th>4월</th> <th>5월</th> <th>6월</th> <th>비율</th> <th>환불 기준</th>
        </tr>
        <tr>
            <td>{refund_df['강좌명'][0]}</td>
            <td class="highlight">{refund_df['요일'][0]}</td>
            <td>{refund_df['총 횟수'][0]}</td>
            <td>{refund_df['4월'][0]}</td>
            <td>{refund_df['5월'][0]}</td>
            <td>{refund_df['6월'][0]}</td>
            <td class="highlight2">{refund_df['Ratio'][0]}</td>
            <td>{refund_df['Refund Type'][0]}</td>
        </tr>
    </table>
    """
    return table_html



# 환불 계산 함수
def calculate_refund(selected_course, refund_date, df):
    refund_date = refund_date + timedelta(days=1)  # 익일 기준 적용
    year, month, day = refund_date.year, refund_date.month, refund_date.day
    
    course_data = df.loc[selected_course]
    fee = course_data.get('수강료', 0)
    class_days = course_data.get('요일', "정보 없음")
    total_classes = course_data.get('전체 수업횟수', 0)
    count1 = course_data.get('4월 수업횟수', 0)
    count2 = course_data.get('5월 수업횟수', 0)
    count3 = course_data.get('6월 수업횟수', 0)
    
    month_data = {4: count1, 5: count2, 6: count3}
    
    # 수업 요일이 없을 경우 예외 처리
    if class_days == "정보 없음":
        return "📌 해당 강좌의 요일 정보가 없습니다."
    
    # 수업 요일을 숫자로 변환
    weekdays_map = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}
    class_weekdays = [weekdays_map[day] for day in class_days.split('/')]
    
    # 해당 달의 해당 요일 개수 구하기
    class_count_in_month = sum(count_weekday_in_month(year, month, wd) for wd in class_weekdays)
    
    # 해당 달에 이미 수강한 수업 횟수 계산
    past_classes = sum(1 for d in range(1, day) if datetime(year, month, d).weekday() in class_weekdays)
    
    # 비율 계산
    if class_count_in_month == 0:
        return "📌 해당 달에 수업 일정이 없습니다."
    
    ratio = past_classes / class_count_in_month
    
    # 환불 기준 결정
    if ratio <= 0.333:
        refund_type = f"{month}월 1/3 전"
    elif ratio <= 0.5:
        refund_type = f"{month}월 1/2 전"
    else:
        refund_type = f"{month}월 1/2 후"
    
    # 결과를 데이터프레임으로 변환하여 출력
    refund_df = pd.DataFrame({
        "강좌명": [selected_course],
        "요일": [class_days],
        "총 횟수": [total_classes],
        "4월": [count1],
        "5월": [count2],
        "6월": [count3],
        "Ratio": [ratio],  # 소수점 2자리로 반올림
        "Refund Type": [refund_type]
    })
    
    # 소수점 2자리까지 포맷팅
    refund_df["Ratio"] = refund_df["Ratio"].map(lambda x: f"{x:.2f}")
    return refund_df, refund_type, past_classes, class_count_in_month  
                      # 🚀 refund_type도 반환!, 뒤에 두개는 ratio계산과정 보여주려고


# 데이터 로드
df = load_data()

# 🎯 Streamlit UI
st.write("엄마 화이팅❤️‍🔥😍😍")
st.title("💰 프로그램 환불 계산기")

# 강좌 선택
courses = df.index.unique()
selected_course = st.selectbox("강좌명을 선택하세요:", courses)
class_days = df.loc[selected_course, "요일"] if selected_course in df.index else "정보 없음" #캘린더를 위해해

# 환불 날짜 선택
refund_date = st.date_input("환불 요청 날짜를 선택하세요:", datetime.today())
year, month = refund_date.year, refund_date.month #캘린더를 위해


## 환불 계산 및 출력
if selected_course:
    result, refund_type, past_classes, class_count_in_month = calculate_refund(selected_course, refund_date, df)  # 🚀 refund_type 추가

    if result is not None:
        st.write("### 📋 강좌 및 환불 정보")
        st.markdown(generate_html_table(result), unsafe_allow_html=True)

        # 표 아래에 비율 계산식 출력
        st.success(f"📊 비율 계산: {past_classes} / {class_count_in_month} = {float(past_classes) / class_count_in_month:.2f}")

        # 환불 금액 조회
        raw_refund_amount = df.loc[selected_course, refund_type] if refund_type in df.columns else "해당 없음"

        if isinstance(raw_refund_amount, (int, float)):
            # 소수점 3자리까지 표시
            refund_amount = f"{raw_refund_amount:.3f}"
            # 최종 환불금액 (일의 자리에서 버림)
            final_refund_amount = int(raw_refund_amount // 10 * 10)
            
        else:
            refund_amount = raw_refund_amount
            final_refund_amount = "해당 없음"

        
        # Streamlit에서 별도로 출력
        st.subheader(" ")
        st.markdown(f"""
        ### 🪄 환불 계산 결과  
        **환불 기준:** `{refund_type}`  
        **계산 결과:** <span style="font-size:24px; font-weight:bold; color:green;">{refund_amount}</span> 원  
        **최종 환불금액:** <span style="font-size:24px; font-weight:bold; color:blue;">{final_refund_amount}</span> 원
        """, unsafe_allow_html=True)
    else:
        st.warning(refund_type)  # 오류 메시지 출력


def generate_calendar(year, month, class_days):
    cal = calendar.Calendar(firstweekday=6)  # ⬅️ 일요일을 첫 번째 요일로 설정
    month_days = cal.monthdayscalendar(year, month)
    days_of_week = ["일","월", "화", "수", "목", "금", "토"]

    table_data = [["일", "월", "화", "수", "목", "금", "토"]]  # 요일 헤더 추가
    for week in month_days:
        row = []
        for j, day in enumerate(week):
            row.append(str(day) if day != 0 else "")
        table_data.append(row)

    # 헤더와 셀에 개별 색상 적용
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=table_data[0],  # 헤더
                    fill_color="#4A4A4A",  # 진한 회색
                    font=dict(color="white"),  # 흰색 글씨
                    align="center",
                ),
                cells=dict(
                    values=[list(col) for col in zip(*table_data[1:])],  # 데이터 부분
                    #fill_color=[
                        #["#EAEAEA" if days_of_week[i] in class_days else "white"] * len(table_data[1:])
                        #for i in range(7)
                    #],  # 수업 요일만 연한 회색
                    align="center",
                ),
            )
        ]
    )

    return fig


# 캘린더 생성 & 표시
# 🚨 예외 처리: 수업 요일 정보가 없을 경우
st.header("")
if class_days == "정보 없음":
    st.error("⚠️ 해당 강좌의 요일 정보가 없습니다!")
else:
    class_days_list = class_days.split("/")  # '/'로 분리된 요일 리스트

    # 🌟 가로로 캘린더 3개 배치 🌟
    col1, col2, col3 = st.columns(3)  # 3개 칼럼 생성

    with col1:
        st.write("<div style='text-align: center; font-size: 24px; font-weight: bold;'> 4월</div>", unsafe_allow_html=True)
        st.plotly_chart(generate_calendar(year, 4, class_days_list))

    with col2:
        st.write("<div style='text-align: center; font-size: 24px; font-weight: bold;'> 5월</div>", unsafe_allow_html=True)
        st.plotly_chart(generate_calendar(year, 5, class_days_list))

    with col3:
        st.write("<div style='text-align: center; font-size: 24px; font-weight: bold;'> 6월</div>", unsafe_allow_html=True)
        st.plotly_chart(generate_calendar(year, 6, class_days_list))
