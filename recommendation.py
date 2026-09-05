import pandas as pd

from is456 import GRADE_LIMITS, check_compliance


FEATURE_NAMES = [
    "cement",
    "slag",
    "flyash",
    "water",
    "superplasticizer",
    "coarseaggregate",
    "fineaggregate",
    "age"
]


def predict_mix(model, scaler, mix):
    mix_df = pd.DataFrame([mix], columns=FEATURE_NAMES)
    scaled_mix = scaler.transform(mix_df)
    prediction = model.predict(scaled_mix)[0]
    return prediction


def test_change(model, scaler, mix, feature_index, change):
    new_mix = mix.copy()
    new_mix[feature_index] += change

    prediction = predict_mix(
        model,
        scaler,
        new_mix
    )

    return prediction


def find_best_change(
    model,
    scaler,
    mix,
    feature_index,
    delta=20
):
    increase_prediction = test_change(
        model,
        scaler,
        mix,
        feature_index,
        delta
    )

    decrease_prediction = test_change(
        model,
        scaler,
        mix,
        feature_index,
        -delta
    )

    if increase_prediction > decrease_prediction:
        return "increase", delta, increase_prediction
    else:
        return "decrease", delta, decrease_prediction


def recommend_strength_change(
    model,
    scaler,
    mix,
    feature_importance
):
    ingredient_indices = {
        "cement": 0,
        "slag": 1,
        "flyash": 2,
        "water": 3,
        "superplasticizer": 4,
        "coarseaggregate": 5,
        "fineaggregate": 6
    }

    best_feature = max(
        ingredient_indices,
        key=lambda x: feature_importance[
            ingredient_indices[x]
        ]
    )

    index = ingredient_indices[best_feature]

    direction, delta, new_prediction = find_best_change(
        model,
        scaler,
        mix,
        index
    )

    return {
        "ingredient": best_feature,
        "direction": direction,
        "delta": delta,
        "new_prediction": new_prediction
    }


def recommend_mix(
    model,
    scaler,
    mix,
    predicted_strength,
    target_grade,
    feature_importance
):
    cement = mix[0]
    water = mix[3]

    limits = GRADE_LIMITS[target_grade]

    compliance = check_compliance(
        cement,
        water,
        target_grade
    )

    # Check minimum cement requirement first
    if not compliance["cement_ok"]:
        required_cement = limits["min_cement"]
        increase = required_cement - cement

        new_mix = mix.copy()
        new_mix[0] += increase

        new_prediction = predict_mix(
            model,
            scaler,
            new_mix
        )

        return {
            "type": "IS456",
            "ingredient": "cement",
            "direction": "increase",
            "delta": increase,
            "new_prediction": new_prediction,
            "reason": "Minimum cement requirement is not satisfied."
        }

    # Check maximum water-cement ratio
    if not compliance["wc_ok"]:
        max_wc = limits["max_wc"]

        required_water = cement * max_wc
        decrease = water - required_water

        new_mix = mix.copy()
        new_mix[3] -= decrease

        new_prediction = predict_mix(
            model,
            scaler,
            new_mix
        )

        return {
            "type": "IS456",
            "ingredient": "water",
            "direction": "decrease",
            "delta": decrease,
            "new_prediction": new_prediction,
            "reason": "Water-cement ratio exceeds the IS 456 limit."
        }

    # Check predicted strength
    if predicted_strength < limits["min_strength"]:
        recommendation = recommend_strength_change(
            model,
            scaler,
            mix,
            feature_importance
        )

        return {
            "type": "STRENGTH",
            "ingredient": recommendation["ingredient"],
            "direction": recommendation["direction"],
            "delta": recommendation["delta"],
            "new_prediction": recommendation["new_prediction"],
            "reason": "Predicted strength is below the target grade."
        }

    return {
        "type": "NONE",
        "reason": "Mix satisfies the target strength and IS 456 checks."
    }