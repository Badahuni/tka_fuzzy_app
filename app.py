import os
from datetime import datetime
from google_sheet import save_to_sheet
from dataclasses import asdict

import pandas as pd
import streamlit as st

from fuzzy_rehab_manual import (PatientInput,
                                recommend_exercise,
                                EXERCISE_LIBRARY)


st.set_page_config(
    page_title=" 무릎인공관절 환자 AI 재활 앱",
    page_icon="🦵",
    layout="centered"
)
st.markdown("""
<style>

/* 전체 글자 */
html, body, [class*="css"] {
    font-size: 25px;
}

/* 입력 항목 글자 */
label {
    font-size: 24px !important;
    font-weight: bold;
}

/* 버튼 */
div.stButton > button {
    height: 70px;
    font-size: 28px;
    font-weight: bold;
}

/* 체크박스 */
.stCheckbox label {
    font-size: 25gipx !important;
}

</style>
""", unsafe_allow_html=True)


DATA_FILE = "patient_data.csv"


# =========================
# 1. 데이터 입출력
# =========================
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
        "swelling",
        "adherence",
        "fuzzy_score",
        "level",
        "label",
        "sets",
        "reps",
        "target_flexion",
        "rest_seconds",
        "exercise_list",
        "caution"
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


# =========================
# 2. 운동 설명 사전
# =========================


# =========================
# 3. 결과를 앱용 운동 리스트로 변환
# =========================
def build_exercise_prescription(result):
    """
    fuzzy_rehab_manual.py의 result.exercise_list(문자열 리스트)를
    앱에서 사용하기 쉬운 dict 리스트로 변환
    """
    prescription = []

    for ex_name in result.exercise_list:
        info = EXERCISE_LIBRARY.get(ex_name, {})
        prescription.append({
            "name": info.get("korean_name", ex_name),
            "original_name": ex_name,
            "sets": int(result.sets),
            "reps": int(result.reps),
            "note": info.get("note", "설명 없음"),
            "video_path": info.get("video_path")
        })

    return prescription


# =========================
# 4. 순응도 계산
# =========================
def calculate_adherence(prescription, performed_sets):
    """
    prescription: [{"name": ..., "sets": ...}, ...]
    performed_sets: {"운동명": 실제 수행 세트}
    """
    prescribed_total = sum(ex["sets"] for ex in prescription)

    performed_total = 0
    for ex in prescription:
        ex_name = ex["name"]
        prescribed_sets = ex["sets"]
        actual_sets = min(performed_sets.get(ex_name, 0), prescribed_sets)
        performed_total += actual_sets

    if prescribed_total == 0:
        return 0.0

    return round((performed_total / prescribed_total) * 100, 2)


# =========================
# 5. 세션 상태 초기화
# =========================
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "recommended_exercises" not in st.session_state:
    st.session_state.recommended_exercises = []

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = {}

if "performed_sets" not in st.session_state:
    st.session_state.performed_sets = {}


# =========================
# 6. UI
# =========================
st.title("무릎인공관절 환자 재활 앱 🦵")
st.caption("매일 상태를 입력하고 오늘의 맞춤 운동을 확인하세요.")

menu = st.sidebar.radio(
    "메뉴",
    ["오늘 입력", "내 기록 보기"]
)


