"""erp_home_view의 각 데이터 저장소"""
home_view_data = {
  "total_sale": "50,000,000",
  "growth_goal": "50",
  "last_year_growth": "50",
  "total_sale_value": "75,000",
  "month_rate": 55,
  "month_goal":"150",
  "week_rate":45,
  "week_goal":"35"
}
## home_view_data
  # total_sale : 총 매출
  # growth_goal: 연간 목표 대비 달성
  # last_year_growth: 지난 해 대비 성장
  # total_sale_value: 총 판매량 수
  # month_rate: 월 판매성과(int),
  # month_goal: 월 목표,
  # week_rate: 주 판매성과(int),
  # week_goal: 주 목표

"""생산 재고 하이라이트 저장소"""
sale_inventory_data = {
  "monthly_production":"30,000",
  "incoming_planned":"21,000",
  "yoy_growth":"35",
  "total_sales_count": "3,845"
}
## sale_inventory_data
  # monthly_production : 이번 달 생산량
  # incoming_planned   : 입고 예정 물량
  # yoy_growth         : 전년 대비 성장률 (%)
  # total_sales_count  : 총 판매량 수 (누적)