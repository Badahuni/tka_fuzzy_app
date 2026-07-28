import os
from datetime import datetime
from google_sheet import save_to_sheet

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
    font-size: 28px;
}

/* 입력 항목 글자 */
label {
    font-size: 26px !important;
    font-weight: bold;
}

/* 버튼 */
div.stButton > button {
    height: 70px;
    font-size: 30px;
    font-weight: bold;
}

/* 체크박스 */
.stCheckbox label {
    font-size: 25gip !important;
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
# 오늘 상태 입력
# =========================
st.header("오늘 상태 입력")

name = st.text_input(
    "이름",
    placeholder="예: 홍길동",
    key="patient_name"
)

postop_day = st.number_input(
    "수술 후 경과일수 (POD)",
    min_value=1,
    max_value=21,
    value=7,
    step=1,
    key="postop_day"
)

st.divider()


# =========================
# 통증 입력: 이모지 선택
# =========================
st.subheader("오늘 통증 정도")

st.caption("0은 통증 없음, 10은 가장 심한 통증입니다.")

pain_options = [
    "😊 0",
    "😊 1",
    "🙂 2",
    "🙂 3",
    "😐 4",
    "😐 5",
    "😣 6",
    "😣 7",
    "😫 8",
    "😫 9",
    "😭 10"
]

selected_pain = st.radio(
    "통증 점수를 선택하세요",
    options=pain_options,
    index=3,
    horizontal=True,
    key="pain_radio",
    label_visibility="collapsed"
)

# "🙂 3"에서 숫자 3만 분리
pain = int(selected_pain.split()[-1])

st.info(f"선택한 통증 점수: {pain}점")


# =========================
# 피로도 입력: - / + 방식
# =========================
st.subheader("오늘 컨디션")

st.caption("0은 피로 없음, 10은 매우 심한 피로입니다.")

fatigue = st.number_input(
    "피로도 점수",
    min_value=0,
    max_value=10,
    value=3,
    step=1,
    key="fatigue_input"
)


# =========================
# ROM 입력: 5도 단위
# =========================
st.subheader("오늘 치료실에서 수행한 무릎 굴곡 각도")

st.caption("무릎이 구부러지는 각도를 5도 단위로 입력하세요.")

rom = st.number_input(
    " 버튼을 눌러주세요 (°)",
    min_value=0,
    max_value=135,
    value=100,
    step=5,
    key="rom_input"
)


# =========================
# 붓기 및 운동 중 통증
# =========================
st.subheader("추가 상태 확인")

swelling_text = st.radio(
    "오늘 무릎에 붓기가 있나요?",
    options=["아니오", "예"],
    horizontal=True,
    key="swelling_radio"
)

exercise_pain_text = st.radio(
    "운동 중 통증이 평소보다 심했나요?",
    options=["아니오", "예"],
    horizontal=True,
    key="exercise_pain_radio"
)

# =========================
# 오늘 운동 추천 버튼
# =========================
if st.button(
    "오늘 운동 추천 받기",
    use_container_width=True,
    key="recommend_button"
):
    if not name.strip():
        st.warning("이름을 입력해주세요.")

    else:
        df = load_data()
        previous_record = get_previous_record(df, name)

        prev_adherence = (
            previous_record["adherence"]
            if previous_record
            else 70.0
        )

        prev_pain = (
            previous_record["pain"]
            if previous_record
            else pain
        )

        prev_rom = (
            previous_record["rom"]
            if previous_record
            else rom
        )

        pain_change = pain - prev_pain
        rom_change = rom - prev_rom

        # 붓기: 아니오 0점, 예 2.5점
        swelling_value = (
            2.5 if swelling_text == "예" else 0.0
        )

        # 운동 중 통증이 심한 경우 보수적으로 적용
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

        prescription = recommend_exercise(patient)

        new_exercise_list = build_exercise_prescription(
            prescription
        )

        # 추천 결과를 세션에 보관
        st.session_state.analysis_done = True
        st.session_state.recommended_exercises = (
            new_exercise_list
        )

        st.session_state.analysis_result = {
            "name": name,
            "postop_day": int(postop_day),
            "pain": float(pain),
            "fatigue": float(fatigue),
            "rom": float(rom),
            "swelling": float(swelling_value),
            "fuzzy_score": prescription.fuzzy_score,
            "level": prescription.level,
            "label": prescription.label,
            "sets": prescription.sets,
            "reps": prescription.reps,
            "target_flexion": prescription.target_flexion,
            "rest_seconds": prescription.rest_seconds,
            "caution": prescription.caution,
            "adjusted_by_safety_filter":
                prescription.adjusted_by_safety_filter
        }

        # 새로운 추천을 받으면 수행 세트 초기화
        st.session_state.performed_sets = {
            ex["name"]: 0
            for ex in new_exercise_list
        }

        st.session_state.save_done = False

        # 이전 운동 입력 위젯 값 제거
        old_widget_keys = [
            key for key in st.session_state.keys()
            if str(key).startswith("performed_set_")
        ]

        for key in old_widget_keys:
            del st.session_state[key]


# ==================================================
# 여기부터는 추천 버튼 밖입니다.
# 앞에 들여쓰기를 추가하지 마세요.
# ==================================================
if (
    st.session_state.analysis_done
    and st.session_state.recommended_exercises
):
    exercise_list = (
        st.session_state.recommended_exercises
    )

    result = st.session_state.analysis_result

    st.subheader("추천 운동 목록")

    performed_sets = {}

    for i, ex in enumerate(exercise_list):
        ex_name = ex.get(
            "name",
            f"운동 {i + 1}"
        )

        ex_sets = int(
            ex.get("sets", 0)
        )

        ex_reps = ex.get(
            "reps",
            "정보 없음"
        )

        ex_note = ex.get(
            "note",
            "설명 없음"
        )

        st.markdown(
            f"### {i + 1}. {ex_name}"
        )

        st.write(f"- 세트: {ex_sets}")
        st.write(f"- 횟수: {ex_reps}")
        st.write(f"- 설명: {ex_note}")

        # 로컬 영상 또는 영상 URL
        video_path = ex.get("video_path")
        video_link = ex.get("video_link")

        if video_path:
            if os.path.exists(video_path):
                st.video(video_path)
            else:
                st.info("등록된 영상 파일을 찾을 수 없습니다.")

        elif video_link:
            st.video(video_link)

        else:
            st.info("등록된 영상이 없습니다.")

        widget_key = (
            f"performed_set_{i}_"
            f"{ex_name}_"
            f"{result.get('postop_day', 0)}"
        )

        performed_sets[ex_name] = st.number_input(
            f"{ex_name} 수행 세트",
            min_value=0,
            max_value=ex_sets,
            value=int(
                st.session_state.performed_sets.get(
                    ex_name,
                    0
                )
            ),
            step=1,
            key=widget_key,
            disabled=st.session_state.save_done
        )

        # 환자가 입력한 값을 유지
        st.session_state.performed_sets[ex_name] = (
            performed_sets[ex_name]
        )

        st.divider()

    # =========================
    # 저장하기
    # =========================
    if not st.session_state.save_done:
        if st.button(
            "저장하기",
            use_container_width=True,
            key="save_button_main"
        ):
            adherence = calculate_adherence(
                exercise_list,
                performed_sets
            )

            row = {
                "date": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "name": result.get("name", ""),
                "postop_day": result.get(
                    "postop_day",
                    ""
                ),
                "pain": result.get("pain", ""),
                "fatigue": result.get(
                    "fatigue",
                    ""
                ),
                "rom": result.get("rom", ""),
                "swelling": result.get(
                    "swelling",
                    ""
                ),
                "adherence": adherence,
                "fuzzy_score": result.get(
                    "fuzzy_score",
                    ""
                ),
                "level": result.get("level", ""),
                "label": result.get("label", ""),
                "sets": result.get("sets", ""),
                "reps": result.get("reps", ""),
                "target_flexion": result.get(
                    "target_flexion",
                    ""
                ),
                "rest_seconds": result.get(
                    "rest_seconds",
                    ""
                ),
                "exercise_list": str([
                    ex["name"]
                    for ex in exercise_list
                ]),
                "caution": result.get(
                    "caution",
                    ""
                )
            }

            # CSV에는 먼저 저장
            save_data(row)

            # Google Sheets 연결 실패 시에도
            # CSV 저장은 유지되도록 처리
            try:
                save_to_sheet(row)
                st.success(
                    "CSV와 Google Sheets에 저장되었습니다."
                )
            except Exception as error:
                st.warning(
                    "CSV에는 저장되었지만 "
                    "Google Sheets 저장에 실패했습니다."
                )
                st.caption(
                    f"오류 내용: {error}"
                )

            st.session_state.save_done = True

            st.success(
                f"저장 완료! 순응도: {adherence}%"
            )

            st.metric(
                "오늘 순응도",
                f"{adherence}%"
            )

            st.progress(
                min(adherence / 100, 1.0)
            )

            st.rerun()

    else:
        adherence = calculate_adherence(
            exercise_list,
            st.session_state.performed_sets
        )

        st.success("오늘 기록이 저장되었습니다.")

        st.metric(
            "오늘 순응도",
            f"{adherence}%"
        )

        st.progress(
            min(adherence / 100, 1.0)
        )

        if st.button(
            "새로운 평가 시작",
            use_container_width=True,
            key="new_assessment_button"
        ):
            st.session_state.analysis_done = False
            st.session_state.recommended_exercises = []
            st.session_state.analysis_result = {}
            st.session_state.performed_sets = {}
            st.session_state.save_done = False

            st.rerun()


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

if st.checkbox("관리자 모드", key="admin_mode"):

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