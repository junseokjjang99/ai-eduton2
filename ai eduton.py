import streamlit as st
import json
import os
import datetime
import random
import openai  # 🔧 수정: from openai import OpenAI → openai 사용

# OpenAI 설정
openai.api_key = st.secrets["API_KEY"]  # 🔧 수정: client 사용 대신 openai.api_key

# 대한민국, OECD 평균 CO₂ 배출량 (1인당, 일일, kg)
KOREA_AVG_DAILY_CO2 = 27.0
OECD_AVG_DAILY_CO2 = 30.0

# 쓰레기 데이터
waste_data = {
    "plastic_bottle": {
        "names": {"ko": "플라스틱 병", "en": "Plastic Bottle", "zh": "塑料瓶"},
        "unit": {"ko": "병", "en": "bottle", "zh": "瓶"},
        "unit_weight": 0.04, "co2_per_kg": 6.0,
        "decompose_years": 450,
        "eco_alternative": {"ko": "텀블러 사용", "en": "Use a tumbler", "zh": "使用保温杯"}
    },
    "paper": {
        "names": {"ko": "종이", "en": "Paper", "zh": "纸"},
        "unit": {"ko": "장", "en": "sheet", "zh": "张"},
        "unit_weight": 0.005, "co2_per_kg": 1.0,
        "decompose_months": 3,
        "eco_alternative": {"ko": "디지털 문서 활용", "en": "Use digital documents", "zh": "使用电子文档"}
    },
    # 필요한 다른 항목 추가 가능
}

# 이모지 및 CO₂ 상태 기준
TREE_STATUS_EMOJIS = {"healthy": "🌳", "slightly_wilting": "🌲", "wilting": "🍂", "dead": "🪵"}
CO2_THRESHOLDS = {"healthy": 2.0, "slightly_wilting": 5.0, "wilting": 10.0}

# 데이터 로드/저장
@st.cache_data
def load_history():
    if os.path.exists("waste_history.json"):
        with open("waste_history.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@st.cache_data
def load_settings():
    if os.path.exists("settings.json"):
        with open("settings.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"daily_target": None}

def save_history(history):
    with open("waste_history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def save_settings(settings):
    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

# AI 상담 함수
def ask_ai(question):
    response = openai.ChatCompletion.create(  # 🔧 수정된 Chat API 사용
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "너는 친환경 전문가 AI야."},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content.strip()

# CO₂ 및 환경 영향 계산
def calculate_impact(waste_key, count, lang):
    data = waste_data[waste_key]
    weight_kg = count * data["unit_weight"]
    co2 = weight_kg * data["co2_per_kg"]
    decompose = f"{data.get('decompose_years','')}{'년' if lang=='ko' else ' years' if lang=='en' else '年'}" \
        if 'decompose_years' in data else \
        f"{data.get('decompose_months','')}{'개월' if lang=='ko' else ' months' if lang=='en' else '个月'}"
    return {
        "waste_key": waste_key, "count": count, "weight_kg": weight_kg,
        "co2_emitted": co2, "date": datetime.date.today().isoformat(),
        "eco_tip": data["eco_alternative"][lang], "decompose_time": decompose
    }

def get_today_co2(history):
    today = datetime.date.today().isoformat()
    return sum(r["co2_emitted"] for r in history if r["date"] == today)

def get_tree_status(total_co2):
    if total_co2 < CO2_THRESHOLDS["healthy"]: return "healthy"
    elif total_co2 < CO2_THRESHOLDS["slightly_wilting"]: return "slightly_wilting"
    elif total_co2 < CO2_THRESHOLDS["wilting"]: return "wilting"
    else: return "dead"

# 앱 실행 본체
def app():
    st.set_page_config(page_title="친환경 배출 추적기 🌱", layout="centered")

    # 세션 초기화
    if "lang" not in st.session_state:
        st.session_state.lang = "ko"
    if "history" not in st.session_state:
        st.session_state.history = load_history()
    if "settings" not in st.session_state:
        st.session_state.settings = load_settings()

    # 언어 선택
    lang_map = {"ko":"한국어","en":"English","zh":"中文"}
    lang = st.sidebar.selectbox("언어 / Language", options=list(lang_map.keys()), format_func=lambda x: lang_map[x])
    st.session_state.lang = lang

    st.title("🌱 친환경 배출 추적기")
    total_co2 = get_today_co2(st.session_state.history)
    tree_status = get_tree_status(total_co2)
    st.markdown(f"### {TREE_STATUS_EMOJIS[tree_status]} 현재 상태")
    st.metric(label="오늘 배출 CO₂", value=f"{total_co2:.2f} kg")

    # 쓰레기 기록
    waste_options = [v["names"][lang] for v in waste_data.values()]
    choice = st.selectbox("쓰레기 종류 선택", options=waste_options)
    count = st.number_input("수량 입력", min_value=1, value=1)
    if st.button("저장"):
        key = [k for k,v in waste_data.items() if v["names"][lang]==choice][0]
        rec = calculate_impact(key, count, lang)
        st.session_state.history.append(rec)
        save_history(st.session_state.history)
        st.success(f"저장됨! CO₂ {rec['co2_emitted']:.2f} kg")

    # 목표 설정
    target = st.number_input("하루 목표 CO₂ (kg)", min_value=0.0, value=st.session_state.settings.get("daily_target") or 5.0)
    if st.button("목표 저장"):
        st.session_state.settings["daily_target"] = target
        save_settings(st.session_state.settings)
        st.success("목표 저장 완료")

    # 평균 비교
    st.subheader("📊 대한민국·OECD 평균 비교")
    st.bar_chart({
        "나": [total_co2],
        "한국 평균": [KOREA_AVG_DAILY_CO2],
        "OECD 평균": [OECD_AVG_DAILY_CO2]
    })

    # AI 챗봇
    st.subheader("🤖 AI 친환경 상담")
    question = st.text_input("질문 입력")
    if st.button("AI에게 물어보기"):
        if question.strip():
            answer = ask_ai(question)
            st.info(answer)

if __name__ == "__main__":
    app()
