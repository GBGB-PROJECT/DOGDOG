from ai.recommend import calculate_base_g

# weight = 7.5
# age_m = 13 # 개월수
# neutered = True
# BCS = 6
# adult_stand_m = 13
# food_kcal = 4.005

base_g, goal_weight = calculate_base_g(
        weight=7.5, 
        age_m=14, 
        neutered=True, 
        bcs=4, 
        adult_month=13, 
        food_kcal=4.005
    )

base_g = round(base_g, 2)
goal_weight = round(goal_weight, 2)

print(base_g, goal_weight)
'''
python -m ai.test.test_base_formula
'''
