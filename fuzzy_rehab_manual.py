from dataclasses import dataclass, asdict

EXERCISE_LIBRARY = {

    "Ankle pump": {
        "phase": 1,
        "type": "ROM",
        "difficulty": 1,
        "video_path": "videos/ankle_pump.mp4",
        "korean_name": "발목 펌프 운동",
        "note": "발목을 위아래 끝까지 올리고 내립니다"
    },

    "Quad set": {
        "phase": 1,
        "type": "Strength",
        "difficulty": 1,
        "video_path": "videos/Q_set.mp4",
        "korean_name": "허벅지근육 수축 운동",
        "note": "허벅지 밑에 수건이나 베개를 두고 무릎힘으로 10초간 눌러줍니다"
    },

    "Passive knee extension stretch": {
        "phase": 1,
        "type": "Stretch",
        "difficulty": 1,
        "video_path": "videos/passive knee extension.mp4",
        "korean_name": "무릎 펴기 스트레칭",
        "note": "무릎을 쭉 편 상태에서 내 양손으로 무릎을 밑으로 10초간 눌러줍니다"
    },

    "Calf stretch": {
        "phase": 1,
        "type": "Stretch",
        "difficulty": 1,
        "video_path": "videos/Calf stretch.mp4",
        "korean_name": "종아리 근육 스트레칭",
        "note": "발가락 밑에 부분에 수건을 걸고 몸쪽으로 잡아당겨서 10초이상 유지합니다"
    },

    "Assited knee flexion": {
        "phase": 1,
        "type": "ROM",
        "difficulty": 2,
        "video_path": "videos/assited knee flexion.mp4",
        "korean_name": "보조 무릎 구부리기 운동",
        "note": "무릎 앞쪽을 손이나 수건으로 감싸서 몸쪽으로 당깁니다"
    },

    "Heel slide": {
        "phase": 2,
        "type": "ROM",
        "difficulty": 2,
        "video_path": "videos/Heel_slide.mp4",
        "korean_name": "무릎 구부리기 운동",
        "note": "누운상태에서 발 뒷꿈치를 침대에 대고 가능한 범위만큼 왔다갔다 반복합니다"
    },

    "knee flexion_extension": {
        "phase": 2,
        "type": "ROM",
        "difficulty": 2,
        "video_path": "videos/knee flexion_extension.mp4",
        "korean_name": "무릎 보조 굽히고 펴기 운동",
        "note": "앉은상태에서 반대편 발로 무릎을 굽히고 펴고 도와줍니다"
    },

    "Heel prop": {
        "phase": 2,
        "type": "Stretch",
        "difficulty": 2,
        "video_path": "videos/heel prop.mp4",
        "korean_name": "무릎 펴기 운동",
        "note": "발목아래 수건을 놓고 무릎 펴기"
    },

    "Straight leg raise": {
        "phase": 2,
        "type": "Strength",
        "difficulty": 2,
        "video_path": "videos/straight leg raise.mp4",
        "korean_name": "다리 들어올리기 운동",
        "note": "누운상태에서 다리를 위로 들 수 있을만큼 들었다 내렸다 반복합니다"
    },

    "Short arc quad": {
        "phase": 2,
        "type": "Strength",
        "difficulty": 2,
        "video_path": "videos/short arc.mp4",
        "korean_name": "짧은범위 무릎 펴기 운동",
        "note": "베개를 무릎밑에 받치고 무릎을 쭉 펴줍니다"
    },

    "Sit to stand": {
        "phase": 2,
        "type": "Functional",
        "difficulty": 3,
        "video_path": "videos/sit to stand.mp4",
        "korean_name": "앉았다 일어나기 운동",
        "note": "침대에서 걸터 앉아서 워커를 잡고 앉았다 섰다 반복합니다"
    },

}

# =========================
# 1. Membership Functions
# =========================
def triangle(x, a, b, c):
    """
    삼각형 멤버십 함수
    """
    if a == b and x == a:
        return 1.0
    if b == c and x == c:
        return 1.0

    if x < a or x > c:
        return 0.0
    elif x == b:
        return 1.0
    elif a <= x < b:
        if b - a == 0:
            return 0.0
        return (x - a) / (b - a)
    elif b < x <= c:
        if c - b == 0:
            return 0.0
        return (c - x) / (c - b)
    return 0.0


