import streamlit as st
import json
import os
import datetime
import random
from openai import OpenAI

# OpenAI 설정 (Streamlit secrets에 API_KEY 저장 필요)
client = OpenAI(api_key=st.secrets["API_KEY"])

# 파일 경로 설정
base_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
history_file = os.path.join(base_dir, "waste_history.json")
settings_file = os.path.join(base_dir, "settings.json")

# 국가 평균 CO₂ 배출량
KOREA_AVG_DAILY_CO2 = 27.0
OECD_AVG_DAILY_CO2 = 30.0

# 나무 상태 이모지와 임계치
TREE_STATUS_EMOJIS = {
    "healthy": "🌳",
    "slightly_wilting": "🌲",
    "wilting": "🍂",
    "dead": "💀"
}

CO2_THRESHOLDS = {
    "healthy": 0,
    "slightly_wilting": 10,
    "wilting": 20,
    "dead": 30
}

# 다국어 메시지
messages = {
    "ko": {
        "welcome": "🌿 환경을 위한 작은 실천, 시작합니다!",
        "goodbye": "👋 이용해 주셔서 감사합니다!",
        "input_count": "몇 {unit}를 버렸나요?",
        "daily_target_prompt": "하루 CO₂ 배출 목표(kg)를 입력하세요:",
        "target_set": "✅ 목표가 설정되었습니다.",
        "over_target": "⚠️ 설정한 목표({target} kg)를 초과했습니다!",
        "result": "결과",
        "weight": "무게",
        "emitted": "배출량",
        "decompose_time": "분해 시간",
        "eco_tip": "친환경 대안",
        "today_co2_emissions": "오늘 누적 CO₂ 배출량:",
        "score": "오늘 점수:",
        "tree_status_messages": {
            "healthy": "건강합니다! 🌳 이 상태를 유지하세요!",
            "slightly_wilting": "조금 시들었어요. 🌲 탄소 배출량을 줄여주세요!",
            "wilting": "많이 시들었어요. 🍂 환경 보호에 더 신경 써주세요!",
            "dead": "나무가 죽었어요... 💀 심각한 수준입니다. 환경을 위해 노력해주세요!"
        },
        "compare_title": "📊 내 CO₂ 배출량과 평균 비교",
        "today_emission_msg": "✅ 오늘 나의 CO₂ 배출량: **{value:.2f} kg**",
        "korea_avg_msg": "🇰🇷 대한민국 1인당 일일 평균 배출량: **{value:.1f} kg**",
        "oecd_avg_msg": "🌍 OECD 평균 1인당 일일 배출량: **{value:.1f} kg**",
        "less_than_korea": "🎉 대한민국 평균보다 적게 배출했어요! 계속 유지해요!",
        "more_than_korea": "⚠️ 대한민국 평균보다 많이 배출했어요. 조금만 더 줄여볼까요?",
        "less_than_oecd": "🌱 OECD 평균보다도 낮은 배출량이에요!",
        "more_than_oecd": "🌏 OECD 평균보다 높은 배출량이에요. 다음엔 더 줄여봐요!"
    }
}

# 쓰레기 데이터
waste_data = {
    "plastic_bottle": {
        "names": {"ko": "플라스틱 병", "en": "Plastic Bottle", "zh": "塑料瓶"},
        "unit": {"ko": "병", "en": "bottle", "zh": "瓶"},
        "co2_per_kg": 6.0,
        "decompose_years": 450,
        "eco_alternative": {"ko": "텀블러를 사용하세요", "en": "Use a tumbler", "zh": "使用可重复杯"}
    },
    "can": {
        "names": {"ko": "캔", "en": "Can", "zh": "罐"},
        "unit": {"ko": "개", "en": "can", "zh": "个"},
        "co2_per_kg": 9.0,
        "decompose_years": 200,
        "eco_alternative": {"ko": "재활용하세요", "en": "Recycle it", "zh": "请回收"}
    }
}

