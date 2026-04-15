# 수유 - 젖먹이는 강아지 수
def get_lactation_factor(num):
    if num == 1:
        return 3
    elif num == 2:
        return 3.5
    elif 3 <= num <= 4:
        return 4
    elif 5 <= num <= 6:
        return 5
    elif 7 <= num <= 8:
        return 5.5
    else: # 9마리 이상
        return 6
    
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

#size에 따른 성견/성장기 구분기준 개월 구하기
def size_standard(size):
    if size == 'xs':
        return 8
    elif size == 's':
        return 10
    elif size == 'm':
        return 12
    elif size == 'l':
        return 15
    elif size == 'xl':
        return 18


# 계수
# 임신/수유 > 질병 > 비만 > 나이(성장기, 노견)
def get_factor(age_m, pregnant, num_puppies, BCS, neutered, size):
    # 성견 - 기준 정하기*****
    if age_m >= size_standard(size):
        #임신/수유
        if pregnant: # 임신 초기/후기 구분 예정*****
            return 3
        if num_puppies >= 1:
            return get_lactation_factor(num_puppies)
        
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

#-----------------------------------------------------------
name = "대추"
print(f"----------- {name}의 하루 권장 급여량 계산 -----------")
# print("강아지의 정보를 입력해주세요.")
# 변수
# weight = input("몸무게(kg)> ")
# age_m = input("나이(개월수)> ")
# neutered = input("중성화 여부(t/f)> ")
# pregnant = input("임신 여부(t/f)>")
# num_puppies = input("수유 중인 강아지의 수")
# BCS = input("비만 충질 지수(1~9)> ")
# size = input("크기(xs,s,m,l,xl)>")
# activity_level = input("활동레벨> ")
# food_kcal = input("사료 1g 당 kcal> ")

weight = 7.5
age_m = 13 # 개월수
neutered = True
pregnant = False
num_puppies = 0
BCS = 6
size = 's'  # xs, s, m, l, xl 
# activity_level = input("활동레벨> ")
food_kcal = 4.005

# RER
#ver1
RER = 70 * weight**0.75

#ver2
# def cal_RER(weight):
#     if weight >= 2 and weight <45:  # 2 ~ 45kg
#         return 30 * weight + 70

#     else: # 그 외
#         return 70 * weight**0.75

# RER = cal_RER(weight)


# 하루 권장 급여량 계산
# DER
w = get_factor(age_m, pregnant, num_puppies, BCS, neutered, size)
DER = RER * w


# 비만 강아지 보정(BCS 6 ~ 9)
#ver1
# def get_high_weight_factor(BCS):
#     if BCS == 6:
#         return 0.9, 1.1
#     elif BCS == 7:
#         return 0.8, 1.2
#     elif BCS == 8:
#         return 0.77, 1.3
#     elif BCS == 9:
#         return 0.74, 1.4

#ver2
def get_high_weight_factor(BCS):
    if BCS == 6:
        return 0.6, 1.1
    elif BCS == 7:
        return 0.5, 1.2
    elif BCS == 8:
        return 0.47, 1.3
    elif BCS == 9:
        return 0.44, 1.4

if 6 <= BCS <= 9:
    g_factor, w_factor = get_high_weight_factor(BCS)
    DER = DER * g_factor
    goal_weight = weight / w_factor
    print(f'목표 몸무게는 {goal_weight:.2f}kg 입니다.')


result = DER / food_kcal

print(f'일일 칼로리는 {DER:.2f}kcal 입니다.')
print(f'하루 권장 급여량은 {result:.2f}g 입니다.')