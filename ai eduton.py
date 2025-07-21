pip install openai

import streamlit as st
import json
import os
import datetime
import random
import openai

# OpenAI 설정
openai.api_key = os.getenv("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")  

# 🧠 AI 질문 함수
def ask_ai(question):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "너는 친환경 전문가 AI야."},
            {"role": "user", "content": question}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

# 🌱 waste_data 
waste_data = {
    "plastic_bottle": {
        "names": {"ko": "플라스틱 병", "en": "plastic bottle", "zh": "塑料瓶"},
        "co2_per_kg": 6.0,
        "decompose_years": 450,
        "eco_alternative": {"ko": "텀블러를 사용하세요", "en": "Use a tumbler", "zh": "使用保温杯"},
        "unit": {"ko": "병", "en": "bottle", "zh": "瓶"},
        "unit_weight": 0.02
    },
    "paper_cup": {
        "names": {"ko": "종이컵", "en": "paper cup" , "zh": "纸杯"},
        "co2_per_kg": 1.2,
        "decompose_years": 20,
        "eco_alternative": {"ko": "세척 가능한 컵을 사용하세요", "en": "Use a washable cup", "zh": "请使用可清洗的杯子"},
        "unit": {"ko": "컵", "en": "cup", "zh": "个"},
        "unit_weight": 0.012
    },
    "paper": {
        "names": {"ko": "종이", "en": "paper", "zh": "纸"},
        "co2_per_kg": 1.0,
        "decompose_weeks": 4,
        "eco_alternative": {"ko": "전자문서나 양면 인쇄를 사용하세요", "en": "Use electronic documents or double-sided printing", "zh": "使用电子文件或双面打印"},
        "unit": {"ko": "장", "en": "piece", "zh": "张"},
        "unit_weight": 0.005
    },
    "aluminum_can": {
        "names": {"ko": "알루미늄 캔", "en": "aluminum can", "zh": "铝罐"},
        "co2_per_kg": 10.0,
        "decompose_years": 200,
        "eco_alternative": {"ko": "재사용 가능한 물병을 사용하세요", "en": "Use a reusable water bottle", "zh": "请使用可重复使用的水瓶"},
        "unit": {"ko": "개", "en": "can", "zh": "个"},
        "unit_weight": 0.015
    },
    "cigarette": {
        "names": {"ko": "담배꽁초", "en": "cigarette butt", "zh": "烟蒂"},
        "co2_per_kg": 3.0,
        "decompose_years": 12,
        "eco_alternative": {"ko": "금연하거나 친환경 필터를 사용하세요", "en": "Quit smoking or use eco-friendly filters", "zh": "戒烟或使用环保滤嘴"},
        "unit": {"ko": "개비", "en": "cigarette", "zh": "根"},
        "unit_weight": 0.001
    },
    "disposable_cup": {
        "names": {"ko": "일회용 컵", "en": "disposable cup", "zh": "一次性杯子"},
        "co2_per_kg": 4.0,
        "decompose_years": 450,
        "eco_alternative": {"ko": "텀블러나 머그컵을 사용하세요", "en": "Use a tumbler or mug", "zh": "请使用随行杯或马克杯"},
        "unit": {"ko": "개", "en": "cup", "zh": "个"},
        "unit_weight": 0.01
    },
    "plastic_bag": {
        "names": {"ko": "비닐봉지", "en": "plastic bag", "zh": "塑料袋"},
        "co2_per_kg": 6.0,
        "decompose_years": 1000,
        "eco_alternative": {"ko": "장바구니를 사용하세요", "en": "Use a shopping bag", "zh": "请使用购物袋"},
        "unit": {"ko": "봉지", "en": "bag", "zh": "袋"},
        "unit_weight": 0.005
    },
    "paper_cup": {
        "names": {"ko": "종이컵", "en": "paper cup", "zh": "纸杯"},
        "co2_per_kg": 1.2,
        "decompose_years": 20,
        "eco_alternative": {"ko": "세척 가능한 컵을 사용하세요", "en": "Use a washable cup", "zh": "请使用可清洗的杯子"},
        "unit": {"ko": "컵", "en": "cup", "zh": "个"},
        "unit_weight": 0.012
    },
    "glass_bottle": {
        "names": {"ko": "유리병", "en": "glass bottle", "zh": "玻璃瓶"},
        "co2_per_kg": 1.5,
        "decompose_years": 1000000,
        "eco_alternative": {"ko": "리필 스테이션을 이용하세요", "en": "Use refill stations", "zh": "请使用补充站"},
        "unit": {"ko": "개", "en": "bottle", "zh": "个"},
        "unit_weight": 0.4
    },
    "tissue": {
        "names": {"ko": "휴지", "en": "tissue", "zh": "纸巾"},
        "co2_per_kg": 0.6,
        "decompose_weeks": 3,
        "eco_alternative": {"ko": "손수건을 사용하세요", "en": "Use a handkerchief", "zh": "请使用手帕"},
        "unit": {"ko": "개", "en": "piece", "zh": "张"},
        "unit_weight": 0.005
    },
    "paper_pack": {
        "names": {"ko": "종이팩", "en": "paper pack", "zh": "纸盒"},
        "co2_per_kg": 1.1,
        "decompose_years": 5,
        "eco_alternative": {"ko": "리필팩을 사용하거나 재활용하세요", "en": "Use refill packs or recycle", "zh": "请使用补充装或回收利用"},
        "unit": {"ko": "개", "en": "pack", "zh": "个"},
        "unit_weight": 0.03
    }
}

