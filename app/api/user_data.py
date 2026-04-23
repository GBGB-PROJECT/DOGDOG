class User:
    pet_list = {
        # pet_id : {nickname, birth_day, sex},
        1:{"nickname":"바둑이테", "birth_day":"2023-01-01", "sex":"1", "profile_image":None},
        2:{"nickname":"누렁", "birth_day":"2022-01-01", "sex":"2", "profile_image":"dog.jpeg"}
    }

    customer_food_detail = {
        # customer_food_id : product_detail
        4: {"thumbnail": "test_product_4.jpg",                  # 상품 이미지
            "product_id":4,                                     # 상품 id
            "total_weight": 5800,                               # 상품 총 무게 g
            "product_detail_id": 2,                             # 상품 상세 id
            "brand": "더리얼 독",                                 # 브랜드
            "product_name": "그레인프리 오븐베이크드 닭고기 시니어",  # 상품명
            "feeding_start": "2026-04-10",                      # 급여 시작일
            "left_food_count": 24,                              # 남은 급여 횟수(현재 날짜로 환산 / 1회 : 1일)
            "left_intake": 800},                                # 남은 사료 무게 g
        14: {"thumbnail": "test_product_14.jpg",
            "product_id":14,
            "total_weight": 1600,
            "product_detail_id": 5,
            "brand": "더리얼 독",
            "product_name": "그레인프리 오븐베이크드 돼지 어덜트",
            "feeding_start": "2026-04-13",
            "left_food_count": 12,
            "left_intake": 600},
        44: {"thumbnail": "test_product_44.jpg",
            "product_id":44,
            "total_weight": 1600,
            "product_detail_id": 14,
            "brand": "더리얼 독",
            "product_name": "그레인프리 크런치 소고기 시니어",
            "feeding_start": "2026-03-26",
            "left_food_count": 17,
            "left_intake": 160},
        70: {"thumbnail": "test_product_70.jpg",
            "product_id":70,
            "total_weight": 50,
            "product_detail_id": 24,
            "brand": "더리얼 독",
            "product_name": "로우 돼지고기 어덜트",
            "feeding_start": "2026-03-23",
            "left_food_count": 1,
            "left_intake": 25},
    }