import httpx

BASE_URL = "http://127.0.0.1:8000"
_CLIENT = httpx.Client(base_url=BASE_URL, timeout=5.0)

# 1 ======= Backend API와 연결


class HomeViewMain:

  @staticmethod
  # sale_dashboard api와 연결하기
  def sale_dashboard():
    """ 판매가/판매량을 확인 가능한 데이터 보드 조회"""
    url = f"{BASE_URL}/erp/home/sale_dashboard"

    try:
      ## 1. Get 요청 전송
      response = _CLIENT.get("/erp/home/sale_dashboard")

      ## 2. 성공 시 (200 ok)
      if response.status_code == 200:
        data = response.json() # 성공 시 응답값을 json으로 출력
        return data.get("data")# 형태가 키 내부에 data 박스 구조임

      ## 3. 실패 시(서버 메시지 출력)
      try:
        errr_info = response.json()
        message = errr_info.get("detail", "데이터 불러오기 실패.")
      except Exception:
        message = f"서버코드 오류: (코드: {response.status_code})"
    
    ## 공통예외처리
    except httpx.ConnectError: raise Exception("서버 연결 실패")
    except httpx.TimeoutException: raise Exception("응답 시간 초과")
    except Exception as e: raise Exception(f"기타 오류 발생: {e}")
  
  @staticmethod
  def inventory_dashboard():
    """입고량, 성장률 확인이 가능한 대시보드"""
    url = f"{BASE_URL}/erp/home/inventory_dashboard"

    try:
      # 1. 요청전송
      response = _CLIENT.get("/erp/home/inventory_dashboard")

      # 2. 성공 시
      if response.status_code == 200:
        data = response.json()
        return data.get('data') # 1회 더 꺼내는 작업이 필요함(사료는 더 확인 필요 또까야 하니까)
      try:
        errr_info = response.json()
        message = errr_info.get("detail", "데이터 불러오기 실패.")
      except Exception:
        message = f"서버코드 오류: (코드: {response.status_code})"
    ## 공통예외처리
    except httpx.ConnectError: raise Exception("서버 연결 실패")
    except httpx.TimeoutException: raise Exception("응답 시간 초과")
    except Exception as e: raise Exception(f"기타 오류 발생: {e}")
  
  @staticmethod
  def sale_chart(period: str = "1개월"):
    """상단 매출, 판매량 차트데이터"""
    url = f"{BASE_URL}/erp/home/chart_dashboard_sale?period={period}"

    try:
      ## 1. Get 요청 전송
      response = _CLIENT.get("/erp/home/chart_dashboard_sale", params={"period": period})

      ## 2. 성공 시 (200 ok)
      if response.status_code == 200:
        data = response.json() # 성공 시 응답값을 json으로 출력
        return data.get("data")# 형태가 키 내부에 data 박스 구조임

      ## 3. 실패 시(서버 메시지 출력)
      try:
        errr_info = response.json()
        message = errr_info.get("detail", "데이터 불러오기 실패.")
      except Exception:
        message = f"서버코드 오류: (코드: {response.status_code})"
    
    ## 공통예외처리
    except httpx.ConnectError: raise Exception("서버 연결 실패")
    except httpx.TimeoutException: raise Exception("응답 시간 초과")
    except Exception as e: raise Exception(f"기타 오류 발생: {e}")

  @staticmethod
  def prduct_defect_chart(period: str = "1개월"):
    """생산 달성률 및 불량률 차트 데이터 조회 (작년 동월 + 최근 5개월)"""
    url = f"{BASE_URL}/erp/home/chart_dashboard_production"

    try:
      ## 1. Get 요청 전송
      response = _CLIENT.get("/erp/home/chart_dashboard_production")

      ## 2. 성공 시 (200 OK)
      if response.status_code == 200:
        data = response.json() 
        return data.get("data") # {"production_rate": [...], "defect_rate": [...]} 반환

      ## 3. 실패 시 (서버 메시지 출력)
      try:
        error_info = response.json()
        message = error_info.get("msg", "데이터 불러오기 실패.")
      except Exception:
        message = f"서버코드 오류: (코드: {response.status_code})"
      
      raise Exception(message)

    ## 공통 예외 처리
    except httpx.ConnectError: raise Exception("서버 연결 실패")
    except httpx.TimeoutException: raise Exception("응답 시간 초과")
    except Exception as e: raise Exception(f"기타 오류 발생: {e}")
