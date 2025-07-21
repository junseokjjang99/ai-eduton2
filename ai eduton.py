import streamlit as st
import json
import os
import datetime
import random
from openai import OpenAI


KOREA_AVG_DAILY_CO2 = 27.0  
OECD_AVG_DAILY_CO2 = 30.0

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
        "unit_weight": 0.02
    },
    "food_waste": {
        "names": {"ko": "음식물 쓰레기", "en": "food waste", "zh": "厨余垃圾"},
        "co2_per_kg": 0.5,
        "decompose_months": 1,
        "eco_alternative": {
            "ko": "남기지 말고 적당량만 요리하세요",
            "en": "Cook just the right amount and don't leave leftovers",
            "zh": "适量烹饪，避免浪费"
        },
        "unit": {"ko": "인분", "en": "servings", "zh": "份"},
        "unit_weight": 0.3
    },
    "paper": {
        "names": {"ko": "종이", "en": "paper", "zh": "纸"},
        "co2_per_kg": 1.0,
        "decompose_weeks": 4,
        "eco_alternative": {
            "ko": "전자문서나 양면 인쇄를 사용하세요",
            "en": "Use electronic documents or double-sided printing",
            "zh": "使用电子文件或双面打印"
        },
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
        "names": {"ko": "담배꽁초", "en": "cigarette butt" , "zh": "烟蒂"},
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
        "names": {"ko": "종이컵", "en": "paper cup" , "zh": "纸杯"},
        "co2_per_kg": 1.2,
        "decompose_years": 20,
        "eco_alternative": {"ko": "세척 가능한 컵을 사용하세요", "en": "Use a washable cup", "zh": "请使用可清洗的杯子"},
        "unit": {"ko": "컵", "en": "cup", "zh": "个"},
        "unit_weight": 0.012
    },
    "glass_bottle": {
        "names": {"ko": "유리병", "en": "glass bottle" , "zh": "玻璃瓶"},
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

# 퀴즈 데이터
quiz_data = [
    {
        "question": {
            "ko": "플라스틱 병이 분해되려면 몇 년이 걸릴까요?",
            "en": "How many years does it take for a plastic bottle to decompose?",
            "zh": "一个塑料瓶需要多少年才能分解？"
        },
        "answer": "450"
    },
    {
        "question": {
            "ko": "종이가 분해되려면 몇 주가 걸릴까요?",
            "en": "How many weeks does it take for a paper to decompose?",
            "zh": "纸张需要几周才能分解？"
        },
        "answer": "4"
    },
    {
        "question": {
            "ko": "담배꽁초가 분해되려면 몇 년이 걸릴까요?",
            "en": "How many years does it take for a cigarette butt to decompose?",
            "zh": "一个烟蒂需要多少年才能分解？"
        },
        "answer": "12"
    },
    {
        "question": {
            "ko": "유리가 분해되려면 몇 년이 걸릴까요?",
            "en": "How many years does it take for a glass to decompose?",
            "zh": "玻璃需要多少年才能分解?"
        },
        "answer": "1000000"
    },
    {
        "question": {
            "ko": "환경 보호의 3R 중 첫 번째는 무엇인가요? (줄이기/재사용/재활용)",
            "en": "What is the first of the 3Rs for the environment? (Reduce/Reuse/Recycle)",
            "zh": "环保3R中的第一个是什么？（减少/重复使用/回收）"
        },
        "answer": {
            "ko": "줄이기",
            "en": "Reduce",
            "zh": "减少"
        }
    },
    {
        "question": {
            "ko": "지구의 대체 행성이 있다(O/X)?",
            "en": "Is there an alternative planet to Earth? (O/X)",
            "zh": "地球有替代行星吗？（O/X）"
        },
        "answer": "X"
    },
    {
        "question": {
            "ko": "전기 대신 자연광을 이용하는 행동은 에너지를 (절약한다/낭비한다)?",
            "en": "Using natural light instead of electricity (saves/wastes) energy?",
            "zh": "使用自然光代替电能是（节约/浪费）能源？"
        },
        "answer": {
            "ko": "절약한다",
            "en": "saves",
            "zh": "节约"
        }
    },
    {
        "question": {
            "ko": "비닐봉지의 평균 분해 기간은 약 몇 년인가요?",
            "en": "About how many years does it take for a plastic bag to decompose?",
            "zh": "一个塑料袋大约需要多少年才能分解？"
        },
        "answer": "1000"
    },
    {
        "question": {
            "ko": "지구의 해수면 상승 주요 원인은? (빙하가 녹음/비가 많이 옴/화산 폭발)",
            "en": "Main cause of rising sea levels? (Melting glaciers/More rain/Volcano eruption)",
            "zh": "海平面上升的主要原因？（冰川融化/降雨多/火山爆发）"
        },
        "answer": {
            "ko": "빙하가 녹음",
            "en": "Melting glaciers",
            "zh": "冰川融化"
        }
    },
    {
        "question": {
            "ko": "기후 변화의 주요 원인 중 하나는? (이산화탄소/질소/수소)",
            "en": "One main cause of climate change? (Carbon dioxide/Nitrogen/Hydrogen)",
            "zh": "气候变化的主要原因之一？（二氧化碳/氮气/氢气）"
        },
        "answer": {
            "ko": "이산화탄소",
            "en": "Carbon dioxide",
            "zh": "二氧化碳"
        }
    },
    {
        "question": {
            "ko": "가장 환경 친화적인 운송 수단은? (자전거/자동차/비행기)",
            "en": "Which is the most eco-friendly transport? (Bicycle/Car/Airplane)",
            "zh": "最环保的交通方式是？（自行车/汽车/飞机）"
        },
        "answer": {
            "ko": "자전거",
            "en": "Bicycle",
            "zh": "自行车"
        }
    },
    {
        "question": {
            "ko": "에너지를 아끼는 행동은? (대기전력 차단/에어컨 계속 켜기/TV 켜두기)",
            "en": "Which action saves energy? (Unplug devices/Keep AC on/Leave TV on)",
            "zh": "节约能源的做法是？（拔掉插头/一直开空调/开着电视）"
        },
        "answer": {
            "ko": "대기전력 차단",
            "en": "Unplug devices",
            "zh": "拔掉插头"
        }
    },
    {
        "question": {
            "ko": "휴지를 대신할 수 있는 친환경 대안은?",
            "en": "What is an eco-friendly alternative to tissues?",
            "zh": "替代纸巾的环保选择是什么？"
        },
        "answer": {
            "ko": "손수건",
            "en": "Handkerchief",
            "zh": "手帕"
        }
    }
]

# 파일 경로
base_dir = os.path.dirname(os.path.abspath(__file__))
history_file = os.path.join(base_dir, "waste_history.json")
settings_file = os.path.join(base_dir, "settings.json")

messages = {
    "ko": {
        "welcome": "🌿 환경을 위한 작은 실천, 시작합니다!",
        "select_menu": "\n1. 쓰레기 입력\n2. 오늘 배출량 및 점수 확인\n3. 하루 목표 설정\n4. 환경 퀴즈\n5. 종료\n선택하세요: ",
        "goodbye": "👋 이용해 주셔서 감사합니다!",
        "invalid_number": "❌ 숫자를 입력해주세요.",
        "invalid_menu": "❌ 올바른 메뉴 번호를 선택해주세요.",
        "input_count": "몇 {unit}를 버렸나요? ",
        "daily_target_prompt": "하루 CO₂ 배출 목표(kg)를 입력하세요: ",
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
            "dead": "나무가 죽었어요... 💀 심각한 수준입니다. 환경을 위해 노력해주세요!"},
        "compare_title": "📊 내 CO₂ 배출량과 평균 비교",
        "today_emission_msg": "✅ 오늘 나의 CO₂ 배출량: **{value:.2f} kg**",
        "korea_avg_msg": "🇰🇷 대한민국 1인당 일일 평균 배출량: **{value:.1f} kg**",
        "oecd_avg_msg": "🌍 OECD 평균 1인당 일일 배출량: **{value:.1f} kg**",
        "less_than_korea": "🎉 대한민국 평균보다 적게 배출했어요! 계속 유지해요!",
        "more_than_korea": "⚠️ 대한민국 평균보다 많이 배출했어요. 조금만 더 줄여볼까요?",
        "less_than_oecd": "🌱 OECD 평균보다도 낮은 배출량이에요!",
        "more_than_oecd": "🌏 OECD 평균보다 높은 배출량이에요. 다음엔 더 줄여봐요!"
        },
    "en": {
        "welcome": "🌿 Let's start a small action for the environment!",
        "select_menu": "\n1. Enter waste\n2. View today's emissions and score\n3. Set daily target\n4. Eco Quiz\n5. Exit\nChoose: ",
        "goodbye": "👋 Thank you for using!",
        "invalid_number": "❌ Please enter a number.",
        "invalid_menu": "❌ Invalid menu number.",
        "input_count": "How many {unit}? ",
        "daily_target_prompt": "Enter daily CO₂ target (kg): ",
        "target_set": "✅ Target set.",
        "over_target": "⚠️ Over daily target ({target} kg)!",
        "result": "Result",
        "weight": "Weight",
        "emitted": "Emitted",
        "decompose_time": "Decompose Time",
        "eco_tip": "Eco Tip",
        "today_co2_emissions": "Today's CO₂ Emissions:",
        "score": "Score:",
        "tree_status_messages": {
            "healthy": "Healthy! 🌳 Keep up the good work!",
            "slightly_wilting": "Slightly wilting. 🌲 Please reduce your carbon emissions!",
            "wilting": "Very wilting. 🍂 Pay more attention to environmental protection!",
            "dead": "The tree is dead... 💀 This is serious. Please work for the environment!"},
        "compare_title": "📊 My CO₂ Emissions vs Average",
        "today_emission_msg": "✅ My CO₂ emissions today: **{value:.2f} kg**",
        "korea_avg_msg": "🇰🇷 Korea's daily average per person: **{value:.1f} kg**",
        "oecd_avg_msg": "🌍 OECD average per person: **{value:.1f} kg**",
        "less_than_korea": "🎉 You emitted less than the Korea average! Keep it up!",
        "more_than_korea": "⚠️ You emitted more than the Korea average. Let's try to reduce it!",
        "less_than_oecd": "🌱 Lower than the OECD average!",
        "more_than_oecd": "🌏 Higher than the OECD average. Let's do better next time!"
        },
    "zh": {
        "welcome": "🌿 开始为环境做一点小改变吧！",
        "select_menu": "\n1. 输入垃圾\n2. 查看今日排放量和分数\n3. 设置每日目标\n4. 环保测验\n5. 退出\n请选择: ",
        "goodbye": "👋 感谢您的使用！",
        "invalid_number": "❌ 请输入数字。",
        "invalid_menu": "❌ 菜单编号无效。",
        "input_count": "多少{unit}？",
        "daily_target_prompt": "请输入每日CO₂排放目标(公斤): ",
        "target_set": "✅ 目标已设置。",
        "over_target": "⚠️ 超过每日目标({target}公斤)！",
        "result": "结果",
        "weight": "重量",
        "emitted": "排放量",
        "decompose_time": "分解时间",
        "eco_tip": "环保建议",
        "today_co2_emissions": "今日累计CO₂排放量:",
        "score": "分数:",
        "tree_status_messages": {
            "healthy": "健康！🌳 请保持下去！",
            "slightly_wilting": "有点枯萎了。🌲 请减少碳排放！",
            "wilting": "枯萎得很厉害。🍂 请更注重环境保护！",
            "dead": "树死了... 💀 情况很严重。请为环境努力！"},
        "compare_title": "📊 我的CO₂排放量与平均值比较",
        "today_emission_msg": "✅ 我今天的CO₂排放量: **{value:.2f} kg**",
        "korea_avg_msg": "🇰🇷 韩国人均每日平均排放量: **{value:.1f} kg**",
        "oecd_avg_msg": "🌍 OECD人均每日平均排放量: **{value:.1f} kg**",
        "less_than_korea": "🎉 少于韩国平均值！继续保持！",
        "more_than_korea": "⚠️ 高于韩国平均值，再努力减少一点吧！",
        "less_than_oecd": "🌱 低于OECD平均值！",
        "more_than_oecd": "🌏 高于OECD平均值，下次努力减少！"
        }
    }