# 🧩 quiz_data 
quiz_data = [
    {"question": {"ko": "플라스틱 병이 분해되려면 몇 년이 걸릴까요?", "en": "How many years does it take for a plastic bottle to decompose?", "zh": "一个塑料瓶需要多少年才能分解？"}, "answer": "450"},
    {"question": {"ko": "종이가 분해되려면 몇 주가 걸릴까요?", "en": "How many weeks does it take for paper to decompose?", "zh": "纸张需要几周才能分解？"}, "answer": "4"},
    {"question": {"ko": "담배꽁초가 분해되려면 몇 년이 걸릴까요?", "en": "How many years does it take for a cigarette butt to decompose?", "zh": "一个烟蒂需要多少年才能分解？"}, "answer": "12"},
    {"question": {"ko": "유리가 분해되려면 몇 년이 걸릴까요?", "en": "How many years does it take for glass to decompose?", "zh": "玻璃需要多少年才能分解？"}, "answer": "1000000"},
    {"question": {"ko": "환경 보호의 3R 중 첫 번째는 무엇인가요? (줄이기/재사용/재활용)", "en": "What is the first of the 3Rs? (Reduce/Reuse/Recycle)", "zh": "环保3R中的第一个是什么？（减少/重复使用/回收）"}, "answer": {"ko": "줄이기", "en": "Reduce", "zh": "减少"}},
    {"question": {"ko": "지구의 대체 행성이 있다(O/X)?", "en": "Is there an alternative planet to Earth? (O/X)", "zh": "地球有替代行星吗？（O/X）"}, "answer": "X"},
    {"question": {"ko": "전기 대신 자연광을 이용하면 에너지를 (절약한다/낭비한다)?", "en": "Using natural light instead of electricity (saves/wastes) energy?", "zh": "使用自然光代替电能是（节约/浪费）能源？"}, "answer": {"ko": "절약한다", "en": "saves", "zh": "节约"}},
    {"question": {"ko": "비닐봉지 분해에는 약 몇 년?", "en": "About how many years does it take for a plastic bag to decompose?", "zh": "一个塑料袋大约需要多少年才能分解？"}, "answer": "1000"},
    {"question": {"ko": "해수면 상승 주요 원인은? (빙하가 녹음/비가 많이 옴/화산 폭발)", "en": "Main cause of rising sea levels? (Melting glaciers/More rain/Volcano eruption)", "zh": "海平面上升的主要原因？（冰川融化/降雨多/火山爆发）"}, "answer": {"ko": "빙하가 녹음", "en": "Melting glaciers", "zh": "冰川融化"}},
    {"question": {"ko": "기후 변화 주요 원인 중 하나는? (이산화탄소/질소/수소)", "en": "One main cause of climate change? (Carbon dioxide/Nitrogen/Hydrogen)", "zh": "气候变化的主要原因之一？（二氧化碳/氮气/氢气）"}, "answer": {"ko": "이산화탄소", "en": "Carbon dioxide", "zh": "二氧化碳"}},
    {"question": {"ko": "가장 친환경적인 교통수단? (자전거/자동차/비행기)", "en": "Which is the most eco-friendly transport? (Bicycle/Car/Airplane)", "zh": "最环保的交通方式是？（自行车/汽车/飞机）"}, "answer": {"ko": "자전거", "en": "Bicycle", "zh": "自行车"}},
    {"question": {"ko": "에너지를 아끼는 행동은? (대기전력 차단/에어컨 계속 켜기/TV 켜두기)", "en": "Which action saves energy? (Unplug devices/Keep AC on/Leave TV on)", "zh": "节约能源的做法是？（拔掉插头/一直开空调/开着电视）"}, "answer": {"ko": "대기전력 차단", "en": "Unplug devices", "zh": "拔掉插头"}},
    {"question": {"ko": "휴지를 대신할 수 있는 친환경 대안은?", "en": "What is an eco-friendly alternative to tissues?", "zh": "替代纸巾的环保选择是什么？"}, "answer": {"ko": "손수건", "en": "Handkerchief", "zh": "手帕"}}
]