def trapezoid(x, a, b, c, d):
    """
    사다리꼴 멤버십 함수
    shoulder 형태(a==b 또는 c==d)도 처리
    """
    if x < a or x > d:
        return 0.0

    if b <= x <= c:
        return 1.0

    if a <= x < b:
        if b - a == 0:
            return 1.0
        return (x - a) / (b - a)

    if c < x <= d:
        if d - c == 0:
            return 1.0
        return (d - x) / (d - c)

    return 0.0


# =========================
# 2. Fuzzification
# =========================
def fuzzify_pain(pain):
    return {
        "low": trapezoid(pain, 0, 0, 2, 4),
        "medium": triangle(pain, 2, 5, 8),
        "high": trapezoid(pain, 6, 8, 10, 10)
    }


def fuzzify_fatigue(fatigue):
    return {
        "low": trapezoid(fatigue, 0, 0, 2, 4),
        "medium": triangle(fatigue, 2, 5, 8),
        "high": trapezoid(fatigue, 6, 8, 10, 10)
    }


def fuzzify_rom(rom):
    return {
        "poor": trapezoid(rom, 0, 0, 60, 85),
        "fair": triangle(rom, 70, 95, 120),
        "good": trapezoid(rom, 100, 120, 150, 150)
    }


def fuzzify_postop_day(day):
    return {
        "early": trapezoid(day, 0, 0, 3, 10),
        "middle": triangle(day, 7, 14, 28),
        "late": trapezoid(day, 21, 35, 60, 60)
    }


def fuzzify_adherence(adherence):
    return {
        "low": trapezoid(adherence, 0, 0, 30, 50),
        "medium": triangle(adherence, 40, 60, 80),
        "high": trapezoid(adherence, 70, 85, 100, 100)
    }


def fuzzify_swelling(swelling):
    """
    swelling: 0~3
    0 = none, 1 = mild, 2 = moderate, 3 = severe
    """
    return {
        "none": trapezoid(swelling, 0, 0, 0.3, 0.8),
        "mild": triangle(swelling, 0.5, 1.0, 1.8),
        "moderate": triangle(swelling, 1.2, 2.0, 2.6),
        "severe": trapezoid(swelling, 2.3, 2.7, 3.0, 3.0)
    }


# =========================
# 3. Data Classes
# =========================
@dataclass
class PatientInput:
    pain: float
    fatigue: float
    rom: float
    postop_day: int
    adherence: float
    swelling: float = 0.0
    pain_change: float = 0.0
    rom_change: float = 0.0


@dataclass
class Prescription:
    fuzzy_score: float
    level: int
    label: str
    sets: int
    reps: int
    target_flexion: int
    rest_seconds: int
    exercise_list: list
    caution: str
    adjusted_by_safety_filter: bool


# =========================
# 4. Fuzzy Inference
# =========================
def calculate_fuzzy_score(patient: PatientInput):
    p = fuzzify_pain(patient.pain)
    f = fuzzify_fatigue(patient.fatigue)
    r = fuzzify_rom(patient.rom)
    d = fuzzify_postop_day(patient.postop_day)
    a = fuzzify_adherence(patient.adherence)
    s = fuzzify_swelling(patient.swelling)

    rules = []

    # -------------------------
    # 안전 우선 규칙
    # -------------------------
    rules.append(("very_low", max(p["high"], f["high"])))
    rules.append(("very_low", s["severe"]))
    rules.append(("very_low", min(d["early"], p["high"])))

    rules.append(("low", r["poor"]))
    rules.append(("low", min(s["moderate"], p["medium"])))
    rules.append(("low", min(a["low"], d["early"])))
    rules.append(("low", min(p["medium"], f["high"])))
    rules.append(("low", min(p["high"], a["low"])))

    # -------------------------
    # 4번: 초기 단계 억제 규칙 추가
    # -------------------------
    rules.append(("very_low", min(d["early"], p["medium"])))
    rules.append(("low", min(d["early"], r["good"])))
    rules.append(("low", min(d["early"], f["medium"])))
    rules.append(("low", min(d["early"], a["high"])))

    # -------------------------
    # 중간 단계 규칙
    # -------------------------
    rules.append(("moderate", min(p["medium"], f["medium"], r["fair"])))
    rules.append(("moderate", min(d["middle"], r["fair"], p["low"])))
    rules.append(("moderate", min(a["medium"], r["fair"])))
    rules.append(("moderate", min(p["low"], f["medium"], r["fair"])))
    rules.append(("moderate", min(d["late"], r["fair"], a["medium"])))

    # -------------------------
    # 적극적 진행 가능 규칙
    # high 규칙은 조금 더 보수적으로 설정
    # -------------------------
    rules.append(("high", min(p["low"], f["low"], r["good"])))
    rules.append(("high", min(r["good"], a["high"], p["low"], d["late"])))
    rules.append(("high", min(d["late"], r["good"], p["low"], f["low"])))
    rules.append(("high", min(d["middle"], r["good"], a["high"], p["low"])))
    rules.append(("high", min(s["none"], p["low"], a["high"], d["late"])))

    output_centers = {
        "very_low": 15,
        "low": 35,
        "moderate": 60,
        "high": 85
    }

    numerator = 0.0
    denominator = 0.0

    for label, strength in rules:
        numerator += output_centers[label] * strength
        denominator += strength

    if denominator == 0:
        return 50.0

    score = numerator / denominator
    return round(score, 2)


