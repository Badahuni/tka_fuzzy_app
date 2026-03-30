def triangle(x, a, b, c):
    if x <= a or x >= c:
        return 0.0
    elif x == b:
        return 1.0
    elif a < x < b:
        return (x - a) / (b - a)
    elif b < x < c:
        return (c - x) / (c - b)
    return 0.0


def trapezoid(x, a, b, c, d):
    if x <= a or x >= d:
        return 0.0
    elif b <= x <= c:
        return 1.0
    elif a < x < b:
        return (x - a) / (b - a)
    elif c < x < d:
        return (d - x) / (d - c)
    return 0.0


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


def calculate_fuzzy_score(pain, fatigue, rom, postop_day, adherence):
    p = fuzzify_pain(pain)
    f = fuzzify_fatigue(fatigue)
    r = fuzzify_rom(rom)
    d = fuzzify_postop_day(postop_day)
    a = fuzzify_adherence(adherence)

    rules = []

    rule1 = min(p["low"], f["low"], r["good"])
    rules.append(("high", rule1))

    rule2 = min(p["medium"], f["medium"], r["fair"])
    rules.append(("moderate", rule2))

    rule3 = max(p["high"], f["high"])
    rules.append(("low", rule3))

    rule4 = min(d["early"], p["high"])
    rules.append(("low", rule4))

    rule5 = min(r["good"], a["high"])
    rules.append(("high", rule5))

    rule6 = r["poor"]
    rules.append(("low", rule6))

    rule7 = min(d["middle"], r["fair"], p["low"])
    rules.append(("moderate", rule7))

    rule8 = min(d["late"], r["good"], p["low"], f["low"])
    rules.append(("high", rule8))

    output_centers = {
        "low": 30,
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