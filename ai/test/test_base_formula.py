from ai.recommend import calculate_base_g

# weight = 7.5
# age_m = 13 # 개월수
# neutered = True
# BCS = 6
# adult_month = 13
# food_kcal = 4.005

base_g, goal_weight = calculate_base_g(
        weight=7.5, 
        age_m=14, 
        neutered=True, 
        bcs=6, 
        adult_month=13, 
        food_kcal=4.005
    )

print(base_g)