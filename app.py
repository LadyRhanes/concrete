import streamlit as st
import joblib

from recommendation import predict_mix, recommend_mix
from is456 import classify_grade, check_compliance, GRADE_LIMITS


# --------------------------------------------------
# Load saved model files
# --------------------------------------------------

model = joblib.load("model.pkl")
scaler = joblib.load("scaler.pkl")
feature_importance = joblib.load("feature_importance.pkl")


# --------------------------------------------------
# Page setup
# --------------------------------------------------

st.set_page_config(
    page_title="Concrete Mix Design Assistant",
    page_icon="🏗️",
    layout="centered"
)

st.title("🏗️ Intelligent Concrete Mix Design Assistant")

st.write(
    "Enter the concrete mix proportions below to predict "
    "28-day compressive strength and check IS 456 requirements."
)

st.info(
    "All quantities are in kg/m³. "
    "The total mix weight should be approximately 2400 kg/m³. "
    "Age is fixed at 28 days."
)


# --------------------------------------------------
# Model information
# --------------------------------------------------

with st.expander("Model Information"):

    st.write("**Model:** Support Vector Regression (SVR)")

    st.write("**Train-test split:** 80/20")

    st.write("**Random seed:** 101")

    st.write("**Held-out test RMSE:** 8.04 MPa")

    st.write("**Held-out test R²:** 0.73")


# --------------------------------------------------
# Input section
# --------------------------------------------------

st.header("Concrete Mix Proportions")

cement = st.number_input(
    "Cement (kg/m³)",
    min_value=0.0,
    value=350.0
)

slag = st.number_input(
    "Blast Furnace Slag (kg/m³)",
    min_value=0.0,
    value=100.0
)

flyash = st.number_input(
    "Fly Ash (kg/m³)",
    min_value=0.0,
    value=50.0
)

water = st.number_input(
    "Water (kg/m³)",
    min_value=0.0,
    value=180.0
)

superplasticizer = st.number_input(
    "Superplasticizer (kg/m³)",
    min_value=0.0,
    value=5.0
)

coarseaggregate = st.number_input(
    "Coarse Aggregate (kg/m³)",
    min_value=0.0,
    value=1000.0
)

fineaggregate = st.number_input(
    "Fine Aggregate (kg/m³)",
    min_value=0.0,
    value=700.0
)


# Age is fixed at 28 days according to the PS
age = 28


target_grade = st.selectbox(
    "Target Concrete Grade",
    ["M20", "M25", "M30", "M35", "M40"]
)


# --------------------------------------------------
# Prediction button
# --------------------------------------------------

predict_button = st.button(
    "Predict Concrete Strength",
    type="primary"
)


# --------------------------------------------------
# Main prediction logic
# --------------------------------------------------

