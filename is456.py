GRADE_LIMITS = {
    "M20": {
        "min_strength": 20,
        "min_cement": 300,
        "max_wc": 0.55
    },
    "M25": {
        "min_strength": 25,
        "min_cement": 300,
        "max_wc": 0.50
    },
    "M30": {
        "min_strength": 30,
        "min_cement": 320,
        "max_wc": 0.45
    },
    "M35": {
        "min_strength": 35,
        "min_cement": 340,
        "max_wc": 0.45
    },
    "M40": {
        "min_strength": 40,
        "min_cement": 360,
        "max_wc": 0.40
    }
}


def classify_grade(strength):
    if strength >= 40:
        return "M40"
    elif strength >= 35:
        return "M35"
    elif strength >= 30:
        return "M30"
    elif strength >= 25:
        return "M25"
    elif strength >= 20:
        return "M20"
    else:
        return "Below M20"


def check_compliance(cement, water, target_grade):
    limits = GRADE_LIMITS[target_grade]

    wc_ratio = water / cement

    cement_ok = cement >= limits["min_cement"]
    wc_ok = wc_ratio <= limits["max_wc"]

    return {
        "cement_ok": cement_ok,
        "wc_ok": wc_ok,
        "wc_ratio": wc_ratio,
        "compliant": cement_ok and wc_ok
    }
# print(classify_grade(37))
# print(classify_grade(42))
# print(classify_grade(18))
# print(check_compliance(320, 140, "M30"))