# 🌍 다국어 메시지
messages = {
    "ko": {"welcome": "🌿 환경을 위한 작은 실천, 시작!", "input_count": "몇 {unit}을 버렸나요? ", "result": "결과"},
    "en": {"welcome": "🌿 Let's start small actions!", "input_count": "How many {unit}? ", "result": "Result"},
    "zh": {"welcome": "🌿 开始小改变！", "input_count": "多少{unit}？", "result": "结果"}
}

# 📊 파일 경로
base_dir = os.path.dirname(os.path.abspath(__file__))
history_file = os.path.join(base_dir, "waste_history.json")
settings_file = os.path.join(base_dir, "settings.json")

# 📦 데이터 로드/저장 함수
@st.cache_data
def load_history():
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@st.cache_data
def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"daily_target": None}

def save_history(history):
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def save_settings(settings):
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

# ♻️ 쓰레기 입력 결과 계산
def calculate_impact(waste_key, count, lang):
    data = waste_data[waste_key]
    weight_kg = count * data["unit_weight"]
    co2 = weight_kg * data["co2_per_kg"]
    return {
        "waste_key": waste_key,
        "count": count,
        "unit": data["unit"][lang],
        "weight_kg": weight_kg,
        "co2_emitted": co2,
        "eco_tip": data["eco_alternative"][lang],
        "date": datetime.datetime.today().strftime("%Y-%m-%d")
    }

# 🪴 AI 챗봇 UI
def display_ai_chat(lang):
    st.header({"ko": "💡 AI 친환경 상담", "en": "💡 AI Eco Chat", "zh": "💡 AI环保咨询"}[lang])
    user_question = st.text_area({"ko": "궁금한 것:", "en": "Your question:", "zh": "你的问题:"}[lang])
    if st.button({"ko": "AI에게 물어보기", "en": "Ask AI", "zh": "问AI"}[lang]):
        if user_question.strip():
            answer = ask_ai(user_question)
            st.markdown(f"**🤖 {answer}**")
        else:
            st.warning({"ko": "질문을 입력하세요.", "en": "Please enter a question.", "zh": "请输入问题."}[lang])

# 🖥️ 메인 앱
def app():
    if 'current_language' not in st.session_state:
        st.session_state['current_language'] = "ko"
    if 'history' not in st.session_state:
        st.session_state['history'] = load_history()
    if 'settings' not in st.session_state:
        st.session_state['settings'] = load_settings()

    lang = st.session_state['current_language']

    st.title(messages[lang]["welcome"])

    # 🏠 메뉴
    menu_options = {
        "ko": ["쓰레기 입력", "AI 친환경 상담"],
        "en": ["Enter waste", "AI Eco Chat"],
        "zh": ["输入垃圾", "AI环保咨询"]
    }
    choice = st.sidebar.radio("메뉴:", menu_options[lang])

    if choice == menu_options[lang][0]:  # 쓰레기 입력
        waste_names = [v["names"][lang] for v in waste_data.values()]
        selected = st.selectbox("종류 선택", waste_names)
        waste_key = next(k for k, v in waste_data.items() if v["names"][lang] == selected)
        count = st.number_input(messages[lang]["input_count"].format(unit=waste_data[waste_key]["unit"][lang]),
                                min_value=0.0, value=0.0, step=1.0)
        if st.button("저장"):
            result = calculate_impact(waste_key, count, lang)
            st.session_state['history'].append(result)
            save_history(st.session_state['history'])
            st.subheader(messages[lang]["result"])
            st.write(result)

    elif choice == menu_options[lang][1]:  # AI 챗봇
        display_ai_chat(lang)

if __name__ == "__main__":
    app()