if predict_button:

    # Keep exactly the same feature order used during training
    mix = [
        cement,
        slag,
        flyash,
        water,
        superplasticizer,
        coarseaggregate,
        fineaggregate,
        age
    ]


    # --------------------------------------------------
    # Basic validation
    # --------------------------------------------------

    if cement <= 0:

        st.error(
            "Cement must be greater than 0 kg/m³."
        )

    else:

        total_weight = sum(mix[:-1])

        if total_weight < 1800 or total_weight > 2800:

            st.warning(
                f"Total mix weight is approximately "
                f"{total_weight:.1f} kg/m³. "
                "The expected value is approximately "
                "2400 kg/m³."
            )


        # --------------------------------------------------
        # ML prediction
        # --------------------------------------------------

        predicted_strength = predict_mix(
            model,
            scaler,
            mix
        )

        predicted_grade = classify_grade(
            predicted_strength
        )


        st.header("Prediction Result")


        col1, col2 = st.columns(2)


        with col1:

            st.metric(
                "Predicted 28-day Compressive Strength",
                f"{predicted_strength:.2f} MPa"
            )


        with col2:

            st.metric(
                "Predicted Concrete Grade",
                predicted_grade
            )


        # --------------------------------------------------
        # Model performance
        # --------------------------------------------------

        st.header("Model Performance")


        col1, col2 = st.columns(2)


        with col1:

            st.metric(
                "Test RMSE",
                "8.04 MPa"
            )


        with col2:

            st.metric(
                "Test R²",
                "0.73"
            )


        st.caption(
            "Support Vector Regression (SVR) | "
            "80/20 train-test split | "
            "Random seed = 101"
        )


        # --------------------------------------------------
        # IS 456 compliance check
        # --------------------------------------------------

        st.header("IS 456 Compliance Check")


        limits = GRADE_LIMITS[target_grade]


        compliance = check_compliance(
            cement,
            water,
            target_grade
        )


        # Check whether predicted strength reaches target
        strength_ok = (
            predicted_strength >= limits["min_strength"]
        )


        st.write(
            f"**Target Grade:** {target_grade}"
        )


        st.write(
            f"**Required minimum strength:** "
            f"{limits['min_strength']} MPa"
        )


        st.write(
            f"**Minimum cement required:** "
            f"{limits['min_cement']} kg/m³"
        )


        st.write(
            f"**Actual water-cement ratio:** "
            f"{compliance['wc_ratio']:.3f}"
        )


        st.write(
            f"**Maximum allowed water-cement ratio:** "
            f"{limits['max_wc']:.2f}"
        )


        # --------------------------------------------------
        # Strength check
        # --------------------------------------------------

        if strength_ok:

            st.success(
                "✓ Predicted strength satisfies "
                "the target grade."
            )

        else:

            st.error(
                "✗ Predicted strength is below "
                "the target grade."
            )


        # --------------------------------------------------
        # Minimum cement check
        # --------------------------------------------------

        if compliance["cement_ok"]:

            st.success(
                "✓ Minimum cement requirement "
                "is satisfied."
            )

        else:

            st.error(
                "✗ Minimum cement requirement "
                "is NOT satisfied."
            )


        # --------------------------------------------------
        # Water-cement ratio check
        # --------------------------------------------------

        if compliance["wc_ok"]:

            st.success(
                "✓ Water-cement ratio requirement "
                "is satisfied."
            )

        else:

            st.error(
                "✗ Water-cement ratio exceeds "
                "the IS 456 limit."
            )


        # --------------------------------------------------
        # Overall compliance
        # --------------------------------------------------

        if strength_ok and compliance["compliant"]:

            st.success(
                "✓ The mix satisfies both the "
                "target strength and the selected "
                "IS 456 requirements."
            )

        else:

            st.warning(
                "ML prediction and IS 456 compliance "
                "are evaluated separately. A mix may "
                "have adequate predicted strength while "
                "still failing an IS 456 requirement."
            )


        # --------------------------------------------------
        # Recommendation engine
        # --------------------------------------------------

        st.header("Mix Recommendation")


        recommendation = recommend_mix(
            model,
            scaler,
            mix,
            predicted_strength,
            target_grade,
            feature_importance
        )


        # --------------------------------------------------
        # No recommendation needed
        # --------------------------------------------------

        if recommendation["type"] == "NONE":

            st.success(
                "No adjustment is currently required "
                "for the selected target grade."
            )


        # --------------------------------------------------
        # Recommendation exists
        # --------------------------------------------------

        else:

            ingredient = recommendation["ingredient"]

            direction = recommendation["direction"]

            delta = recommendation["delta"]

            new_prediction = recommendation["new_prediction"]


            if direction == "increase":

                action = "Increase"

            else:

                action = "Decrease"


            st.subheader(
                f"{action} {ingredient}"
            )


            st.write(
                f"Recommended adjustment: "
                f"**{action.lower()} {ingredient} by "
                f"approximately {delta:.2f} kg/m³**."
            )


            st.write(
                f"**Reason:** "
                f"{recommendation['reason']}"
            )


            # Show updated prediction
            st.metric(
                "Updated Predicted Strength",
                f"{new_prediction:.2f} MPa",
                delta=(
                    f"{new_prediction - predicted_strength:.2f} MPa"
                )
            )


            st.caption(
                "The updated prediction was obtained by "
                "rerunning the ML model after applying "
                "the recommended adjustment."
            )