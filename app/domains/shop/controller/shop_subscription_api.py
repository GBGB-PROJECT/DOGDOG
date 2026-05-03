from urllib.parse import quote
from api_client import ApiClient, BASE_URL

# 구독 내역 확인 ----------------------------------------------------
async def get_subscription_status(page):
    api = ApiClient(page)

    response = await api.get("/subscriptions")

    if response.status_code != 200:
        print("구독 조회 실패:", response.text)
        return None

    result = response.json()

    if result.get("success") is False:
        print("구독 조회 실패:", result.get("message"))
        return None

    return result.get("data")


# 구독 생성 ---------------------------------------------------------
async def create_subscription(page, data):
    api = ApiClient(page)
    response = await api.post("/subscriptions", data=data)

    if response.status_code not in (200, 201):
        print("구독 생성 실패:", response.text)
        return None

    result = response.json()

    if result.get("success") is False:
        print("구독 생성 실패:", result.get("message"))
        return None

    return result.get("data")
