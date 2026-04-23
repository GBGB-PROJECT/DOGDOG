import pandas as pd
import numpy as np

input_csv  = "/content/drive/MyDrive/ai/data/interim/basic_dataset.csv"
output_csv = "/content/drive/MyDrive/ai/data/interim/feature_dataset.csv"

df = pd.read_csv(input_csv)

def map_group_to_size(group):
    group = str(group).upper()

    if group in ["SS"]:
        return "XS", 11
    if group in ["SL"]:
        return "S", 13
    if group in ["MS", "ML"]:
        return "M", 15
    if group in ["LS"]:
        return "L", 19
    return "XL", 25


def map_defecation_to_stool_score(defecation):
    if defecation:
        # return np.random.choice([1, 2, 3, 4, 5, 6, 7], p=[0.1, 0.1, 0.6, 0.05, 0.05, 0.05, 0.05])
        return np.random.choice([1, 2, 3, 4, 5, 6, 7], p=[0.1, 0.1, 0.4, 0.1, 0.1, 0.1, 0.1])
    return 3


np.random.seed(42)

# 1. size 추가
df[["size", "adult_stand_m"]] = df["group"].apply(
    lambda x: pd.Series(map_group_to_size(x))
)

# 2. season 더미 추가
df["season"] = np.random.choice([1, 2, 3, 4], p=[0.2, 0.3, 0.2, 0.3], size=len(df))  # 봄, 여름, 가을, 겨울

# 3. food_kcal 더미 추가
df["food_kcal"] = np.round(np.random.uniform(3.08, 4.25, size=len(df)), 2)

# 4. stool_score 추가
# df["stool_score"] = np.random.choice(
#     [1, 2, 3, 4, 5, 6, 7],
#     p=[0.1, 0.1, 0.4, 0.1, 0.1, 0.1, 0.1],
#     size=len(df)
# )
df["stool_score"] = np.random.choice(
    [1, 2, 3, 4, 5, 6, 7],
    p=[0.1, 0.1, 0.6, 0.05, 0.05, 0.05, 0.05],
    size=len(df)
)

print(df.head())
print(df.columns.tolist())

df.to_csv(output_csv, index=False, encoding="utf-8-sig")
print("저장 완료:", output_csv)

#---------- 결과 확인 ----------
# DF = pd.read_csv(output_csv)
# DF.info()
# DF.head()
# DF["stool_score"].value_counts(dropna=False)
# DF["season"].value_counts(dropna=False)