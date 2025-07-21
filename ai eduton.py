import streamlit as st
import json
import os
import datetime
from openai import OpenAI

# 쓰레기 데이터
waste_data = {
    "plastic_bottle": {
        "names": {"ko": "플라스틱 병", "en": "plastic bottle", "zh": "塑料瓶"},
        "co2_per_kg": 6.0,
        "decompose_years": 450,
        "eco_alternative": {
            "ko": "텀블러를 사용하세요",
            "en": "Use a tumbler",
            "zh": "使用随行杯"
        },
        "unit": {"ko": "병", "en": "bottle", "zh": "瓶"}
    },
    "paper_cup": {
        "names": {"ko": "종이컵", "en": "paper cup", "zh": "纸杯"},
        "co2_per_kg": 2.5,
        "decompose_years": 20,
        "eco_alternative": {
            "ko": "머그컵을 사용하세요",
            "en": "Use a mug cup",
            "zh": "使用马克杯"
        },
        "unit": {"ko": "개", "en": "cup", "zh": "个"}
    },
    "food_waste": {
        "names": {"ko": "음식물 쓰레기", "en": "food waste", "zh": "厨余垃圾"},
        "co2_per_kg": 1.9,
        "decompose_years": 1,
        "eco_alternative": {
            "ko": "필요한 만큼만 조리하세요",
            "en": "Cook only what you need",
            "zh": "只烹饪需要的量"
        },
        "unit": {"ko": "kg", "en": "kg", "zh": "kg"}
    }
}

# 평균 배출량 (kg CO₂)
KOREA_AVG_DAILY_CO2 = 32.5
OECD_AVG_DAILY_CO2 = 30.0

# 파일 경로
HISTORY_FILE = 'waste_history.json'
SETTINGS_FILE = 'settings.json'

# 다국어 메시지
messages = {
    "ko": {
        "language_selection": "언어를 선택하세요:",
        "menu_title": "메뉴",
        "option_input": "배출량 입력",
        "option_compare": "평균 배출량과 비교",
        "option_ai": "AI와 대화",
        "option_history": "이전 기록 보기",
        "option_settings": "목표 설정",
        "option_about": "앱 소개",
        "today_emission_msg": "오늘 배출량: {value:.2f} kg CO₂",
        "korea_avg_msg": "대한민국 1인 평균 배출량: {value} kg CO₂",
        "oecd_avg_msg": "OECD 평균 배출량: {value} kg CO₂",
        "compare_title": "평균 배출량 비교",
        "less_than_korea": "대한민국 평균보다 적게 배출했어요!",
        "more_than_korea": "대한민국 평균보다 많이 배출했어요!",
        "less_than_oecd": "OECD 평균보다 적게 배출했어요!",
        "more_than_oecd": "OECD 평균보다 많이 배출했어요!",
        "input_title": "배출량 입력",
        "select_waste": "쓰레기 종류를 선택하세요:",
        "input_quantity": "배출량을 입력하세요 (단위: {unit}):",
        "submit": "저장",
        "success_saved": "저장되었습니다!",
        "history_title": "배출 이력",
        "settings_title": "목표 설정",
        "input_target": "일일 배출 목표 (kg CO₂):",
        "save_settings": "설정 저장",
        "settings_saved": "설정이 저장되었습니다.",
        "about_title": "앱 소개",
        "about_text": "이 앱은 다국어 지원 쓰레기 배출 추적 앱입니다.",
        "ai_title": "AI와 대화",
        "ask_question": "질문을 입력하세요:",
        "ai_response": "AI 답변:"
    },
    "en": {
        "language_selection": "Select language:",
        "menu_title": "Menu",
        "option_input": "Input waste",
        "option_compare": "Compare with average",
        "option_ai": "Chat with AI",
        "option_history": "View history",
        "option_settings": "Set target",
        "option_about": "About",
        "today_emission_msg": "Today's emission: {value:.2f} kg CO₂",
        "korea_avg_msg": "Korea average: {value} kg CO₂",
        "oecd_avg_msg": "OECD average: {value} kg CO₂",
        "compare_title": "Compare with average",
        "less_than_korea": "You emitted less than Korea average!",
        "more_than_korea": "You emitted more than Korea average!",
        "less_than_oecd": "You emitted less than OECD average!",
        "more_than_oecd": "You emitted more than OECD average!",
        "input_title": "Input waste",
        "select_waste": "Select waste type:",
        "input_quantity": "Enter quantity (unit: {unit}):",
        "submit": "Save",
        "success_saved": "Saved successfully!",
        "history_title": "Waste history",
        "settings_title": "Set target",
        "input_target": "Daily target (kg CO₂):",
        "save_settings": "Save settings",
        "settings_saved": "Settings saved.",
        "about_title": "About",
        "about_text": "This is a multilingual waste tracking app.",
        "ai_title": "Chat with AI",
        "ask_question": "Enter your question:",
        "ai_response": "AI Response:"
    },
    "zh": {
        "language_selection": "请选择语言:",
        "menu_title": "菜单",
        "option_input": "输入垃圾量",
        "option_compare": "与平均值比较",
        "option_ai": "与 AI 聊天",
        "option_history": "查看历史",
        "option_settings": "设置目标",
        "option_about": "关于",
        "today_emission_msg": "今日排放量: {value:.2f} kg CO₂",
        "korea_avg_msg": "韩国平均: {value} kg CO₂",
        "oecd_avg_msg": "OECD 平均: {value} kg CO₂",
        "compare_title": "平均值比较",
        "less_than_korea": "低于韩国平均排放量！",
        "more_than_korea": "高于韩国平均排放量！",
        "less_than_oecd": "低于 OECD 平均排放量！",
        "more_than_oecd": "高于 OECD 平均排放量！",
        "input_title": "输入垃圾量",
        "select_waste": "选择垃圾种类:",
        "input_quantity": "输入数量 (单位: {unit}):",
        "submit": "保存",
        "success_saved": "保存成功！",
        "history_title": "历史记录",
        "settings_title": "设置目标",
        "input_target": "每日排放目标 (kg CO₂):",
        "save_settings": "保存设置",
        "settings_saved": "设置已保存。",
        "about_title": "关于",
        "about_text": "这是一个支持多语言的垃圾追踪应用。",
        "ai_title": "与 AI 聊天",
        "ask_question": "输入你的问题:",
        "ai_response": "AI 回答:"
    }
}

