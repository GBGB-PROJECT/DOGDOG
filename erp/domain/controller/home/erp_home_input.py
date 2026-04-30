
"""
이 파일은 API를 전달받았다 가정하고(raw, api에서...)  
=> get_raw_data
가공을 해서 
view 출력 가능 형태로 전환
"""
## API로부터 받은 raw 데이터(예시) => 데이터가 확인이 되면 그냥 가지고만 오면 된다.(이거는 예시라 작성된 것)
def get_home_view_data():
# [RAW DATA] 이곳에서 API 데이터를 호출하고 processed_data에서 전처리 하면 됨.
    raw_total_sales = 25000000
    raw_yoy_growth = 53
    raw_sales_qty = 4500
    
    raw_yearly_rate = 0.5
    raw_monthly_rate = 0.85
    raw_weekly_rate = 0.75
    year = 2026
    
    raw_monthly_goal = 3500000
    raw_weekly_goal = 750000

    ## 생산 하이라이트
    monthly_production_qty = 354000 # 이번달 생산량
    expected_incoming_qty = 12000 # 입고 예정
    current_total_inventory = 53000 # 현재 총 재고량
    monthly_avg_sales_qty = 13500 # 월 평균 판매량

    ## 건사료/습식사료/간식 (전체 제고를 100으로 백분률로 입력)
    dry_feed= 60
    wet_feed= 25
    snack= 15

### 1. 매출 하이라이트
    sales_processed_data = {
        # 매출 하이라이트 (hd용)
        "total_sale": f"{raw_total_sales:,}",
        "last_year_growth": f"{raw_yoy_growth}",
        "total_sale_value": f"{raw_sales_qty:,}",
        "growth_goal": f"{raw_yearly_rate * 100}",
        "year": year,

        # 목표 달성률 및 차트용 (hd용)
        "month_rate": raw_monthly_rate, # 차트용은 숫자로 전달 (0.85)
        "month_rate_text": f"{raw_monthly_rate * 100}", # 텍스트용 (85.0)
        "month_goal": f"{raw_monthly_goal // 10000:,}", # 만원 단위 절삭
        
        "week_rate": raw_weekly_rate,
        "week_rate_text": f"{raw_weekly_rate * 100}",
        "week_goal": f"{raw_weekly_goal // 10000:,}",
    }

### 3. 생산 제고 하이라이트
    inventory_processed_data = {
        "monthly_production_qty": f"{monthly_production_qty:,}",
        "expected_incoming_qty": f"{expected_incoming_qty:,}",
        "current_total_inventory": f"{current_total_inventory:,}",
        "monthly_avg_sales_qty": f"{monthly_avg_sales_qty:,}"
    }

### 4. 사료 비율
    feed_data={
        "dry_feed": dry_feed,
        "wet_feed": wet_feed,
        "snack": snack
    }
    return sales_processed_data, inventory_processed_data, feed_data

### 3. home 페이지의 line data 내역
def get_sales_data(period):
    chart_data_map = {
        "1주일": [ 
            ("4/1", 20, 15), ("4/2", 40, 30), ("4/3", 20, 18), 
            ("4/4", 80, 65), ("4/5", 50, 38), ("4/6", 60, 52), ("4/7", 20, 16)
        ],
        "1개월": [ 
            ("1월", 20, 18), ("2월", 40, 32), ("3월", 20, 15), 
            ("4월", 80, 68), ("5월", 50, 42), ("6월", 70, 58), ("7월", 20, 17)
        ],
        "1년": [ 
            ("2021", 20, 18), ("2023", 40, 35), ("2024", 20, 16), 
            ("2025", 80, 70), ("2026", 50, 44)
        ],
    }
    # 요청한 기간(period)의 데이터를 꺼내주고, 없으면 빈 리스트 반환
    return chart_data_map.get(period, [])

### 4. 생산달성률/불량률 line chart 데이터 - 지금 연결되어 있음
def get_production_defect_rate():
    production_defect_rate = {
        "production_rate": [0.20, 0.20, 0.70, 0.20, 0.20, 0.20, 0.20],
        "defect_rate": [0.20, 0.20, 0.20, 0.20, 0.60, 0.20, 0.20]
    }
    return production_defect_rate