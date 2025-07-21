import streamlit as st
import json
import os
import datetime
import random
from openai import OpenAI

# OpenAI 설정
client = OpenAI(api_key=st.secrets["API_KEY"])

def ask_ai(question):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "너는 친환경 전문가 AI야."},
            {"role": "user", "content": question}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

# --- CO2 평균 배출량 상수 ---
KOREA_AVG_DAILY_CO2 = 27.0  # kg, 대한민국 1인당 일일 CO₂ 배출량 예시
OECD_AVG_DAILY_CO2 = 30.0   # kg, OECD 평균 1인당 일일 CO₂ 배출량 예시

# 쓰레기 종류 다국어 버전
waste_data = {
    "plastic_bottle": {
        "names": {"ko": "플라스틱 병", "en": "plastic bottle", "zh": "塑料瓶"},
        "co2_per_kg": 6.0,
        "decompose_years": 450,
        "eco_alternative": {
            "ko": "텀블러를 사용하세요",
            "en": "Use a tumbler",
            "zh": "使用保温杯"
        },
        "unit": {"ko": "병", "en": "bottle", "zh": "瓶"},
        "unit_weight": 0.04
    },
    "plastic_bag": {
        "names": {"ko": "비닐봉지", "en": "plastic bag", "zh": "塑料袋"},
        "co2_per_kg": 6.0,
        "decompose_years": 400,
        "eco_alternative": {
            "ko": "장바구니를 사용하세요",
            "en": "Use a shopping bag",
            "zh": "使用购物袋"
        },
        "unit": {"ko": "개", "en": "piece", "zh": "个"},
        "unit_weight": 0.01
    },
    "paper": {
        "names": {"ko": "종이", "en": "paper", "zh": "纸"},
        "co2_per_kg": 1.0,
        "decompose_months": 3,
        "eco_alternative": {
            "ko": "디지털 문서를 활용하세요",
            "en": "Use digital documents",
            "zh": "使用电子文档"
        },
        "unit": {"ko": "장", "en": "sheet", "zh": "张"},
        "unit_weight": 0.005
    },
    "can": {
        "names": {"ko": "캔", "en": "can", "zh": "罐头"},
        "co2_per_kg": 8.0,
        "decompose_years": 50,
        "eco_alternative": {
            "ko": "재활용을 생활화하세요",
            "en": "Practice recycling",
            "zh": "养成回收习惯"
        },
        "unit": {"ko": "개", "en": "piece", "zh": "个"},
        "unit_weight": 0.015
    },
    "glass_bottle": {
        "names": {"ko": "유리병", "en": "glass bottle", "zh": "玻璃瓶"},
        "co2_per_kg": 2.0,
        "decompose_years": 1000,
        "eco_alternative": {
            "ko": "재사용 가능한 용기를 사용하세요",
            "en": "Use reusable containers",
            "zh": "使用可重复使用的容器"
        },
        "unit": {"ko": "병", "en": "bottle", "zh": "瓶"},
        "unit_weight": 0.2
    },
    "styrofoam": {
        "names": {"ko": "스티로폼", "en": "styrofoam", "zh": "泡沫塑料"},
        "co2_per_kg": 14.0,
        "decompose_years": 500,
        "eco_alternative": {
            "ko": "스티로폼 사용 줄이기",
            "en": "Reduce styrofoam use",
            "zh": "减少泡沫塑料使用"
        },
        "unit": {"ko": "개", "en": "piece", "zh": "个"},
        "unit_weight": 0.03
    }
}