# 메뉴 옵션
menu_options = {
    "ko": ["배출량 입력", "평균 배출량과 비교", "AI와 대화", "이전 기록 보기", "목표 설정", "앱 소개"],
    "en": ["Input waste", "Compare with average", "Chat with AI", "View history", "Set target", "About"],
    "zh": ["输入垃圾量", "与平均值比较", "与 AI 聊天", "查看历史", "设置目标", "关于"]
}

# 캐시: 기록 불러오기
@st.cache_data
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# 캐시: 설정 불러오기
@st.cache_data
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# 기록 저장
def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# 설정 저장
def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

# CO₂ 배출량 계산
def calculate_impact(waste_key, quantity):
    data = waste_data[waste_key]
    return quantity * data["co2_per_kg"]

# 오늘 날짜의 CO₂ 합산
def get_today_co2_and_score(history):
    today = datetime.date.today().isoformat()
    today_records = [h for h in history if h["date"] == today]
    total_co2 = sum(r["co2"] for r in today_records)
    return total_co2, today_records

# OpenAI 클라이언트 안전 초기화
def init_openai_client():
    try:
        return OpenAI(api_key=st.secrets["API_KEY"])
    except Exception as e:
        st.error(f"OpenAI 초기화 오류: {e}")
        return None

# --- Streamlit 앱 시작 ---
st.set_page_config(page_title="Waste Tracker", page_icon="♻️")

if "history" not in st.session_state:
    st.session_state["history"] = load_history()
if "settings" not in st.session_state:
    st.session_state["settings"] = load_settings()

lang = st.sidebar.selectbox(
    messages["ko"]["language_selection"],
    options=["ko", "en", "zh"],
    format_func=lambda l: {"ko": "한국어", "en": "English", "zh": "中文"}[l]
)

choice = st.sidebar.radio(messages[lang]["menu_title"], menu_options[lang])

# 메뉴 처리
if choice == menu_options[lang][0]:  # 배출량 입력
    st.header(messages[lang]["input_title"])
    waste_key = st.selectbox(
        messages[lang]["select_waste"],
        options=list(waste_data.keys()),
        format_func=lambda k: waste_data[k]["names"][lang]
    )
    unit = waste_data[waste_key]["unit"][lang]
    quantity = st.number_input(
        messages[lang]["input_quantity"].format(unit=unit),
        min_value=0.0, step=0.1
    )

    if st.button(messages[lang]["submit"]):
        co2 = calculate_impact(waste_key, quantity)
        record = {
            "date": datetime.date.today().isoformat(),
            "waste": waste_key,
            "quantity": quantity,
            "co2": co2
        }
        st.session_state["history"].append(record)
        save_history(st.session_state["history"])
        st.success(messages[lang]["success_saved"])

elif choice == menu_options[lang][1]:  # 평균 배출량과 비교
    st.header(messages[lang]["compare_title"])
    today_co2, _ = get_today_co2_and_score(st.session_state["history"])

    st.write(messages[lang]["today_emission_msg"].format(value=today_co2))
    st.write(messages[lang]["korea_avg_msg"].format(value=KOREA_AVG_DAILY_CO2))
    st.write(messages[lang]["oecd_avg_msg"].format(value=OECD_AVG_DAILY_CO2))

    st.bar_chart({
        "Me": [today_co2],
        "Korea avg": [KOREA_AVG_DAILY_CO2],
        "OECD avg": [OECD_AVG_DAILY_CO2]
    })

    if today_co2 < KOREA_AVG_DAILY_CO2:
        st.success(messages[lang]["less_than_korea"])
    else:
        st.warning(messages[lang]["more_than_korea"])

    if today_co2 < OECD_AVG_DAILY_CO2:
        st.info(messages[lang]["less_than_oecd"])
    else:
        st.info(messages[lang]["more_than_oecd"])

elif choice == menu_options[lang][2]:  # AI와 대화
    st.header(messages[lang]["ai_title"])
    client = init_openai_client()
    question = st.text_input(messages[lang]["ask_question"])

    if client and st.button(messages[lang]["submit"]):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": question}]
                )
                answer = response.choices[0].message.content
                st.write(f"{messages[lang]['ai_response']} {answer}")
            except Exception as e:
                st.error(f"AI 오류: {e}")

elif choice == menu_options[lang][3]:  # 기록 보기
    st.header(messages[lang]["history_title"])
    st.json(st.session_state["history"])

elif choice == menu_options[lang][4]:  # 목표 설정
    st.header(messages[lang]["settings_title"])
    target = st.number_input(
        messages[lang]["input_target"],
        min_value=0.0, step=0.1,
        value=st.session_state["settings"].get("daily_target", 0.0)
    )
    if st.button(messages[lang]["save_settings"]):
        st.session_state["settings"]["daily_target"] = target
        save_settings(st.session_state["settings"])
        st.success(messages[lang]["settings_saved"])

elif choice == menu_options[lang][5]:  # 앱 소개
    st.header(messages[lang]["about_title"])
    st.write(messages[lang]["about_text"])
