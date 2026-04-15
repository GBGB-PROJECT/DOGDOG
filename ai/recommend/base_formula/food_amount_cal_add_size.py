# 저체중(BCS 1 ~ 4) = 체중 증가가 필요한 강아지
def get_low_weight_factor(BCS):
    if BCS == 1:
        return 1.8
    elif BCS == 2:
        return 1.6
    elif BCS == 3:
        return 1.4
    elif BCS == 4:
        return 1.2

# adult_month
# size(견종)에 따른 생애주기 구분 -> 성견 유무 구하기
# 견종 -> size 구분
# size -> 성견 기준 개월 도출

# 계수
# (임신/수유) > 질병->ai > 비만 > 나이(성장기, 노견)
def get_factor(age_m, BCS, neutered, adult_month):
    # 성견 - 기준 정하기*****
    if age_m >= adult_month:
        #저체중
        if BCS <= 4:
            return get_low_weight_factor(BCS)

        #비만*****

        # 특이사항 없는 반려견 (BCS 5)
        # 중성화 여부
        if neutered:
            return 1.6
        
        else:
            return 1.8

    # 성장기
    else: 
        # 0 ~ 4개월
        if age_m <= 4:
            return 3

        else: # < 성견
            return 2

#--------------------------------------------------------------
# RER
#ver1
def cal_RER(weight: float) -> float:
    RER = 70 * weight**0.75

    return RER

#ver2
# def cal_RER(weight: float) -> float:
#     if weight >= 2 and weight <45:  # 2 ~ 45kg
#         return 30 * weight + 70

#     else: # 그 외
#         return 70 * weight**0.75

#---------------------------------------------------------------

# 비만 강아지 보정(BCS 6 ~ 9)
#ver1
def get_high_weight_factor(BCS):
    if BCS == 6:
        return 0.9, 1.1
    elif BCS == 7:
        return 0.8, 1.2
    elif BCS == 8:
        return 0.77, 1.3
    elif BCS == 9:
        return 0.74, 1.4

#ver2
# def get_high_weight_factor(BCS):
#     if BCS == 6:
#         return 0.6, 1.1
#     elif BCS == 7:
#         return 0.5, 1.2
#     elif BCS == 8:
#         return 0.47, 1.3
#     elif BCS == 9:
#         return 0.44, 1.4

# ------------------------------- 진짜 계산 -------------------------------
# 하루 권장 급여량 계산 ***
def calculate_base_g(
        weight: float, 
        age_m: int, 
        neutered: bool, 
        bcs: int, 
        adult_month: int, 
        food_kcal: float
    ) -> float:
    RER = cal_RER(weight)

    # DER
    w = get_factor(age_m, bcs, neutered, adult_month)
    DER = RER * w

    base_g = DER / food_kcal
    goal_weight = base_g

    if 6 <= bcs <= 9:
        g_factor, w_factor = get_high_weight_factor(bcs)
        DER = DER * g_factor
        goal_weight = weight / w_factor
        print(f'목표 몸무게는 {goal_weight:.2f}kg 입니다.')

    print(f'일일 칼로리는 {DER:.2f}kcal 입니다.')
    print(f'하루 권장 급여량은 {base_g:.2f}g 입니다.')

    return base_g, goal_weight