# 환경 퀴즈 데이터
quiz_data = [
    {
        "question": {
            "ko": "플라스틱 병을 재활용하면 CO₂ 배출을 얼마나 줄일 수 있나요?",
            "en": "How much can CO₂ emissions be reduced by recycling plastic bottles?",
            "zh": "回收塑料瓶可以减少多少二氧化碳排放？"
        },
        "options": {
            "ko": ["10%", "50%", "80%", "90%"],
            "en": ["10%", "50%", "80%", "90%"],
            "zh": ["10%", "50%", "80%", "90%"]
        },
        "answer": 2
    },
    {
        "question": {
            "ko": "종이를 재활용하면 나무 몇 그루를 살릴 수 있을까요?",
            "en": "How many trees can be saved by recycling paper?",
            "zh": "回收纸张可以拯救多少棵树？"
        },
        "options": {
            "ko": ["1그루", "5그루", "10그루", "100그루"],
            "en": ["1 tree", "5 trees", "10 trees", "100 trees"],
            "zh": ["1棵", "5棵", "10棵", "100棵"]
        },
        "answer": 1
    }
]

# 메시지 다국어
messages = {
    "ko": {
        "welcome": "친환경 생활에 오신 것을 환영합니다!",
        "select_language": "언어를 선택하세요:",
        "input_waste": "쓰레기 종류를 선택하세요:",
        "input_count": "배출한 수량을 입력하세요:",
        "invalid_input": "올바른 숫자를 입력하세요.",
        "record_saved": "배출량이 저장되었습니다.",
        "today_emission": "오늘의 CO₂ 배출량",
        "eco_score": "친환경 점수",
        "set_daily_target": "하루 목표 CO₂ 배출량을 설정하세요 (kg):",
        "target_saved": "목표가 저장되었습니다.",
        "quiz_title": "환경 퀴즈",
        "quiz_correct": "정답입니다!",
        "quiz_incorrect": "틀렸습니다. 다시 시도하세요.",
        "tree_status_messages": {
            "healthy": "나무가 건강해요! 계속 좋은 습관을 유지하세요.",
            "slightly_wilting": "나무가 조금 시들었어요. 조금 더 노력해봐요.",
            "wilting": "나무가 시들었어요. 친환경 습관이 필요해요.",
            "dead": "나무가 죽었어요. 배출량을 줄여야 해요."
        }
    },
    "en": {
        "welcome": "Welcome to Eco-Friendly Living!",
        "select_language": "Select your language:",
        "input_waste": "Select waste type:",
        "input_count": "Enter quantity disposed:",
        "invalid_input": "Please enter a valid number.",
        "record_saved": "Emission recorded.",
        "today_emission": "Today's CO₂ Emissions",
        "eco_score": "Eco Score",
        "set_daily_target": "Set daily CO₂ emission target (kg):",
        "target_saved": "Target saved.",
        "quiz_title": "Eco Quiz",
        "quiz_correct": "Correct!",
        "quiz_incorrect": "Incorrect, try again.",
        "tree_status_messages": {
            "healthy": "The tree is healthy! Keep up the good habits.",
            "slightly_wilting": "The tree is slightly wilting. Try a bit harder.",
            "wilting": "The tree is wilting. Eco habits are needed.",
            "dead": "The tree is dead. Emissions must be reduced."
        }
    },
    "zh": {
        "welcome": "欢迎来到环保生活！",
        "select_language": "请选择语言：",
        "input_waste": "选择垃圾种类：",
        "input_count": "输入投放数量：",
        "invalid_input": "请输入有效数字。",
        "record_saved": "排放量已记录。",
        "today_emission": "今日二氧化碳排放量",
        "eco_score": "环保分数",
        "set_daily_target": "设置每日二氧化碳排放目标（千克）：",
        "target_saved": "目标已保存。",
        "quiz_title": "环保测验",
        "quiz_correct": "正确！",
        "quiz_incorrect": "错误，请再试一次。",
        "tree_status_messages": {
            "healthy": "树木健康！继续保持好习惯。",
            "slightly_wilting": "树木有点枯萎了。再加把劲。",
            "wilting": "树木枯萎了。需要环保习惯。",
            "dead": "树木死亡。必须减少排放。"
        }
    }
}
compare_messages = {
    "ko": {
        "header": "📊 내 CO₂ 배출량과 평균 비교",
        "today_co2": "✅ 오늘 나의 CO₂ 배출량: **{value:.2f} kg**",
        "korea_avg": "🇰🇷 대한민국 1인당 일일 평균 배출량: **{value:.1f} kg**",
        "oecd_avg": "🌍 OECD 평균 1인당 일일 배출량: **{value:.1f} kg**",
        "less_than_korea": "🎉 대한민국 평균보다 적게 배출했어요! 계속 유지해요!",
        "more_than_korea": "⚠️ 대한민국 평균보다 많이 배출했어요. 조금만 더 줄여볼까요?",
        "less_than_oecd": "🌱 OECD 평균보다도 낮은 배출량이에요!",
        "more_than_oecd": "🌏 OECD 평균보다 높은 배출량이에요. 다음엔 더 줄여봐요!"
    },
    "en": {
        "header": "📊 Compare My CO₂ Emissions with Averages",
        "today_co2": "✅ My CO₂ emissions today: **{value:.2f} kg**",
        "korea_avg": "🇰🇷 South Korea's average daily per capita: **{value:.1f} kg**",
        "oecd_avg": "🌍 OECD average daily per capita: **{value:.1f} kg**",
        "less_than_korea": "🎉 You emitted less than the South Korea average! Keep it up!",
        "more_than_korea": "⚠️ You emitted more than the South Korea average. Let's try to reduce it!",
        "less_than_oecd": "🌱 Your emissions are below the OECD average!",
        "more_than_oecd": "🌏 Your emissions are above the OECD average. Try to reduce next time!"
    },
    "zh": {
        "header": "📊 我的CO₂排放量与平均值比较",
        "today_co2": "✅ 我今天的CO₂排放量: **{value:.2f} kg**",
        "korea_avg": "🇰🇷 韩国人均每日平均排放量: **{value:.1f} kg**",
        "oecd_avg": "🌍 OECD人均每日平均排放量: **{value:.1f} kg**",
        "less_than_korea": "🎉 你的排放量低于韩国平均水平！继续保持！",
        "more_than_korea": "⚠️ 你的排放量高于韩国平均水平。试着减少排放吧！",
        "less_than_oecd": "🌱 你的排放量低于OECD平均水平！",
        "more_than_oecd": "🌏 你的排放量高于OECD平均水平。下次努力减少！"
    }
}


