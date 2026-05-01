
def move_month(year: int, month: int, diff: int):
    # 🔥 생산관리/재고현황 월 이동 공통 계산
    month_index = (year * 12) + (month - 1) + diff
    new_year = month_index // 12
    new_month = (month_index % 12) + 1
    return new_year, new_month
