from urllib.parse import quote
from api_client import ApiClient, BASE_URL

def proxy_image_url(url):
    if not url:
        return "test_product_4.jpg"

    image_url = str(url).strip()

    if image_url.startswith("http://") or image_url.startswith("https://"):
        return f"{BASE_URL}/images/proxy?url={quote(image_url, safe='')}"

    return image_url

def parse_pdi_urls(pdi):
    if not pdi:
        return []

    if isinstance(pdi, list):
        return [str(url).strip() for url in pdi if str(url).strip()]

    text = str(pdi).strip()

    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]

    urls = []
    for item in text.split(","):
        url = item.strip().strip("'").strip('"')
        if url:
            urls.append(url)

    return urls

# 상품 목록 조회 ------------------------------------------------------------------------
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

# 추천사료 조회 -----------------------------------------------------------------------
async def get_recommended_foods(page, pet_id: int):
    api = ApiClient(page)

    response = await api.get(f"/pets/{pet_id}/recommended-foods")

    if response.status_code != 200:
        print("추천사료 조회 실패:", response.text)
        return {}

    result = response.json()

    if result.get("success") is False:
        print("추천사료 조회 실패:", result.get("message"))
        return {}

    foods = result.get("data", [])

    food_dict = {}

    for item in foods:
        product_id = item.get("product_id")

        food_dict[product_id] = {
            "thumbnail": proxy_image_url(item.get("thumbnail")) or "test_product_4.jpg",
            "brand": item.get("brand") or "",
            "product_name": item.get("product_name") or "",
            "sales_price": item.get("retail_price") or 0,
        }

    return food_dict

# 상품 상세 조회 -----------------------------------------------------------------------
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
        pdi_urls = parse_pdi_urls(data.get("pdi"))
        data["pdi_images"] = [proxy_image_url(url) for url in pdi_urls]
    
    print(data["pdi_images"])

    return data

async def get_feeding_guide(page, pet_id: int):
    api = ApiClient(page)
    response = await api.get(f"/calc_feeding/{pet_id}/guide")
    if response.status_code != 200:
        return None
    result = response.json()
    if result.get("success") is False:
        return None
    return result.get("data")