# =========================
# 5. Score -> Level
# =========================
def score_to_level(score):
    """
    조금 더 보수적으로 설정
    """
    if score < 35:
        return 1
    elif score < 55:
        return 2
    elif score < 75:
        return 3
    return 4


def level_to_label(level):
    labels = {
        1: "매우 낮음 / 통증 관리 중심",
        2: "낮음 / 기초 회복 중심",
        3: "중간 / ROM + 근력 강화",
        4: "높음 / 기능 회복 집중"
    }
    return labels[level]


# =========================
# 6. Level -> Prescription
# =========================
def level_to_prescription(level, current_rom):
    table = {
        1: {"sets": 2, "reps": 8, "target_delta": 0, "rest_seconds": 90},
        2: {"sets": 3, "reps": 8, "target_delta": 5, "rest_seconds": 60},
        3: {"sets": 3, "reps": 10, "target_delta": 10, "rest_seconds": 45},
        4: {"sets": 4, "reps": 10, "target_delta": 15, "rest_seconds": 30},
    }

    result = table[level].copy()
    result["target_flexion"] = int(min(current_rom + result["target_delta"], 120))
    return result


# =========================
# 7. 6번: 운동 종류 필터
# =========================
def filter_exercises(level, postop_day):
    """
    수술 후 경과일과 레벨을 함께 반영해서
    실제 추천 운동 종류를 보수적으로 제한
    """

    if postop_day <= 7:

        if level == 1:
            return [
                "Ankle pump",
                "Quad set",
                "Calf stretch"
            ]

        elif level == 2:
            return [
                "Ankle pump",
                "Quad set",
                "Calf stretch",
                "Passive knee extension stretch"
            ]

        else:
            return [
                "Ankle pump",
                "Quad set",
                "Calf stretch",
                "Assited knee flexion",
                "Passive knee extension stretch"
            ]

    # 2주 이내: 아직 보수적
    elif postop_day <= 14:

        if level == 1:
            return [
                "Quad set",
                "Heel slide",
                "Calf stretch",
                "Assited knee flexion"
            ]

        elif level == 2:
            return [
                "Quad set",
                "Heel slide",
                "Heel prop",
                "Assited knee flexion",
                "knee flexion_extension"
            ]

        else:
            return [
                "Short arc quad",
                "Heel slide",
                "Heel prop",
                "knee flexion_extension"
            ]

    # 3주차
    elif postop_day <= 21:

        if level == 1:
            return [
                "Short arc quad",
                "Sit to stand",
                "knee flexion_extension"
            ]

        elif level == 2:
            return [
                "Short arc quad",
                "Straight leg raise",
                "Sit to stand",
                "knee flexion_extension"
            ]

        else:
            return [
                "Straight leg raise",
                "Sit to stand",
                "knee flexion_extension",
                "Short arc quad"
            ]