# =========================
# 7. 오늘 입력
# =========================
if menu == "오늘 입력":
    st.subheader("오늘 상태 입력")

    name = st.text_input("이름", placeholder="예: 홍길동")
    postop_day = st.number_input("수술 후 일수 (POD)", min_value=0, max_value=365, value=7)

    pain = st.slider("오늘 통증", 0, 10, 3)
    fatigue = st.slider("오늘 피로도", 0, 10, 2)
    rom = st.slider("오늘 ROM (°)", 0, 135, 90, step=5)

    swelling_text = st.radio("붓기 있나요?", ["아니오", "예"], horizontal=True)
    exercise_pain_text = st.radio("운동 중 통증이 심했나요?", ["아니오", "예"], horizontal=True)

    if st.button("오늘 운동 추천 받기", use_container_width=True):
        if not name.strip():
            st.warning("이름을 입력해주세요.")
        else:
            df = load_data()
            previous_record = get_previous_record(df, name)

            prev_adherence = previous_record["adherence"] if previous_record else 70.0
            prev_pain = previous_record["pain"] if previous_record else pain
            prev_rom = previous_record["rom"] if previous_record else rom

            pain_change = pain - prev_pain
            rom_change = rom - prev_rom

            # 붓기 입력을 0 또는 2.5 정도로 반영
            swelling_value = 2.5 if swelling_text == "예" else 0.0

            # 운동 중 통증 심했으면 pain_change를 조금 더 보수적으로 반영
            if exercise_pain_text == "예":
                pain_change = max(pain_change, 2)

            patient = PatientInput(
                pain=float(pain),
                fatigue=float(fatigue),
                rom=float(rom),
                postop_day=int(postop_day),
                adherence=float(prev_adherence),
                swelling=float(swelling_value),
                pain_change=float(pain_change),
                rom_change=float(rom_change)
            )

            result = recommend_exercise(patient)
            exercise_list = build_exercise_prescription(result)

            st.session_state.analysis_done = True
            st.session_state.recommended_exercises = exercise_list
            st.session_state.analysis_result = {
                "name": name,
                "postop_day": postop_day,
                "pain": pain,
                "fatigue": fatigue,
                "rom": rom,
                "swelling": swelling_value,
                "fuzzy_score": result.fuzzy_score,
                "level": result.level,
                "label": result.label,
                "sets": result.sets,
                "reps": result.reps,
                "target_flexion": result.target_flexion,
                "rest_seconds": result.rest_seconds,
                "caution": result.caution,
                "adjusted_by_safety_filter": result.adjusted_by_safety_filter
            }
            st.session_state.performed_sets = {ex["name"]: 0 for ex in exercise_list}

    if st.session_state.analysis_done:
        result = st.session_state.analysis_result
        exercise_list = st.session_state.recommended_exercises

        st.subheader("AI 추천 결과")
        st.write(f"**퍼지 점수:** {result['fuzzy_score']}")
        st.write(f"**운동 레벨:** Level {result['level']}")
        st.write(f"**해석:** {result['label']}")
        st.write(f"**권장 세트 수:** {result['sets']}세트")
        st.write(f"**권장 반복 수:** {result['reps']}회")
        st.write(f"**목표 굴곡 각도:** {result['target_flexion']}°")
        st.write(f"**휴식 시간:** {result['rest_seconds']}초")
        st.write(f"**주의사항:** {result['caution']}")

        st.subheader("추천 운동")

        exercise_names = [ex["name"] for ex in exercise_list]
        selected_name = st.selectbox("운동 선택", exercise_names)

        selected_ex = None
        for ex in exercise_list:
            if ex["name"] == selected_name:
                selected_ex = ex
                break

        if selected_ex:
            st.write(f"### {selected_ex['name']}")
            st.write(f"- {selected_ex['reps']}회 × {selected_ex['sets']}세트")
            st.write(f"- 설명: {selected_ex.get('note', '설명 없음')}")

            video_path = selected_ex.get("video_path")

            if video_path and os.path.exists(video_path):
                st.video(video_path)
            else:
                st.info("등록된 영상이 없습니다.")



        if exercise_list:
            st.subheader("추천 운동 목록")

            performed_sets = {}

            for i, ex in enumerate(exercise_list):
                ex_name = ex.get("name", f"운동 {i + 1}")
                ex_sets = int(ex.get("sets", 0))
                ex_reps = ex.get("reps", "정보 없음")
                ex_note = ex.get("note", "설명 없음")

                st.markdown(f"### {i + 1}. {ex_name}")
                st.write(f"- 세트: {ex_sets}")
                st.write(f"- 횟수: {ex_reps}")
                st.write(f"- 설명: {ex_note}")

                performed_sets[ex_name] = st.number_input(
                    f"{ex_name} 수행 세트",
                    min_value=0,
                    max_value=ex_sets,
                    value=0,
                    step=1,
                    key=f"performed_set_{i}_{ex_name}_{result.get('name', 'user')}_{result.get('postop_day', 0)}"
                )

                st.divider()

            if st.button("저장하기", use_container_width=True, key="save_button_main"):
                adherence = calculate_adherence(exercise_list, performed_sets)

                row = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "name": result.get("name", ""),
                    "postop_day": result.get("postop_day", ""),
                    "pain": result.get("pain", ""),
                    "fatigue": result.get("fatigue", ""),
                    "rom": result.get("rom", ""),
                    "swelling": result.get("swelling", ""),
                    "adherence": adherence,
                    "fuzzy_score": result.get("fuzzy_score", ""),
                    "level": result.get("level", ""),
                    "label": result.get("label", ""),
                    "sets": result.get("sets", ""),
                    "reps": result.get("reps", ""),
                    "target_flexion": result.get("target_flexion", ""),
                    "rest_seconds": result.get("rest_seconds", ""),
                    "exercise_list": str([ex["name"] for ex in exercise_list]),
                    "caution": result.get("caution", "")
                }

                save_data(row)  # CSV 저장
                save_to_sheet(row)  # Google Sheets 저장

                st.success("Google Sheets 저장 완료")

                st.success(f"저장 완료! 순응도: {adherence}%")
                st.metric("오늘 순응도", f"{adherence}%")
                st.progress(min(adherence / 100, 1.0))

                st.session_state.performed_sets = {}
                st.session_state.recommended_exercises = []
                st.session_state.analysis_result = {}
                st.session_state.analysis_done = False


# =========================
# 8. 내 기록 보기
# =========================
elif menu == "내 기록 보기":
    df = load_data()

    name = st.text_input("이름 입력")

    if name:
        patient_df = df[df["name"].astype(str) == str(name)].copy()

        if patient_df.empty:
            st.warning("기록이 없습니다.")
        else:
            st.dataframe(patient_df, use_container_width=True)

            if "pain" in patient_df.columns:
                st.subheader("통증 변화")
                st.line_chart(patient_df["pain"])

            if "rom" in patient_df.columns:
                st.subheader("ROM 변화")
                st.line_chart(patient_df["rom"])

            if "adherence" in patient_df.columns:
                st.subheader("순응도 변화")
                st.line_chart(patient_df["adherence"])


st.divider()

if st.checkbox("관리자 모드"):

        df = load_data()

        st.subheader("저장된 환자 데이터")

        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="CSV 다운로드",
            data=csv,
            file_name="patient_data.csv",
            mime="text/csv"
        )