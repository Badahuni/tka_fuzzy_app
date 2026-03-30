import os
from datetime import datetime

import pandas as pd
import streamlit as st

from fuzzy_logic import calculate_fuzzy_score
from adaptive_logic import (
    adaptive_adjustment,
    classify_intensity,
    prescribe_exercises,
)

st.set_page_config(
    page_title="TKA 환자 재활 앱",
    page_icon="🦵",
    layout="centered"
)

DATA_FILE = "patient_data.csv"


def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=[
        "date",
        "name",
        "postop_day",
        "pain",
        "fatigue",
        "rom",
        "adherence",
        "fuzzy_score",
        "final_score",
        "intensity",
        "exercise_list"
    ])


def save_data(row):
    df = load_data()
    new_df = pd.DataFrame([row])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")


def get_previous_record(df, patient_name):
    patient_df = df[df["name"].astype(str) == str(patient_name)].copy()

    if patient_df.empty:
        return None

    patient_df["date"] = pd.to_datetime(patient_df["date"], errors="coerce")
    patient_df = patient_df.sort_values("date")

    last_row = patient_df.iloc[-1]

    return {
        "pain": float(last_row["pain"]),
        "fatigue": float(last_row["fatigue"]),
        "rom": float(last_row["rom"]),
        "adherence": float(last_row["adherence"]),
        "postop_day": int(last_row["postop_day"])
    }


def calculate_adherence(prescription, performed_sets):
    prescribed_total = sum(ex["sets"] for ex in prescription)

    performed_total = 0
    for ex in prescription:
        actual_sets = min(performed_sets.get(ex["name"], 0), ex["sets"])
        performed_total += actual_sets

    if prescribed_total == 0:
        return 0.0

    return round((performed_total / prescribed_total) * 100, 2)


# 세션 상태 초기화
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "recommended_exercises" not in st.session_state:
    st.session_state.recommended_exercises = []

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = {}

if "performed_sets" not in st.session_state:
    st.session_state.performed_sets = {}


st.title("🦵 TKA 환자 재활 앱")
st.caption("매일 상태를 입력하고 오늘의 운동을 확인하세요.")

menu = st.sidebar.radio(
    "메뉴",
    ["오늘 입력", "내 기록 보기"]
)

# =========================
# 1. 오늘 입력
# =========================
if menu == "오늘 입력":
    st.subheader("오늘 상태 입력")

    name = st.text_input("이름", placeholder="예: 홍길동")
    postop_day = st.number_input("수술 후 일수 (POD)", min_value=0, max_value=365, value=7)

    pain = st.slider("오늘 통증", 0, 10, 3)
    fatigue = st.slider("오늘 피로도", 0, 10, 2)
    rom = st.slider("오늘 ROM (°)", 0, 150, 90, step=5)

    swelling = st.radio("붓기 있나요?", ["아니오", "예"], horizontal=True)
    exercise_pain = st.radio("운동 중 통증 심했나요?", ["아니오", "예"], horizontal=True)

    if st.button("오늘 운동 추천 받기", use_container_width=True):
        if not name.strip():
            st.warning("이름을 입력해주세요.")
        else:
            df = load_data()
            previous_record = get_previous_record(df, name)

            temp_adherence = previous_record["adherence"] if previous_record else 70

            fuzzy_score = calculate_fuzzy_score(
                pain, fatigue, rom, postop_day, temp_adherence
            )

            current_data = {
                "pain": pain,
                "fatigue": fatigue,
                "rom": rom,
                "adherence": temp_adherence,
                "postop_day": postop_day
            }

            final_score, reasons = adaptive_adjustment(
                fuzzy_score, current_data, previous_record
            )

            if swelling == "예":
                final_score -= 5
                reasons.append("붓기로 인해 -5 조정")

            if exercise_pain == "예":
                final_score -= 5
                reasons.append("운동 통증으로 -5 조정")

            intensity = classify_intensity(final_score)
            exercise_list = prescribe_exercises(intensity)

            st.session_state.analysis_done = True
            st.session_state.recommended_exercises = exercise_list
            st.session_state.analysis_result = {
                "name": name,
                "postop_day": postop_day,
                "pain": pain,
                "fatigue": fatigue,
                "rom": rom,
                "fuzzy_score": fuzzy_score,
                "final_score": final_score,
                "intensity": intensity,
                "reasons": reasons
            }
            st.session_state.performed_sets = {ex["name"]: 0 for ex in exercise_list}

    if st.session_state.analysis_done:
        result = st.session_state.analysis_result
        exercise_list = st.session_state.recommended_exercises

        st.subheader("오늘의 운동")

        for ex in exercise_list:
            st.write(f"**{ex['name']}**")
            st.write(f"{ex['reps']}회 × {ex['sets']}세트")

            if ex.get("video_link"):
                st.markdown(f"[영상 보기]({ex['video_link']})")

        st.subheader("운동 수행 체크")

        performed_sets = {}
        for ex in exercise_list:
            performed_sets[ex["name"]] = st.number_input(
                f"{ex['name']} 수행 세트",
                0, ex["sets"], 0,
                key=ex["name"]
            )

        if st.button("저장하기", use_container_width=True):
            adherence = calculate_adherence(exercise_list, performed_sets)

            save_data({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "name": result["name"],
                "postop_day": result["postop_day"],
                "pain": result["pain"],
                "fatigue": result["fatigue"],
                "rom": result["rom"],
                "adherence": adherence,
                "fuzzy_score": result["fuzzy_score"],
                "final_score": result["final_score"],
                "intensity": result["intensity"],
                "exercise_list": str(exercise_list)
            })

            st.success(f"저장 완료! 순응도: {adherence}%")

# =========================
# 2. 기록 보기
# =========================
elif menu == "내 기록 보기":
    df = load_data()

    name = st.text_input("이름 입력")

    if name:
        patient_df = df[df["name"] == name]

        if patient_df.empty:
            st.warning("기록 없음")
        else:
            st.dataframe(patient_df)

            st.line_chart(patient_df["pain"])
            st.line_chart(patient_df["rom"])
            st.line_chart(patient_df["adherence"])