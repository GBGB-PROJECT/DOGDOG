from google.colab import drive
import os
import json
import pandas as pd

# json_folder = "/content/drive/MyDrive/ai/data/raw_dataset/sample_labeling_data/반려견"  # 원본데이터 위치
json_folder = "/content/drive/MyDrive/ai/data/raw_dataset/data/Training"  # 원본데이터 위치
output_csv  = "/content/drive/MyDrive/ai/data/interim/basic_dataset.csv"  # csv결과 저장 위치


def safe_get(data, keys, default=None):
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def parse_sex(sex_code):
    """
    sex_code 예: IF, IM ...
    현재는 성별만 단순 추출하고,
    중성화 여부는 확실하지 않으므로 None 처리
    """
    if not sex_code:
        return None, None

    sex_code = str(sex_code).upper()

    # 끝 글자 기준으로 단순 추정
    if sex_code == "IF":
        return "female", 1
    elif sex_code == "IM":
        return "male", 1
    elif sex_code == "SF":
        return "female", 0
    elif sex_code == "CM":
        return "male", 0

    return None, None

def age_to_month(age):
    month = age * 12
    return month


def map_activity_level(exercise_value):
    """
    AI-Hub exercise:
    1: 매일 30분 이하
    2: 매일 30분 이상
    3: 매일 1시간 이상
    """
    if exercise_value in [1, 2, 3]:
        return int(exercise_value)
    return None


def map_disease(disease_code):
    """
    NOR이면 질병 없음(0), 그 외는 질병 있음(1)으로 단순화
    """
    if disease_code is None:
        return None

    disease_code = str(disease_code).upper()
    return 0 if disease_code == "NOR" else 1


def map_food_count(food_count):
    if food_count == 4:
      food_count = 3
    return food_count


def extract_basic_row(data, filename=""):
    row = {}

    row["source_file"] = filename
    # 품종그룹(SS[5kg미만 단모],MS[5-10kg미만 단모],LS[10kg 이상 단모],SL[5kg미만 장보],ML[5-10kg미만 장모],LL[10kg이상 장모],UK[알 수 없음, 장/단구분 어려움])
    # -> XS, S, M, L, XL
    row["breed"] = safe_get(data, ["metadata", "id", "breed"])
    row["group"] = safe_get(data, ["metadata", "id", "group"])

    row["age"] = safe_get(data, ["metadata", "id", "age"])
    # row["age"]= age_to_month(safe_get(data, ["metadata", "id", "age"]))

    row["sex_code"] = safe_get(data, ["metadata", "id", "sex"])
    sex, neutered = parse_sex(row["sex_code"])
    row["sex"] = sex
    row["neutered"] = neutered

    row["weight"] = safe_get(data, ["metadata", "physical", "weight"])
    row["bcs"] = safe_get(data, ["metadata", "physical", "BCS"])

    exercise = safe_get(data, ["metadata", "breeding", "exercise"])
    row["activity_level"] = map_activity_level(exercise)

    row["food_count"] = safe_get(data, ["metadata", "breeding", "food-count"])
    row["defecation"] = safe_get(data, ["metadata", "breeding", "defecation"])

    row["disease_code"] = safe_get(data, ["metadata", "medical", "disease"])
    row["disease"] = map_disease(row["disease_code"])

    return row


rows = []
seen_mission_ids = set()

files = [f for f in os.listdir(json_folder) if f.endswith(".json")]

for filename in files:
    file_path = os.path.join(json_folder, filename)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    pet_id = safe_get(data, ["metadata", "id", "mission-id"])

    # 이미 저장된 강아지면 건너뜀
    if pet_id in seen_mission_ids:
        continue

    row = extract_basic_row(data, filename)
    rows.append(row)
    seen_mission_ids.add(pet_id)

basic_df = pd.DataFrame(rows)

print("중복 제거 후 행 수:", len(basic_df))

print("컬럼:", basic_df.columns.tolist())
print(basic_df.head())

basic_df.to_csv(output_csv, index=False, encoding="utf-8-sig")
print("저장 완료:", output_csv)

#---------- 결과 확인 ----------
# basic_df = pd.read_csv(output_csv)
# basic_df.info()
# basic_df
# basic_df.isnull().sum()  # neutered에만 852 null 존재
# basic_df["sex_code"].value_counts(dropna=False)
# basic_df["disease_code"].value_counts(dropna=False)
# basic_df["food_count"].value_counts(dropna=False)
# basic_df["group"].value_counts(dropna=False)