eco_quotes = [
    "작은 실천이 큰 변화를 만듭니다.",
    "환경을 생각하는 하루가 더 나은 미래를 만듭니다.",
    "지구는 우리 모두의 집입니다.",
    "쓰레기 줄이기, 지구 살리기의 시작입니다.",
    "친환경은 선택이 아닌 필수입니다."
]

TREE_STATUS_EMOJIS = {
    "healthy": "🌳",
    "slightly_wilting": "🌲",
    "wilting": "🍂",
    "dead": "🪵"
}

CO2_THRESHOLDS = {
    "healthy": 2.0,
    "slightly_wilting": 5.0,
    "wilting": 10.0
}

@st.cache_data
def load_history():
    history_file = "waste_history.json"
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@st.cache_data
def load_settings():
    settings_file = "settings.json"
    if os.path.exists(settings_file):
        with open(settings_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"daily_target": None}

def save_history(history):
    with open("waste_history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def save_settings(settings):
    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

def calculate_impact(waste_key, count, lang):
    data = waste_data[waste_key]
    weight_kg = count * data["unit_weight"]
    co2 = weight_kg * data["co2_per_kg"]

    decompose = ""
    if "decompose_years" in data:
        decompose = f"{data['decompose_years']}년" if lang=="ko" else \
                    f"{data['decompose_years']} years" if lang=="en" else \
                    f"{data['decompose_years']}年"
    elif "decompose_months" in data:
        decompose = f"{data['decompose_months']}개월" if lang=="ko" else \
                    f"{data['decompose_months']} months" if lang=="en" else \
                    f"{data['decompose_months']}个月"
    elif "decompose_weeks" in data:
        decompose = f"{data['decompose_weeks']}주" if lang=="ko" else \
                    f"{data['decompose_weeks']} weeks" if lang=="en" else \
                    f"{data['decompose_weeks']}周"

    return {
        "waste_key": waste_key,
        "count": count,
        "unit": data["unit"][lang],
        "weight_kg": weight_kg,
        "co2_emitted": co2,
        "decompose_time": decompose,
        "eco_tip": data["eco_alternative"][lang],
        "date": datetime.datetime.today().strftime("%Y-%m-%d")
    }

def get_today_co2_and_score(history):
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    today_records = [r for r in history if r["date"] == today]
    total_co2 = sum(r["co2_emitted"] for r in today_records)
    eco_score = max(0, 100 - total_co2 * 5)
    return total_co2, eco_score

def get_tree_status(total_co2):
    if total_co2 < CO2_THRESHOLDS["healthy"]:
        return "healthy"
    elif total_co2 < CO2_THRESHOLDS["slightly_wilting"]:
        return "slightly_wilting"
    elif total_co2 < CO2_THRESHOLDS["wilting"]:
        return "wilting"
    else:
        return "dead"

def display_eco_quiz(lang):
    st.header(messages[lang]["quiz_title"])
    quiz = random.choice(quiz_data)

    st.write(quiz["question"][lang])

    options = quiz["options"][lang]
    answer_index = quiz["answer"]
    user_answer = st.radio("선택하세요:", options, key="quiz_answer")

    if st.button("제출", key="quiz_submit"):
        if user_answer == options[answer_index]:
            st.success(messages[lang]["quiz_correct"])
        else:
            st.error(messages[lang]["quiz_incorrect"])

def display_ai_chat(lang):
    st.header("AI 친환경 상담")
    question = st.text_input("질문을 입력하세요:" if lang=="ko" else "Enter your question:" if lang=="en" else "请输入问题：")

    if st.button("전송" if lang=="ko" else "Send" if lang=="en" else "发送"):
        if question.strip() != "":
            answer = ask_ai(question)
            st.markdown(f"**AI 답변:**\n\n{answer}")

def app():
    if 'current_language' not in st.session_state:
        st.session_state['current_language'] = "ko"
    if 'history' not in st.session_state:
        st.session_state['history'] = load_history()
    if 'settings' not in st.session_state:
        st.session_state['settings'] = load_settings()

    st.sidebar.title("🌐 언어 선택")
    language_options = {"ko": "한국어", "en": "English", "zh": "中文"}
    selected_language_name = st.sidebar.radio(
        "언어를 선택하세요:",
        options=list(language_options.values()),
        index=list(language_options.keys()).index(st.session_state['current_language'])
    )
    for code, name in language_options.items():
        if name == selected_language_name:
            st.session_state['current_language'] = code
            break

    lang = st.session_state['current_language']

    st.title(messages[lang]["welcome"])
    st.write(random.choice(eco_quotes))

    current_co2, _ = get_today_co2_and_score(st.session_state['history'])
    tree_status = get_tree_status(current_co2)
    tree_emoji = TREE_STATUS_EMOJIS[tree_status]
    tree_message = messages[lang]["tree_status_messages"][tree_status]

    st.markdown(
        f"<p style='text-align: center; font-size: 5em;'>{tree_emoji}</p>",
        unsafe_allow_html=True
    )
    st.write(f"<p style='text-align: center;'>현재 CO₂ 배출량: <b>{current_co2:.2f} kg</b></p>", unsafe_allow_html=True)

    if tree_status == "healthy":
        message_style = "background-color: #e6ffe6; color: #1f7a1f; padding: 10px; border-radius: 5px;"
    elif tree_status == "slightly_wilting":
        message_style = "background-color: #e6f7ff; color: #1f6b8f; padding: 10px; border-radius: 5px;"
    elif tree_status == "wilting":
        message_style = "background-color: #fff8e6; color: #a37200; padding: 10px; border-radius: 5px;"
    else:
        message_style = "background-color: #ffe6e6; color: #a30000; padding: 10px; border-radius: 5px;"

    st.markdown(
        f"<p style='text-align: center; {message_style}'><b>{tree_message}</b></p>",
        unsafe_allow_html=True
    )

    st.sidebar.title("메뉴")
    menu_options = {
        "ko": ["쓰레기 입력", "오늘 배출량 및 점수 확인", "하루 목표 설정", "환경 퀴즈", "AI챗봇", "평균 배출량과 비교"],
        "en": ["Enter waste", "View today's emissions and score", "Set daily target", "Eco Quiz", "AI Chatbot", "Compare with average"],
        "zh": ["输入垃圾", "查看今日排放量和分数", "设置每日目标", "环保测验", "AI环保咨询", "与平均值比较"]
    }

    choice = st.sidebar.radio("옵션을 선택하세요:", menu_options[lang])

    if choice == menu_options[lang][0]:
        st.header(messages[lang]["input_waste"])
        options = [waste_data[key]["names"][lang] for key in waste_data]
        selected = st.selectbox("", options)

        waste_key = None
        for key, data in waste_data.items():
            if data["names"][lang] == selected:
                waste_key = key
                break

        count = st.number_input(messages[lang]["input_count"], min_value=0, step=1)

        if st.button("저장"):
            if count <= 0:
                st.error(messages[lang]["invalid_input"])
            else:
                record = calculate_impact(waste_key, count, lang)
                st.session_state['history'].append(record)
                save_history(st.session_state['history'])
                st.success(messages[lang]["record_saved"])

                st.markdown(f"**{record['waste_key']}**: {record['count']} {record['unit']} / CO₂ 배출량: {record['co2_emitted']:.2f} kg")
                st.markdown(f"분해 기간: {record['decompose_time']}")
                st.markdown(f"친환경 팁: {record['eco_tip']}")

    elif choice == menu_options[lang][1]:
        st.header(messages[lang]["today_emission"])
        total_co2, eco_score = get_today_co2_and_score(st.session_state['history'])
        st.write(f"CO₂ 배출량: {total_co2:.2f} kg")
        st.write(f"{messages[lang]['eco_score']}: {eco_score:.0f}/100")

    elif choice == menu_options[lang][2]:
        st.header(messages[lang]["set_daily_target"])
        current_target = st.session_state['settings'].get("daily_target", None)
        new_target = st.number_input("", min_value=0.0, value=current_target if current_target else 5.0)

        if st.button("저장"):
            st.session_state['settings']["daily_target"] = new_target
            save_settings(st.session_state['settings'])
            st.success(messages[lang]["target_saved"])

    elif choice == menu_options[lang][3]:
        display_eco_quiz(lang)

    elif choice == menu_options[lang][4]:
        display_ai_chat(lang)

elif choice == menu_options[lang][5]:  # 평균 배출량과 비교
    msg = compare_messages[lang]
    st.header(msg["header"])
    today_co2, _ = get_today_co2_and_score(st.session_state['history'])

    st.write(msg["today_co2"].format(value=today_co2))
    st.write(msg["korea_avg"].format(value=KOREA_AVG_DAILY_CO2))
    st.write(msg["oecd_avg"].format(value=OECD_AVG_DAILY_CO2))

    st.bar_chart({
        "오늘 나" if lang=="ko" else "Me" if lang=="en" else "我": [today_co2],
        "대한민국 평균" if lang=="ko" else "Korea Avg" if lang=="en" else "韩国平均": [KOREA_AVG_DAILY_CO2],
        "OECD 평균" if lang=="ko" else "OECD Avg" if lang=="en" else "OECD平均": [OECD_AVG_DAILY_CO2]
    })

    if today_co2 < KOREA_AVG_DAILY_CO2:
        st.success(msg["less_than_korea"])
    else:
        st.warning(msg["more_than_korea"])

    if today_co2 < OECD_AVG_DAILY_CO2:
        st.info(msg["less_than_oecd"])
    else:
        st.info(msg["more_than_oecd"])


if __name__ == "__main__":
    app()
