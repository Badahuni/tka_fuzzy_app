import random


def adaptive_adjustment(current_score, current_data, previous_data):
    adjusted_score = current_score
    reasons = []

    if previous_data is None:
        reasons.append("이전 기록이 없어 적응형 보정 없이 기본 점수를 사용했습니다.")
        return round(adjusted_score, 2), reasons

    pain_delta = current_data["pain"] - previous_data["pain"]
    fatigue_delta = current_data["fatigue"] - previous_data["fatigue"]
    rom_delta = current_data["rom"] - previous_data["rom"]

    if pain_delta >= 2:
        adjusted_score -= 10
        reasons.append("이전 기록보다 통증이 증가하여 -10점 조정했습니다.")

    if fatigue_delta >= 2:
        adjusted_score -= 5
        reasons.append("이전 기록보다 피로도가 증가하여 -5점 조정했습니다.")

    if rom_delta >= 5:
        adjusted_score += 5
        reasons.append("이전 기록보다 ROM이 향상되어 +5점 조정했습니다.")

    if current_data["adherence"] >= 80:
        adjusted_score += 5
        reasons.append("이전 기록 기준 순응도가 높아 +5점 조정했습니다.")
    elif current_data["adherence"] < 50:
        adjusted_score -= 5
        reasons.append("이전 기록 기준 순응도가 낮아 -5점 조정했습니다.")

    if current_data["postop_day"] <= 3 and adjusted_score > 69:
        adjusted_score = 69
        reasons.append("수술 초기 단계이므로 최대 강도를 중간 수준으로 제한했습니다.")

    adjusted_score = max(0, min(100, adjusted_score))

    if not reasons:
        reasons.append("이전 기록과 큰 차이가 없어 점수를 그대로 유지했습니다.")

    return round(adjusted_score, 2), reasons


def classify_intensity(score):
    if score < 40:
        return "Low"
    elif score < 70:
        return "Moderate"
    else:
        return "High"


EXERCISE_LIBRARY = [
    # Low
    {
        "name": "발목 펌프 운동",
        "level": "Low",
        "sets": 3,
        "reps": 10,
        "type": "ROM",
        "video_link": "https://youtu.be/_1zihncx4ZQ?si=zZh8r1txLGsDfT6N"
    },
    {
        "name": "무릎굽히고 펴기",
        "level": "Low",
        "sets": 3,
        "reps": 10,
        "type": "ROM",
        "video_link": "https://youtu.be/dwmr-AQmm-Q?si=8lk71irj_VqL9U0q"
    },
    {
        "name": "허벅지 기초긴장",
        "level": "Low",
        "sets": 3,
        "reps": 10,
        "type": "Strength",
        "video_link": "https://youtube.com/shorts/0af1u1JrGYY?si=dDqTFU7hhqYb-fWg"
    },
    {
        "name": "수동 무릎 구부리기",
        "level": "Low",
        "sets": 2,
        "reps": 10,
        "type": "ROM",
        "video_link": "https://youtube.com/shorts/D76FGNkZCAc?si=OI6HbFh2SLX5d1Vb"
    },

    # Moderate

    {
        "name": "무릎 굴곡신전 능동운동",
        "level": "Moderate",
        "sets": 3,
        "reps": 10,
        "type": "ROM",
        "video_link": "https://youtube.com/shorts/hBqSeoD1YfU?si=ocO_FU5VLZb9v0cA"
    },
    {
        "name": "직거상 운동",
        "level": "Moderate",
        "sets": 3,
        "reps": 10,
        "type": "Strength",
        "video_link": "https://www.youtube.com/watch?v=8M7nR6F7xJQ"
    },
    {
        "name": "침대에서 앉았다 일어서기",
        "level": "Moderate",
        "sets": 3,
        "reps": 10,
        "type": "Strength",
        "video_link": "https://www.youtube.com/watch?v=aclHkVaku9U"
    },
    {
        "name": "Step-up",
        "level": "Moderate",
        "sets": 3,
        "reps": 10,
        "type": "Function",
        "video_link": "https://www.youtube.com/watch?v=WCFCdxz7XJ4"
    },



    # High
    {
        "name": "Step-up",
        "level": "Moderate",
        "sets": 3,
        "reps": 10,
        "type": "Function",
        "video_link": "https://www.youtube.com/watch?v=WCFCdxz7XJ4"
                    },
    {
        "name": "sit to stand",
        "level": "High",
        "sets": 3,
        "reps": 12,
        "type": "Strength",
        "video_link": "https://www.youtube.com/watch?v=QOVaHwm-Q6U"
    },
    {
        "name": "Balance training",
        "level": "High",
        "sets": 3,
        "reps": 10,
        "type": "Balance",
        "video_link": "https://www.youtube.com/watch?v=Ivyq8e7O5mA"
    },
    {
        "name": "Stair training",
        "level": "High",
        "sets": 3,
        "reps": 10,
        "type": "Function",
        "video_link": "https://www.youtube.com/watch?v=WCFCdxz7XJ4"
    },
    {
        "name": "저항성 무릎 운동",
        "level": "High",
        "sets": 3,
        "reps": 12,
        "type": "Strength",
        "video_link": "https://www.youtube.com/watch?v=aclHkVaku9U"
    }
]


def prescribe_exercises(intensity):
    candidates = [ex for ex in EXERCISE_LIBRARY if ex["level"] == intensity]

    rom = [ex for ex in candidates if ex["type"] == "ROM"]
    strength = [ex for ex in candidates if ex["type"] == "Strength"]

    selected = []

    if rom:
        selected.append(random.choice(rom))

    if strength:
        strength_candidates = [ex for ex in strength if ex not in selected]
        if strength_candidates:
            selected.append(random.choice(strength_candidates))

    remaining = [ex for ex in candidates if ex not in selected]

    if remaining:
        selected += random.sample(remaining, min(2, len(remaining)))

    return selected