eco_quotes = [
    "The Earth is what we all have in common. - Wendell Berry",
    "작은 변화가 큰 변화를 만듭니다.",
    "지구는 우리가 물려받은 것이 아니라, 빌려온 것입니다.",
    "There is no Planet B.",
    "One planet, one chance."
]

# 나무 상태에 따른 이모지 및 CO2 임계값
TREE_STATUS_EMOJIS = {
    "healthy": "🌳",            # CO2 0-5kg (건강한 나무)
    "slightly_wilting": "🌲", # CO2 5-10kg (약간 시든 나무 또는 다른 종류의 나무)
    "wilting": "🍂",            # CO2 10-20kg (잎이 지는 나무)
    "dead": "💀"                # CO2 20kg 이상 (죽은 나무 또는 해골)
}

CO2_THRESHOLDS = {
    "healthy": 5.0,
    "slightly_wilting": 10.0,
    "wilting": 20.0
}


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
    # 세션 상태에 퀴즈 인덱스가 없으면 초기화하거나 새로운 퀴즈 선택
    if 'current_quiz_index' not in st.session_state:
        st.session_state['current_quiz_index'] = random.randint(0, len(quiz_data) - 1)
    
    quiz = quiz_data[st.session_state['current_quiz_index']]
    q_text = quiz["question"][lang]
    correct_answer = quiz["answer"]
    if isinstance(correct_answer, dict):
        correct_answer = correct_answer[lang]

    st.write("---")
    st.subheader(f"🌱 {q_text}")
    
    # Use a unique key for the text input to prevent issues on re-runs
    # and wrap in a form to handle submission cleanly
    with st.form(key=f"quiz_form_{st.session_state['current_quiz_index']}"):
        user_answer = st.text_input(
            {"ko": "정답을 입력하세요: ", "en": "Enter your answer: ", "zh": "请输入答案: "}[lang],
            key=f"quiz_input_{st.session_state['current_quiz_index']}"
        )
        submit_button = st.form_submit_button(
            {"ko": "정답 확인", "en": "Check Answer", "zh": "检查答案"}[lang]
        )

        if submit_button:
            if user_answer.strip().lower() == str(correct_answer).lower():
                st.success({"ko": "✅ 정답입니다! 잘 하셨어요!", "en": "✅ Correct! Well done!", "zh": "✅ 正确！做得好！"}[lang])
            else:
                st.error({"ko": f"❌ 아쉽지만 오답입니다. 정답: {correct_answer}", "en": f"❌ Incorrect. The correct answer: {correct_answer}", "zh": f"❌ 答错了。正确答案是: {correct_answer}"}[lang])
    
    # "다른 문제 풀기" 버튼 추가
    if st.button({"ko": "다른 문제 풀기", "en": "Solve another quiz", "zh": "解决另一个测验"}[lang], key=f"next_quiz_{st.session_state['current_quiz_index']}"):
        st.session_state['current_quiz_index'] = random.randint(0, len(quiz_data) - 1)
        st.rerun() # 앱을 다시 실행하여 새로운 퀴즈 표시

    st.write("---")

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

