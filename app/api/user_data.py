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

    pet_log = {
        # pet_log_numeric_id : {category, log_status, log_date}
        33:{"category":"급여량",
            "log_status":"77",
            "log_date":"2026-02-09 13:41:30.000"},
        66:{"category":"음수량",
            "log_status":"13",
            "log_date":"2026-02-09 15:41:30.000"},
        74:{"category":"급여량",
            "log_status":"111",
            "log_date":"2026-02-09 16:41:30.000"},
        88:{"category":"산책",
            "log_status":"30",
            "log_date":"2026-02-09 18:41:30.000"},
        131:{"category":"급여량",
            "log_status":"77",
            "log_date":"2026-02-10 13:41:30.000"},
        151:{"category":"음수량",
            "log_status":"13",
            "log_date":"2026-02-10 15:41:30.000"},
        166:{"category":"급여량",
            "log_status":"111",
            "log_date":"2026-02-10 16:41:30.000"},
        181:{"category":"산책",
            "log_status":"30",
            "log_date":"2026-02-10 18:41:30.000"},
        222:{"category":"급여량",
            "log_status":"77",
            "log_date":"2026-02-11 13:41:30.000"},
        262:{"category":"음수량",
            "log_status":"13",
            "log_date":"2026-02-12 15:41:30.000"},
        288:{"category":"급여량",
            "log_status":"111",
            "log_date":"2026-02-12 16:41:30.000"},
        292:{"category":"산책",
            "log_status":"30",
            "log_date":"2026-02-13 18:41:30.000"},
        333:{"category":"급여량",
            "log_status":"77",
            "log_date":"2026-02-14 13:41:30.000"},
        341:{"category":"음수량",
            "log_status":"13",
            "log_date":"2026-02-14 15:41:30.000"},
        351:{"category":"급여량",
            "log_status":"111",
            "log_date":"2026-02-15 16:41:30.000"},
        352:{"category":"산책",
            "log_status":"30",
            "log_date":"2026-02-15 18:41:30.000"},
        474:{"category":"음수량",
            "log_status":"13",
            "log_date":"2026-04-24 15:41:30.000"},
        484:{"category":"급여량",
            "log_status":"111",
            "log_date":"2026-04-24 16:41:30.000"},
        498:{"category":"산책",
            "log_status":"30",
            "log_date":"2026-04-24 18:41:30.000"},
    }