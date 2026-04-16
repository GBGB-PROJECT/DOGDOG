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
    
    raw_monthly_goal = 3500000
    raw_weekly_goal = 750000

    # [PROCESSING] View가 바로 출력할 수 있게 가공
    processed_data = {
        # 매출 하이라이트 (hd용)
        "total_sale": f"{raw_total_sales:,}",
        "last_year_growth": f"{raw_yoy_growth}",
        "total_sale_value": f"{raw_sales_qty:,}",
        "growth_goal": f"{raw_yearly_rate * 100}",

        # 목표 달성률 및 차트용 (hd용)
        "month_rate": raw_monthly_rate, # 차트용은 숫자로 전달 (0.85)
        "month_rate_text": f"{raw_monthly_rate * 100}", # 텍스트용 (85.0)
        "month_goal": f"{raw_monthly_goal // 10000:,}", # 만원 단위 절삭
        
        "week_rate": raw_weekly_rate,
        "week_rate_text": f"{raw_weekly_rate * 100}",
        "week_goal": f"{raw_weekly_goal // 10000:,}",
    }
    return processed_data

