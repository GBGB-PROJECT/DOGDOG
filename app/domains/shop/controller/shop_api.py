from api_client import ApiClient

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

        product_dict[product_id] = {
            "thumbnail": item.get("thumbnail", "test_product_4.jpg"),
            "product_name": item.get("product_name", ""),
            "sales_price": item.get("retail_price", 0),
            "product_id": item.get("product_id"),
            "product_detail_id": item.get("product_detail_id"),
        }

    return product_dict


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

    return result.get("data")