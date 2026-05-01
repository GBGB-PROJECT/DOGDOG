from urllib.parse import quote
from api_client import ApiClient, BASE_URL

def proxy_image_url(url):
    if not url:
        return "test_product_4.jpg"

    image_url = str(url).strip()

    if image_url.startswith("http://") or image_url.startswith("https://"):
        return f"{BASE_URL}/images/proxy?url={quote(image_url, safe='')}"

    return image_url


# def normalize_thumbnail(url):
#     if not url:
#         return "test_product_4.jpg"

#     url = str(url).strip()

#     if "photo3.enuri.info/data/images/service/big" in url:
#         return url.replace(
#             "https://photo3.enuri.info/data/images/service/big",
#             "https://image.enuri.info/webimage_300"
#         )

#     return url

# def normalize_thumbnail(url):
#     try:
#         # 이미 성공 패턴이면 그대로
#         if "webimage_300" in url:
#             return url if url.endswith(".jpg") else url + ".jpg"

#         # photo3 계열 처리
#         if "photo3.enuri.info" in url:
#             if "service/" in url:
#                 # service/ 이후 경로 추출
#                 path = url.split("service/")[1]

#                 # big / dnw/master 제거
#                 path = path.replace("big/", "")
#                 path = path.replace("dnw/master/", "")

#                 # 새 URL 생성
#                 new_url = f"https://image.enuri.info/webimage_300/{path}"

#                 # 확장자 보정
#                 if not new_url.endswith(".jpg"):
#                     new_url += ".jpg"

#                 return new_url

#         # image인데 webimage_300 없는 경우
#         if "image.enuri.info" in url and "webimage_300" not in url:
#             parts = url.split("/")
#             new_url = "https://image.enuri.info/webimage_300/" + "/".join(parts[-2:])
#             if not new_url.endswith(".jpg"):
#                 new_url += ".jpg"
#             return new_url

#         # 마지막 fallback
#         return url

#     except Exception:
#         return url

'''
상품 목록 조회 API
- keyword: 상품명, 브랜드명, 기능, 타입, 단백질 관련 검색
- sort: price_desc, price_asc, weight_desc, weight_asc

data = [
    {
        "product_id": row.product_id,
        "product_detail_id": row.product_detail_id,
        "thumbnail": row.thumbnail,
        "product_name": f"{row.product_name} {row.weight}g X{row.quantity}",
        "brand": row.brand,
        "type": row.type,
        "function": row.function,
        "quantity":row.quantity,
        "weight": float(row.weight) if row.weight is not None else None,
        "is_sample": row.is_sample,
        "retail_price": float(row.retail_price) if row.retail_price is not None else 0,
    }
]
'''
'''
{
"thumbnail":"test_product_4.jpg",
"brand":"더리얼 독",
"product_name":"3",
"sales_price":"999799"
},
'''

async def get_shop_product_list(page, sort=None, keyword=None):
    api = ApiClient(page)

    params = {}
    if sort:
        params["sort"] = sort
    if keyword:
        params["keyword"] = keyword

    response = await api.get("/products", params=params)

    if response.status_code != 200:
        print("상품 목록 조회 실패:", response.text)
        return {}

    result = response.json()

    if result.get("success") is False:
        print("상품 목록 조회 실패:", result.get("message"))
        return {}

    products = result.get("data", [])

    product_dict = {}

    for item in products:
        product_id = item.get("product_id")

        # thumbnail = normalize_thumbnail(item.get("thumbnail"))
        # thumbnail = item.get("thumbnail")
        thumbnail = proxy_image_url(item.get("thumbnail"))

        product_dict[product_id] = {
            "thumbnail": thumbnail,
            "brand": item.get("brand") or "",
            "product_name": item.get("product_name") or "",
            "sales_price": item.get("retail_price") or 0,
        }

    return product_dict

'''
data = {
            "product_id": product.product_id,
            "product_detail_id": product_detail.product_detail_id,

            "brand": product_detail.brand,
            "product_name": product_name,

            "type": product_detail.type,
            "life": product_detail.life,
            "function": product_detail.function,
            "description": product_detail.description,
            "calories": float(product_detail.calories) if product_detail.calories is not None else None,
            
            "thumbnail": product_detail.thumbnail,
            "pdi": product_detail.pdi,
            
            "quantity": product.quantity,
            "weight": product.weight,
            "retail_price": float(product.retail_price) if product.retail_price is not None else None,
            "is_sample": product.is_sample
        }
'''
async def get_shop_product_detail(page, product_id: int):
    api = ApiClient(page)

    response = await api.get(f"/products/{product_id}")

    if response.status_code != 200:
        print("상품 상세 조회 실패:", response.text)
        return None

    result = response.json()

    if result.get("success") is False:
        print("상품 상세 조회 실패:", result.get("message"))
        return None
    
    data = result.get("data")
    print(data)
    
    if data:
        data["thumbnail"] =  proxy_image_url(data.get("thumbnail"))
        data["pdi"] = proxy_image_url(data.get("pdi"))
    
    print(data["pdi"])

    return data