def app():
    # 세션 상태 변수 초기화
    if 'current_language' not in st.session_state:
        st.session_state['current_language'] = "ko"
    if 'history' not in st.session_state:
        st.session_state['history'] = load_history()
    if 'settings' not in st.session_state:
        st.session_state['settings'] = load_settings()

    # 사이드바에서 언어 선택
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

    # --- ✨ 이모지 트리 표시 로직 (크기 조절 및 메시지) ✨ ---
    current_co2, _ = get_today_co2_and_score(st.session_state['history'])
    tree_status = get_tree_status(current_co2)
    tree_emoji = TREE_STATUS_EMOJIS[tree_status]
    tree_message = messages[lang]["tree_status_messages"][tree_status] # 상태 메시지 가져오기

    # HTML <font-size>를 사용하여 이모지 크기 조절
    st.markdown(
        f"<p style='text-align: center; font-size: 5em;'>{tree_emoji}</p>", # 이모지 크기를 5em으로 설정하고 중앙 정렬
        unsafe_allow_html=True
    )
    st.write(f"<p style='text-align: center;'>현재 CO₂ 배출량: <b>{current_co2:.2f} kg</b></p>", unsafe_allow_html=True)
    
    # 상태에 따라 다른 스타일의 메시지 박스 사용
    if tree_status == "healthy":
        message_style = "background-color: #e6ffe6; color: #1f7a1f; padding: 10px; border-radius: 5px;" # Light green for success
    elif tree_status == "slightly_wilting":
        message_style = "background-color: #e6f7ff; color: #1f6b8f; padding: 10px; border-radius: 5px;" # Light blue for info
    elif tree_status == "wilting":
        message_style = "background-color: #fff8e6; color: #a37200; padding: 10px; border-radius: 5px;" # Light yellow for warning
    else: # dead
        message_style = "background-color: #ffe6e6; color: #a30000; padding: 10px; border-radius: 5px;" # Light red for error

    st.markdown(
        f"<p style='text-align: center; {message_style}'><b>{tree_message}</b></p>",
        unsafe_allow_html=True
    )
    # --- ✨ 이모지 트리 표시 로직 끝 ✨ ---


    # 사이드바 라디오 버튼을 사용하여 메인 메뉴
    st.sidebar.title("메뉴")
    menu_options = {
    "ko": ["쓰레기 입력", "오늘 배출량 및 점수 확인", "하루 목표 설정", "환경 퀴즈", "AI챗봇", "평균 배출량과 비교"],
    "en": ["Enter waste", "View today's emissions and score", "Set daily target", "Eco Quiz", "AI Chatbot", "Compare with average"],
    "zh": ["输入垃圾", "查看今日排放量和分数", "设置每日目标", "环保测验", "AI环保咨询", "与平均值比较"]
    }

    choice = st.sidebar.radio("옵션을 선택하세요:", menu_options[lang])

    if choice == menu_options[lang][0]:  # 쓰레기 입력
        st.header(menu_options[lang][0])

        waste_names = [data['names'][lang] for data in waste_data.values()]
        selected_waste_name = st.selectbox(
            {"ko": "쓰레기 종류를 선택하세요:", "en": "Select waste type:", "zh": "请选择垃圾类型:"}[lang],
            waste_names
        )

        waste_key = None
        for k, v in waste_data.items():
            if selected_waste_name == v["names"][lang]:
                waste_key = k
                break

        if waste_key:
            unit_text = waste_data[waste_key]["unit"][lang]
            try:
                count = st.number_input(
                    messages[lang]["input_count"].format(unit=unit_text),
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    format="%f"
                )
            except ValueError:
                st.error(messages[lang]["invalid_number"])
                count = 0.0

            if st.button({"ko": "입력", "en": "Submit", "zh": "提交"}[lang]):
                if count >= 0:
                    result = calculate_impact(waste_key, count, lang)
                    st.session_state['history'].append(result)
                    save_history(st.session_state['history']) # 파일 시스템에 저장

                    st.subheader(f"📊 {messages[lang].get('result', '결과')}")
                    st.write(f"- **{waste_data[result['waste_key']]['names'][lang]}**: {result['count']} {result['unit']}")
                    st.write(f"- **{messages[lang].get('weight', '무게')}:** {result['weight_kg']:.3f} kg")
                    st.write(f"- **CO₂ {messages[lang].get('emitted', '배출량')}:** {result['co2_emitted']:.2f} kg")
                    st.write(f"- **{messages[lang].get('decompose_time', '분해 시간')}:** {result['decompose_time']}")
                    st.success(f"🌱 **{messages[lang].get('eco_tip', '친환경 대안')}:** {result['eco_tip']}")

                    today_co2, eco_score = get_today_co2_and_score(st.session_state['history'])
                    st.info(f"📝 {messages[lang]['today_co2_emissions']} {today_co2:.2f} kg")
                    st.success(f"🏆 {messages[lang]['score']} {eco_score:.1f} / 100")

                    if st.session_state['settings'].get("daily_target") and today_co2 > st.session_state['settings']["daily_target"]:
                        st.warning(messages[lang]["over_target"].format(target=st.session_state['settings']["daily_target"]))
                else:
                    st.error(messages[lang]["invalid_number"].replace("숫자를", "0 이상의 숫자를").replace("Please enter a number.", "Enter a number >= 0."))


    elif choice == menu_options[lang][1]:  # 오늘 배출량 및 점수 확인
        st.header(menu_options[lang][1])
        today_co2, eco_score = get_today_co2_and_score(st.session_state['history'])
        st.info(f"📝 {messages[lang]['today_co2_emissions']} {today_co2:.2f} kg")
        st.success(f"🏆 {messages[lang]['score']} {eco_score:.1f} / 100")

    elif choice == menu_options[lang][2]:  # 하루 목표 설정
        st.header(menu_options[lang][2])
        try:
            target = st.number_input(
                messages[lang]["daily_target_prompt"],
                min_value=0.0,
                value=st.session_state['settings'].get("daily_target", 0.0) or 0.0,
                step=0.1,
                format="%f"
            )
            if st.button(messages[lang]["target_set"].replace("✅ 목표가 설정되었습니다.", "설정").replace("✅ Target set.", "Set").replace("✅ 目标已设置。", "设置")):
                st.session_state['settings']["daily_target"] = target
                save_settings(st.session_state['settings'])
                st.success(messages[lang]["target_set"])
        except ValueError:
            st.error(messages[lang]["invalid_number"])

    elif choice == menu_options[lang][3]:  # 환경 퀴즈
        st.header(menu_options[lang][3])
        display_eco_quiz(lang)

    elif choice == menu_options[lang][4]:
        display_ai_chat(lang)

  elif choice == menu_options[lang][5]:  # 평균 배출량과 비교
    st.header(messages[lang]["compare_title"])
    today_co2, _ = get_today_co2_and_score(st.session_state['history'])

    st.write(messages[lang]["today_emission_msg"].format(value=today_co2))
    st.write(messages[lang]["korea_avg_msg"].format(value=KOREA_AVG_DAILY_CO2))
    st.write(messages[lang]["oecd_avg_msg"].format(value=OECD_AVG_DAILY_CO2))

    st.bar_chart({
        "오늘 나" if lang == "ko" else "Me" if lang == "en" else "我": [today_co2],
        "대한민국 평균" if lang == "ko" else "Korea avg" if lang == "en" else "韩国平均": [KOREA_AVG_DAILY_CO2],
        "OECD 평균" if lang == "ko" else "OECD avg" if lang == "en" else "OECD平均": [OECD_AVG_DAILY_CO2]
    })

    if today_co2 < KOREA_AVG_DAILY_CO2:
        st.success(messages[lang]["less_than_korea"])
    else:
        st.warning(messages[lang]["more_than_korea"])

    if today_co2 < OECD_AVG_DAILY_CO2:
        st.info(messages[lang]["less_than_oecd"])
    else:
        st.info(messages[lang]["more_than_oecd"])

if __name__ == "__main__":
    app()