# 친환경 명언
eco_quotes = [
    "작은 변화가 큰 차이를 만듭니다.",
    "지구는 우리가 빌린 것입니다, 후손에게 돌려주세요.",
    "Zero waste, zero regrets!"
]

# 퀴즈 데이터
quiz_data = [
    {"question": {"ko": "플라스틱 병의 분해 기간은?", "en": "...", "zh": "..."}, "answer": 450},
    {"question": {"ko": "캔의 분해 기간은?", "en": "...", "zh": "..."}, "answer": 200}
]

# JSON 파일 로드 & 저장
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# AI 질문
def ask_ai(question):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content.strip()

# Streamlit 시작
st.set_page_config(page_title="🌿 환경 배출 추적기", page_icon="🌿")
st.title(messages["ko"]["welcome"])

# 데이터 불러오기
history = load_json(history_file, {})
settings = load_json(settings_file, {"daily_target": None})

# 목표 설정
daily_target = st.number_input(
    messages["ko"]["daily_target_prompt"],
    min_value=0.0, format="%.1f",
    value=settings.get("daily_target") or 10.0
)
if st.button("목표 저장"):
    settings["daily_target"] = daily_target
    save_json(settings_file, settings)
    st.success(messages["ko"]["target_set"])

# 오늘 날짜 키
today_key = datetime.date.today().isoformat()

# 배출 기록 초기화
if today_key not in history:
    history[today_key] = []

# 쓰레기 입력
st.subheader("🗑️ 쓰레기 배출 입력")
for key, item in waste_data.items():
    count = st.number_input(
        f"{item['names']['ko']} ({item['unit']['ko']}) - 몇 개?",
        min_value=0, step=1, value=0, key=key
    )
    if count > 0:
        weight_kg = count * 0.02  # 예시 무게
        co2 = weight_kg * item["co2_per_kg"]
        history[today_key].append({
            "type": key,
            "count": count,
            "co2": co2
        })
        st.write(f"{messages['ko']['emitted']}: {co2:.2f} kg, {messages['ko']['eco_tip']}: {item['eco_alternative']['ko']}")

save_json(history_file, history)

# 오늘 총 배출량
today_total = sum(entry["co2"] for entry in history[today_key])
st.metric(messages["ko"]["today_co2_emissions"], f"{today_total:.2f} kg")

# 평균 비교
st.subheader(messages["ko"]["compare_title"])
st.write(messages["ko"]["today_emission_msg"].format(value=today_total))
st.write(messages["ko"]["korea_avg_msg"].format(value=KOREA_AVG_DAILY_CO2))
st.write(messages["ko"]["oecd_avg_msg"].format(value=OECD_AVG_DAILY_CO2))

if today_total < KOREA_AVG_DAILY_CO2:
    st.success(messages["ko"]["less_than_korea"])
else:
    st.warning(messages["ko"]["more_than_korea"])

if today_total < OECD_AVG_DAILY_CO2:
    st.info(messages["ko"]["less_than_oecd"])
else:
    st.warning(messages["ko"]["more_than_oecd"])

# 나무 상태 표시
st.subheader("🌱 오늘의 나무 상태")
status = "healthy"
for s, threshold in CO2_THRESHOLDS.items():
    if today_total >= threshold:
        status = s
emoji = TREE_STATUS_EMOJIS[status]
st.write(f"{emoji} {messages['ko']['tree_status_messages'][status]}")

# 친환경 명언
st.subheader("🌿 오늘의 친환경 명언")
st.info(random.choice(eco_quotes))

# AI에게 묻기
st.subheader("🤖 AI에게 환경 질문하기")
question = st.text_input("질문을 입력하세요:")
if st.button("AI에게 물어보기") and question:
    answer = ask_ai(question)
    st.write("AI 답변:", answer)

# 종료
st.text(messages["ko"]["goodbye"])