# =========================
# 8. Safety Filter
# =========================
def apply_safety_filter(patient: PatientInput, level, prescription):
    adjusted = False
    caution_list = []

    safe_level = level

    if patient.pain >= 7:
        safe_level = 1
        adjusted = True
        caution_list.append("통증이 높아 Level 1로 제한")

    if patient.swelling >= 2.5:

        if patient.postop_day <= 14:
            new_level = min(safe_level, 2)

            if new_level != safe_level:
                safe_level = new_level
                adjusted = True
                caution_list.append(
                    "수술 후 14일 이내이며 부종이 있어 운동 강도를 Level 2 이하로 제한했습니다."
                )

        elif patient.postop_day <= 28:
            new_level = min(safe_level, 3)

            if new_level != safe_level:
                safe_level = new_level
                adjusted = True
                caution_list.append(
                    "수술 후 15~28일이며 부종이 있어 운동 강도를 Level 3 이하로 제한했습니다."
                )

        else:
            new_level = max(1, safe_level - 1)

            if new_level != safe_level:
                safe_level = new_level
                adjusted = True
                caution_list.append(
                    "부종이 있어 현재 운동 강도에서 1단계 낮췄습니다."
                )

    if patient.adherence < 50:
        safe_level = min(safe_level, 2)
        adjusted = True
        caution_list.append("전날 수행률이 낮아 세트 증가 제한")

    if patient.pain_change >= 2:
        safe_level = max(1, safe_level - 1)
        adjusted = True
        caution_list.append("통증이 전일 대비 증가하여 1단계 하향")

    if patient.rom_change < 0 and patient.pain_change > 0:
        safe_level = 1
        adjusted = True
        caution_list.append("ROM 감소와 통증 증가 동반: 치료사 확인 권장")

    # 수술 초기 1주 이내: 무조건 Level 2 이하
    if patient.postop_day <= 7:
        if safe_level > 2:
            safe_level = 2
            adjusted = True
            caution_list.append("수술 초기(1주 이내): 강도 Level 2 이하로 제한")

    safe_prescription = level_to_prescription(safe_level, patient.rom)

    if patient.swelling >= 2.5:
        safe_prescription["target_flexion"] = int(min(patient.rom + 5, 120))
        caution_list.append("부종으로 목표 굴곡 증량을 5도로 제한")

    if not caution_list:
        caution_text = "특이사항 없음"
    else:
        caution_text = "; ".join(caution_list)

    return safe_level, safe_prescription, adjusted, caution_text


# =========================
# 9. Main Recommendation Logic
# =========================
def recommend_exercise(patient: PatientInput):
    score = calculate_fuzzy_score(patient)
    initial_level = score_to_level(score)
    initial_prescription = level_to_prescription(initial_level, patient.rom)

    final_level, final_prescription, adjusted, caution = apply_safety_filter(
        patient, initial_level, initial_prescription
    )

    # 6번: 운동 종류 필터 적용
    exercise_list = filter_exercises(final_level, patient.postop_day)

    return Prescription(
        fuzzy_score=score,
        level=final_level,
        label=level_to_label(final_level),
        sets=final_prescription["sets"],
        reps=final_prescription["reps"],
        target_flexion=final_prescription["target_flexion"],
        rest_seconds=final_prescription["rest_seconds"],
        exercise_list=exercise_list,
        caution=caution,
        adjusted_by_safety_filter=adjusted
    )


# =========================
# 10. Print Helper
# =========================
def print_result(patient: PatientInput, result: Prescription):
    print("=" * 80)
    print("환자 입력값")
    for key, value in asdict(patient).items():
        print(f"- {key}: {value}")

    print("-" * 80)
    print("추천 결과")
    for key, value in asdict(result).items():
        print(f"- {key}: {value}")
    print("=" * 80)
    print()


# =========================
# 11. Demo Test
# =========================
def run_demo():
    demo_patients = [
        PatientInput(
            pain=6,
            fatigue=5,
            rom=100,
            postop_day=5,
            adherence=80,
            swelling=1,
            pain_change=0,
            rom_change=2
        ),
        PatientInput(
            pain=2,
            fatigue=2,
            rom=100,
            postop_day=20,
            adherence=90,
            swelling=0,
            pain_change=0,
            rom_change=5
        ),
        PatientInput(
            pain=5,
            fatigue=4,
            rom=85,
            postop_day=10,
            adherence=70,
            swelling=1,
            pain_change=1,
            rom_change=3
        ),
        PatientInput(
            pain=8,
            fatigue=7,
            rom=70,
            postop_day=4,
            adherence=40,
            swelling=3,
            pain_change=3,
            rom_change=-5
        ),
        PatientInput(
            pain=3,
            fatigue=3,
            rom=95,
            postop_day=35,
            adherence=85,
            swelling=0.5,
            pain_change=0,
            rom_change=2
        ),
    ]

    for i, patient in enumerate(demo_patients, start=1):
        print(f"[예시 환자 {i}]")
        result = recommend_exercise(patient)
        print_result(patient, result)


# =========================
# 12. Run
# =========================
if __name__ == "__main__":
    run_demo()
