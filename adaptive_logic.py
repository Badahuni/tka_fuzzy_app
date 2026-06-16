import random
from fuzzy_rehab_manual import EXERCISE_LIBRARY

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



def prescribe_exercises(intensity):

    candidates = [
        ex for ex in EXERCISE_LIBRARY
        if ex["level"] == intensity
    ]

    return candidates