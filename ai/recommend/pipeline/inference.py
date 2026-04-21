import joblib
import json
import numpy as np
from ai.recommend import calculate_base_g

model = joblib.load("ai/recommend/models/model.pkl")

with open("ai/recommend/models/feature_columns.json", "r") as f:
    feature_cols = json.load(f) 

def predict_recommend_g(
    age,
    neutered,
    weight,
    bcs,
    activity_level,
    season,
    fcs,
    adult_stand_m,
    food_kcal
):
    # 1. base_g 계산
    base_g, goal_weight = calculate_base_g(
        weight=weight,
        age_m=age,
        neutered=neutered,
        bcs=bcs,
        adult_month=adult_stand_m,
        food_kcal=food_kcal
    )

    # 2. feature 구성
    input_dict = {
        "age": age,
        "neutered": int(neutered),
        "weight": weight,
        "bcs": bcs,
        "activity_level": activity_level,
        "season": season,
        "fcs": fcs,
        "adult_stand_m": adult_stand_m,
        "base_g": base_g,
        "goal_weight": goal_weight,
    }

    # 3. 순서 맞추기
    X_input = np.array([[input_dict[col] for col in feature_cols]])

    # 4. 예측
    pred_ratio = model.predict(X_input)[0]

    # 5. 최종 급여량 계산
    recommend_g = base_g * pred_ratio
    recommend_kcal = food_kcal * recommend_g

    return {
        "base_g": round(base_g, 2),
        "adjustment_ratio": round(float(pred_ratio), 3),
        "recommend_g": round(float(recommend_g), 2),
        "recommend_kcal": round(float(recommend_kcal), 2),
        "goal_weight": round(goal_weight, 2),
    }