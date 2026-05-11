from backend.app.ai.recommend import predict_recommend_g

guide_feeding = predict_recommend_g(
    age = 23,
    neutered = 1,
    weight = 7.5 ,
    bcs = 6,
    activity_level = 2,
    season = 1,
    fcs = 3,
    adult_stand_m = 13,
    food_kcal = 4.005
)
print(guide_feeding)

'''
python -m ai.test.test_inference
'''