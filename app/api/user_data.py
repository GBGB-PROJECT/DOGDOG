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
    "500": {
        "category": "급여량",
        "log_status": "77",
        "log_date": "2026-03-01 12:54:50.000"
    },
    "513": {
        "category": "음수량",
        "log_status": "15",
        "log_date": "2026-03-01 15:13:29.000"
    },
    "520": {
        "category": "급여량",
        "log_status": "115",
        "log_date": "2026-03-01 17:36:28.000"
    },
    "534": {
        "category": "산책",
        "log_status": "39",
        "log_date": "2026-03-01 18:36:46.000"
    },
    "544": {
        "category": "급여량",
        "log_status": "80",
        "log_date": "2026-03-02 12:27:35.000"
    },
    "552": {
        "category": "음수량",
        "log_status": "19",
        "log_date": "2026-03-02 16:03:59.000"
    },
    "560": {
        "category": "급여량",
        "log_status": "112",
        "log_date": "2026-03-02 17:10:17.000"
    },
    "570": {
        "category": "산책",
        "log_status": "40",
        "log_date": "2026-03-02 18:13:45.000"
    },
    "589": {
        "category": "급여량",
        "log_status": "75",
        "log_date": "2026-03-03 13:47:15.000"
    },
    "598": {
        "category": "음수량",
        "log_status": "18",
        "log_date": "2026-03-03 16:29:14.000"
    },
    "608": {
        "category": "급여량",
        "log_status": "109",
        "log_date": "2026-03-03 17:56:57.000"
    },
    "623": {
        "category": "산책",
        "log_status": "45",
        "log_date": "2026-03-03 19:47:13.000"
    },
    "640": {
        "category": "급여량",
        "log_status": "72",
        "log_date": "2026-03-04 13:44:24.000"
    },
    "651": {
        "category": "음수량",
        "log_status": "19",
        "log_date": "2026-03-04 16:02:46.000"
    },
    "657": {
        "category": "급여량",
        "log_status": "106",
        "log_date": "2026-03-04 16:05:36.000"
    },
    "671": {
        "category": "산책",
        "log_status": "33",
        "log_date": "2026-03-04 19:46:15.000"
    },
    "685": {
        "category": "급여량",
        "log_status": "76",
        "log_date": "2026-03-05 13:04:35.000"
    },
    "694": {
        "category": "음수량",
        "log_status": "19",
        "log_date": "2026-03-05 15:59:38.000"
    },
    "700": {
        "category": "급여량",
        "log_status": "109",
        "log_date": "2026-03-05 16:05:35.000"
    },
    "707": {
        "category": "산책",
        "log_status": "34",
        "log_date": "2026-03-05 18:58:07.000"
    },
    "727": {
        "category": "급여량",
        "log_status": "78",
        "log_date": "2026-03-06 12:18:30.000"
    },
    "738": {
        "category": "음수량",
        "log_status": "21",
        "log_date": "2026-03-06 16:11:26.000"
    },
    "743": {
        "category": "급여량",
        "log_status": "106",
        "log_date": "2026-03-06 16:32:40.000"
    },
    "757": {
        "category": "산책",
        "log_status": "34",
        "log_date": "2026-03-06 18:18:40.000"
    },
    "773": {
        "category": "급여량",
        "log_status": "76",
        "log_date": "2026-03-07 12:26:35.000"
    },
    "782": {
        "category": "음수량",
        "log_status": "15",
        "log_date": "2026-03-07 15:40:51.000"
    },
    "791": {
        "category": "급여량",
        "log_status": "113",
        "log_date": "2026-03-07 16:48:51.000"
    },
    "802": {
        "category": "산책",
        "log_status": "43",
        "log_date": "2026-03-07 20:01:16.000"
    },
    "821": {
        "category": "급여량",
        "log_status": "73",
        "log_date": "2026-03-08 13:16:29.000"
    },
    "832": {
        "category": "음수량",
        "log_status": "21",
        "log_date": "2026-03-08 15:20:47.000"
    },
    "844": {
        "category": "급여량",
        "log_status": "107",
        "log_date": "2026-03-08 16:17:43.000"
    },
    "859": {
        "category": "산책",
        "log_status": "45",
        "log_date": "2026-03-08 20:07:54.000"
    },
    "877": {
        "category": "급여량",
        "log_status": "73",
        "log_date": "2026-03-09 13:42:56.000"
    },
    "884": {
        "category": "음수량",
        "log_status": "18",
        "log_date": "2026-03-09 16:44:19.000"
    },
    "889": {
        "category": "급여량",
        "log_status": "113",
        "log_date": "2026-03-09 17:46:16.000"
    },
    "899": {
        "category": "산책",
        "log_status": "43",
        "log_date": "2026-03-09 19:29:27.000"
    },
    "916": {
        "category": "급여량",
        "log_status": "72",
        "log_date": "2026-03-10 13:10:01.000"
    },
    "925": {
        "category": "음수량",
        "log_status": "13",
        "log_date": "2026-03-10 16:08:25.000"
    },
    "931": {
        "category": "급여량",
        "log_status": "115",
        "log_date": "2026-03-10 17:50:00.000"
    },
    "944": {
        "category": "산책",
        "log_status": "41",
        "log_date": "2026-03-10 19:34:39.000"
    },
    "954": {
        "category": "급여량",
        "log_status": "77",
        "log_date": "2026-03-11 13:57:11.000"
    },
    "966": {
        "category": "음수량",
        "log_status": "23",
        "log_date": "2026-03-11 16:29:21.000"
    },
    "974": {
        "category": "급여량",
        "log_status": "106",
        "log_date": "2026-03-11 16:19:22.000"
    },
    "980": {
        "category": "산책",
        "log_status": "40",
        "log_date": "2026-03-11 18:48:57.000"
    },
    "992": {
        "category": "급여량",
        "log_status": "80",
        "log_date": "2026-03-12 13:53:16.000"
    },
    "1001": {
        "category": "음수량",
        "log_status": "14",
        "log_date": "2026-03-12 16:47:51.000"
    },
    "1007": {
        "category": "급여량",
        "log_status": "115",
        "log_date": "2026-03-12 17:45:03.000"
    },
    "1012": {
        "category": "산책",
        "log_status": "37",
        "log_date": "2026-03-12 18:20:24.000"
    },
    "1031": {
        "category": "급여량",
        "log_status": "75",
        "log_date": "2026-03-13 13:04:25.000"
    },
    "1039": {
        "category": "음수량",
        "log_status": "17",
        "log_date": "2026-03-13 16:43:25.000"
    },
    "1048": {
        "category": "급여량",
        "log_status": "110",
        "log_date": "2026-03-13 17:10:10.000"
    },
    "1057": {
        "category": "산책",
        "log_status": "44",
        "log_date": "2026-03-13 18:23:46.000"
    },
    "1067": {
        "category": "급여량",
        "log_status": "81",
        "log_date": "2026-03-14 12:27:44.000"
    },
    "1075": {
        "category": "음수량",
        "log_status": "14",
        "log_date": "2026-03-14 15:52:13.000"
    },
    "1084": {
        "category": "급여량",
        "log_status": "115",
        "log_date": "2026-03-14 16:41:02.000"
    },
    "1091": {
        "category": "산책",
        "log_status": "33",
        "log_date": "2026-03-14 19:24:52.000"
    },
    "1103": {
        "category": "급여량",
        "log_status": "81",
        "log_date": "2026-03-15 12:42:43.000"
    },
    "1108": {
        "category": "음수량",
        "log_status": "14",
        "log_date": "2026-03-15 16:50:31.000"
    },
    "1123": {
        "category": "급여량",
        "log_status": "115",
        "log_date": "2026-03-15 17:12:46.000"
    },
    "1133": {
        "category": "산책",
        "log_status": "44",
        "log_date": "2026-03-15 18:59:38.000"
    },
    "1151": {
        "category": "급여량",
        "log_status": "72",
        "log_date": "2026-03-16 12:25:46.000"
    },
    "1159": {
        "category": "음수량",
        "log_status": "23",
        "log_date": "2026-03-16 16:28:58.000"
    },
    "1167": {
        "category": "급여량",
        "log_status": "107",
        "log_date": "2026-03-16 16:07:29.000"
    },
    "1178": {
        "category": "산책",
        "log_status": "42",
        "log_date": "2026-03-16 19:25:29.000"
    },
    "1194": {
        "category": "급여량",
        "log_status": "82",
        "log_date": "2026-03-17 13:40:39.000"
    },
    "1204": {
        "category": "음수량",
        "log_status": "15",
        "log_date": "2026-03-17 15:17:50.000"
    },
    "1215": {
        "category": "급여량",
        "log_status": "111",
        "log_date": "2026-03-17 16:57:20.000"
    },
    "1223": {
        "category": "산책",
        "log_status": "36",
        "log_date": "2026-03-17 19:07:59.000"
    },
    "1234": {
        "category": "급여량",
        "log_status": "78",
        "log_date": "2026-03-18 13:06:35.000"
    },
    "1240": {
        "category": "음수량",
        "log_status": "19",
        "log_date": "2026-03-18 15:40:17.000"
    },
    "1248": {
        "category": "급여량",
        "log_status": "114",
        "log_date": "2026-03-18 17:21:19.000"
    },
    "1263": {
        "category": "산책",
        "log_status": "34",
        "log_date": "2026-03-18 18:00:23.000"
    },
    "1273": {
        "category": "급여량",
        "log_status": "72",
        "log_date": "2026-03-19 12:21:46.000"
    },
    "1288": {
        "category": "음수량",
        "log_status": "23",
        "log_date": "2026-03-19 15:01:36.000"
    },
    "1301": {
        "category": "급여량",
        "log_status": "113",
        "log_date": "2026-03-19 16:46:15.000"
    },
    "1316": {
        "category": "산책",
        "log_status": "34",
        "log_date": "2026-03-19 20:26:34.000"
    },
    "1333": {
        "category": "급여량",
        "log_status": "77",
        "log_date": "2026-03-20 13:28:01.000"
    },
    "1340": {
        "category": "음수량",
        "log_status": "16",
        "log_date": "2026-03-20 15:12:14.000"
    },
    "1345": {
        "category": "급여량",
        "log_status": "114",
        "log_date": "2026-03-20 16:12:05.000"
    },
    "1358": {
        "category": "산책",
        "log_status": "41",
        "log_date": "2026-03-20 20:08:38.000"
    },
    "1368": {
        "category": "급여량",
        "log_status": "74",
        "log_date": "2026-03-21 12:06:34.000"
    },
    "1374": {
        "category": "음수량",
        "log_status": "17",
        "log_date": "2026-03-21 15:05:33.000"
    },
    "1381": {
        "category": "급여량",
        "log_status": "111",
        "log_date": "2026-03-21 16:14:55.000"
    },
    "1392": {
        "category": "산책",
        "log_status": "37",
        "log_date": "2026-03-21 20:51:56.000"
    },
    "1412": {
        "category": "급여량",
        "log_status": "77",
        "log_date": "2026-03-22 13:10:13.000"
    },
    "1425": {
        "category": "음수량",
        "log_status": "21",
        "log_date": "2026-03-22 16:19:30.000"
    },
    "1430": {
        "category": "급여량",
        "log_status": "115",
        "log_date": "2026-03-22 17:57:14.000"
    },
    "1440": {
        "category": "산책",
        "log_status": "34",
        "log_date": "2026-03-22 19:30:11.000"
    },
    "1454": {
        "category": "급여량",
        "log_status": "76",
        "log_date": "2026-03-23 13:01:00.000"
    },
    "1459": {
        "category": "음수량",
        "log_status": "20",
        "log_date": "2026-03-23 16:01:43.000"
    },
    "1472": {
        "category": "급여량",
        "log_status": "110",
        "log_date": "2026-03-23 17:31:53.000"
    },
    "1478": {
        "category": "산책",
        "log_status": "38",
        "log_date": "2026-03-23 20:34:39.000"
    },
    "1489": {
        "category": "급여량",
        "log_status": "80",
        "log_date": "2026-03-24 13:49:10.000"
    },
    "1494": {
        "category": "음수량",
        "log_status": "17",
        "log_date": "2026-03-24 16:33:52.000"
    },
    "1504": {
        "category": "급여량",
        "log_status": "113",
        "log_date": "2026-03-24 16:24:50.000"
    },
    "1514": {
        "category": "산책",
        "log_status": "42",
        "log_date": "2026-03-24 19:28:16.000"
    },
    "1534": {
        "category": "급여량",
        "log_status": "76",
        "log_date": "2026-03-25 13:32:14.000"
    },
    "1543": {
        "category": "음수량",
        "log_status": "16",
        "log_date": "2026-03-25 15:21:18.000"
    },
    "1553": {
        "category": "급여량",
        "log_status": "105",
        "log_date": "2026-03-25 17:22:20.000"
    },
    "1562": {
        "category": "산책",
        "log_status": "47",
        "log_date": "2026-03-25 19:09:24.000"
    },
    "1577": {
        "category": "급여량",
        "log_status": "79",
        "log_date": "2026-03-26 12:22:52.000"
    },
    "1589": {
        "category": "음수량",
        "log_status": "15",
        "log_date": "2026-03-26 16:16:43.000"
    },
    "1603": {
        "category": "급여량",
        "log_status": "111",
        "log_date": "2026-03-26 16:49:34.000"
    },
    "1609": {
        "category": "산책",
        "log_status": "35",
        "log_date": "2026-03-26 19:23:46.000"
    },
    "1620": {
        "category": "급여량",
        "log_status": "78",
        "log_date": "2026-03-27 12:00:16.000"
    },
    "1629": {
        "category": "음수량",
        "log_status": "18",
        "log_date": "2026-03-27 16:40:50.000"
    },
    "1644": {
        "category": "급여량",
        "log_status": "107",
        "log_date": "2026-03-27 16:11:52.000"
    },
    "1653": {
        "category": "산책",
        "log_status": "37",
        "log_date": "2026-03-27 20:01:22.000"
    },
    "1671": {
        "category": "급여량",
        "log_status": "75",
        "log_date": "2026-03-28 13:56:11.000"
    },
    "1680": {
        "category": "음수량",
        "log_status": "18",
        "log_date": "2026-03-28 16:50:20.000"
    },
    "1687": {
        "category": "급여량",
        "log_status": "113",
        "log_date": "2026-03-28 17:40:29.000"
    },
    "1701": {
        "category": "산책",
        "log_status": "46",
        "log_date": "2026-03-28 19:49:42.000"
    },
    "1721": {
        "category": "급여량",
        "log_status": "76",
        "log_date": "2026-03-29 12:23:07.000"
    },
    "1736": {
        "category": "음수량",
        "log_status": "22",
        "log_date": "2026-03-29 15:42:41.000"
    },
    "1749": {
        "category": "급여량",
        "log_status": "111",
        "log_date": "2026-03-29 17:28:26.000"
    },
    "1755": {
        "category": "산책",
        "log_status": "38",
        "log_date": "2026-03-29 19:22:35.000"
    },
    "1768": {
        "category": "급여량",
        "log_status": "78",
        "log_date": "2026-03-30 12:12:12.000"
    },
    "1776": {
        "category": "음수량",
        "log_status": "25",
        "log_date": "2026-03-30 15:26:54.000"
    },
    "1782": {
        "category": "급여량",
        "log_status": "114",
        "log_date": "2026-03-30 16:29:26.000"
    },
    "1789": {
        "category": "산책",
        "log_status": "43",
        "log_date": "2026-03-30 18:47:02.000"
    },
    "1802": {
        "category": "급여량",
        "log_status": "72",
        "log_date": "2026-03-31 13:07:59.000"
    },
    "1816": {
        "category": "음수량",
        "log_status": "16",
        "log_date": "2026-03-31 16:30:23.000"
    },
    "1824": {
        "category": "급여량",
        "log_status": "112",
        "log_date": "2026-03-31 16:04:47.000"
    },
    "1837": {
        "category": "산책",
        "log_status": "50",
        "log_date": "2026-03-31 19:31:44.000"
    },
    "1847": {
        "category": "급여량",
        "log_status": "81",
        "log_date": "2026-04-01 13:48:00.000"
    },
    "1853": {
        "category": "음수량",
        "log_status": "26",
        "log_date": "2026-04-01 16:27:30.000"
    },
    "1863": {
        "category": "급여량",
        "log_status": "106",
        "log_date": "2026-04-01 16:25:02.000"
    },
    "1874": {
        "category": "산책",
        "log_status": "44",
        "log_date": "2026-04-01 18:17:24.000"
    },
    "1885": {
        "category": "급여량",
        "log_status": "78",
        "log_date": "2026-04-02 13:32:04.000"
    },
    "1894": {
        "category": "음수량",
        "log_status": "24",
        "log_date": "2026-04-02 15:53:47.000"
    },
    "1905": {
        "category": "급여량",
        "log_status": "111",
        "log_date": "2026-04-02 17:26:15.000"
    },
    "1911": {
        "category": "산책",
        "log_status": "49",
        "log_date": "2026-04-02 19:14:24.000"
    },
    "1928": {
        "category": "급여량",
        "log_status": "74",
        "log_date": "2026-04-03 13:39:37.000"
    },
    "1941": {
        "category": "음수량",
        "log_status": "20",
        "log_date": "2026-04-03 15:36:18.000"
    },
    "1949": {
        "category": "급여량",
        "log_status": "110",
        "log_date": "2026-04-03 16:29:58.000"
    },
    "1959": {
        "category": "산책",
        "log_status": "42",
        "log_date": "2026-04-03 19:42:57.000"
    },
    "1969": {
        "category": "급여량",
        "log_status": "77",
        "log_date": "2026-04-04 12:19:55.000"
    },
    "1976": {
        "category": "음수량",
        "log_status": "24",
        "log_date": "2026-04-04 15:47:14.000"
    },
    "1982": {
        "category": "급여량",
        "log_status": "111",
        "log_date": "2026-04-04 17:03:48.000"
    },
    "1987": {
        "category": "산책",
        "log_status": "36",
        "log_date": "2026-04-04 18:30:25.000"
    },
    "2002": {
        "category": "급여량",
        "log_status": "82",
        "log_date": "2026-04-05 13:57:32.000"
    },
    "2017": {
        "category": "음수량",
        "log_status": "22",
        "log_date": "2026-04-05 15:42:00.000"
    },
    "2031": {
        "category": "급여량",
        "log_status": "115",
        "log_date": "2026-04-05 16:46:45.000"
    },
    "2041": {
        "category": "산책",
        "log_status": "44",
        "log_date": "2026-04-05 20:12:37.000"
    },
    "2054": {
        "category": "급여량",
        "log_status": "79",
        "log_date": "2026-04-06 13:05:00.000"
    },
    "2064": {
        "category": "음수량",
        "log_status": "26",
        "log_date": "2026-04-06 15:24:28.000"
    },
    "2069": {
        "category": "급여량",
        "log_status": "105",
        "log_date": "2026-04-06 17:55:04.000"
    },
    "2078": {
        "category": "산책",
        "log_status": "45",
        "log_date": "2026-04-06 20:35:32.000"
    },
    "2088": {
        "category": "급여량",
        "log_status": "75",
        "log_date": "2026-04-07 13:39:08.000"
    },
    "2096": {
        "category": "음수량",
        "log_status": "17",
        "log_date": "2026-04-07 15:01:20.000"
    },
    "2110": {
        "category": "급여량",
        "log_status": "107",
        "log_date": "2026-04-07 16:37:47.000"
    },
    "2121": {
        "category": "산책",
        "log_status": "37",
        "log_date": "2026-04-07 18:21:26.000"
    },
    "2139": {
        "category": "급여량",
        "log_status": "73",
        "log_date": "2026-04-08 12:02:50.000"
    },
    "2151": {
        "category": "음수량",
        "log_status": "26",
        "log_date": "2026-04-08 16:39:34.000"
    },
    "2159": {
        "category": "급여량",
        "log_status": "113",
        "log_date": "2026-04-08 17:46:04.000"
    },
    "2166": {
        "category": "산책",
        "log_status": "50",
        "log_date": "2026-04-08 18:50:44.000"
    },
    "2176": {
        "category": "급여량",
        "log_status": "74",
        "log_date": "2026-04-09 13:50:00.000"
    },
    "2191": {
        "category": "음수량",
        "log_status": "18",
        "log_date": "2026-04-09 16:23:57.000"
    },
    "2204": {
        "category": "급여량",
        "log_status": "110",
        "log_date": "2026-04-09 17:39:42.000"
    },
    "2209": {
        "category": "산책",
        "log_status": "51",
        "log_date": "2026-04-09 19:04:51.000"
    },
    "2219": {
        "category": "급여량",
        "log_status": "79",
        "log_date": "2026-04-10 12:22:24.000"
    },
    "2230": {
        "category": "음수량",
        "log_status": "20",
        "log_date": "2026-04-10 16:57:52.000"
    },
    "2243": {
        "category": "급여량",
        "log_status": "110",
        "log_date": "2026-04-10 17:22:52.000"
    },
    "2255": {
        "category": "산책",
        "log_status": "41",
        "log_date": "2026-04-10 20:41:36.000"
    },
    "2265": {
        "category": "급여량",
        "log_status": "75",
        "log_date": "2026-04-11 13:51:50.000"
    },
    "2274": {
        "category": "음수량",
        "log_status": "18",
        "log_date": "2026-04-11 15:26:38.000"
    },
    "2281": {
        "category": "급여량",
        "log_status": "106",
        "log_date": "2026-04-11 16:28:34.000"
    },
    "2286": {
        "category": "산책",
        "log_status": "42",
        "log_date": "2026-04-11 19:09:06.000"
    },
    "2303": {
        "category": "급여량",
        "log_status": "79",
        "log_date": "2026-04-12 12:30:26.000"
    },
    "2315": {
        "category": "음수량",
        "log_status": "23",
        "log_date": "2026-04-12 15:56:37.000"
    },
    "2326": {
        "category": "급여량",
        "log_status": "106",
        "log_date": "2026-04-12 17:46:20.000"
    },
    "2334": {
        "category": "산책",
        "log_status": "42",
        "log_date": "2026-04-12 20:40:28.000"
    },
    "2350": {
        "category": "급여량",
        "log_status": "72",
        "log_date": "2026-04-13 12:24:36.000"
    },
    "2360": {
        "category": "음수량",
        "log_status": "21",
        "log_date": "2026-04-13 15:01:36.000"
    },
    "2373": {
        "category": "급여량",
        "log_status": "107",
        "log_date": "2026-04-13 16:32:04.000"
    },
    "2385": {
        "category": "산책",
        "log_status": "45",
        "log_date": "2026-04-13 18:40:36.000"
    },
    "2401": {
        "category": "급여량",
        "log_status": "80",
        "log_date": "2026-04-14 13:22:49.000"
    },
    "2406": {
        "category": "음수량",
        "log_status": "19",
        "log_date": "2026-04-14 16:54:06.000"
    },
    "2415": {
        "category": "급여량",
        "log_status": "113",
        "log_date": "2026-04-14 16:10:02.000"
    },
    "2426": {
        "category": "산책",
        "log_status": "45",
        "log_date": "2026-04-14 18:47:09.000"
    },
    "2437": {
        "category": "급여량",
        "log_status": "78",
        "log_date": "2026-04-15 12:32:05.000"
    },
    "2445": {
        "category": "음수량",
        "log_status": "17",
        "log_date": "2026-04-15 16:41:37.000"
    },
    "2457": {
        "category": "급여량",
        "log_status": "106",
        "log_date": "2026-04-15 16:18:10.000"
    },
    "2471": {
        "category": "산책",
        "log_status": "48",
        "log_date": "2026-04-15 19:10:18.000"
    },
    "2486": {
        "category": "급여량",
        "log_status": "75",
        "log_date": "2026-04-16 13:14:36.000"
    },
    "2493": {
        "category": "음수량",
        "log_status": "27",
        "log_date": "2026-04-16 15:18:00.000"
    },
    "2505": {
        "category": "급여량",
        "log_status": "108",
        "log_date": "2026-04-16 16:52:43.000"
    },
    "2519": {
        "category": "산책",
        "log_status": "39",
        "log_date": "2026-04-16 20:24:11.000"
    },
    "2538": {
        "category": "급여량",
        "log_status": "74",
        "log_date": "2026-04-17 12:21:03.000"
    },
    "2551": {
        "category": "음수량",
        "log_status": "19",
        "log_date": "2026-04-17 16:06:18.000"
    },
    "2557": {
        "category": "급여량",
        "log_status": "114",
        "log_date": "2026-04-17 16:04:27.000"
    },
    "2564": {
        "category": "산책",
        "log_status": "48",
        "log_date": "2026-04-17 20:24:23.000"
    },
    "2577": {
        "category": "급여량",
        "log_status": "81",
        "log_date": "2026-04-18 12:20:28.000"
    },
    "2588": {
        "category": "음수량",
        "log_status": "19",
        "log_date": "2026-04-18 15:16:33.000"
    },
    "2600": {
        "category": "급여량",
        "log_status": "106",
        "log_date": "2026-04-18 16:02:11.000"
    },
    "2608": {
        "category": "산책",
        "log_status": "50",
        "log_date": "2026-04-18 19:22:28.000"
    },
    "2619": {
        "category": "급여량",
        "log_status": "75",
        "log_date": "2026-04-19 13:24:35.000"
    },
    "2631": {
        "category": "음수량",
        "log_status": "25",
        "log_date": "2026-04-19 16:59:27.000"
    },
    "2640": {
        "category": "급여량",
        "log_status": "110",
        "log_date": "2026-04-19 16:55:01.000"
    },
    "2653": {
        "category": "산책",
        "log_status": "48",
        "log_date": "2026-04-19 18:30:35.000"
    },
    "2667": {
        "category": "급여량",
        "log_status": "82",
        "log_date": "2026-04-20 13:20:28.000"
    },
    "2674": {
        "category": "음수량",
        "log_status": "24",
        "log_date": "2026-04-20 15:39:38.000"
    },
    "2686": {
        "category": "급여량",
        "log_status": "113",
        "log_date": "2026-04-20 17:27:56.000"
    },
    "2691": {
        "category": "산책",
        "log_status": "49",
        "log_date": "2026-04-20 18:53:41.000"
    },
    "2708": {
        "category": "급여량",
        "log_status": "78",
        "log_date": "2026-04-21 12:11:14.000"
    },
    "2718": {
        "category": "음수량",
        "log_status": "28",
        "log_date": "2026-04-21 16:44:44.000"
    },
    "2723": {
        "category": "급여량",
        "log_status": "105",
        "log_date": "2026-04-21 17:47:06.000"
    },
    "2729": {
        "category": "산책",
        "log_status": "54",
        "log_date": "2026-04-21 18:28:31.000"
    },
    "2742": {
        "category": "급여량",
        "log_status": "80",
        "log_date": "2026-04-22 12:04:38.000"
    },
    "2753": {
        "category": "음수량",
        "log_status": "27",
        "log_date": "2026-04-22 15:38:55.000"
    },
    "2763": {
        "category": "급여량",
        "log_status": "115",
        "log_date": "2026-04-22 16:55:40.000"
    },
    "2772": {
        "category": "산책",
        "log_status": "42",
        "log_date": "2026-04-22 19:05:12.000"
    },
    "2788": {
        "category": "급여량",
        "log_status": "82",
        "log_date": "2026-04-23 13:32:35.000"
    },
    "2798": {
        "category": "음수량",
        "log_status": "27",
        "log_date": "2026-04-23 16:39:43.000"
    },
    "2803": {
        "category": "급여량",
        "log_status": "113",
        "log_date": "2026-04-23 17:18:35.000"
    },
    "2814": {
        "category": "산책",
        "log_status": "42",
        "log_date": "2026-04-23 19:18:29.000"
    },
    "2824": {
        "category": "급여량",
        "log_status": "77",
        "log_date": "2026-04-24 12:39:01.000"
    },
    "2829": {
        "category": "음수량",
        "log_status": "19",
        "log_date": "2026-04-24 16:10:32.000"
    },
    "2840": {
        "category": "급여량",
        "log_status": "107",
        "log_date": "2026-04-24 16:01:46.000"
    },
    "2851": {
        "category": "산책",
        "log_status": "47",
        "log_date": "2026-04-24 19:17:44.000"
    },
    "2861": {
        "category": "급여량",
        "log_status": "79",
        "log_date": "2026-04-25 13:30:00.000"
    },
    "2866": {
        "category": "음수량",
        "log_status": "28",
        "log_date": "2026-04-25 16:03:03.000"
    },
    "2875": {
        "category": "급여량",
        "log_status": "109",
        "log_date": "2026-04-25 17:03:26.000"
    },
    "2887": {
        "category": "산책",
        "log_status": "51",
        "log_date": "2026-04-25 19:05:25.000"
    },
    "2906": {
        "category": "급여량",
        "log_status": "72",
        "log_date": "2026-04-26 12:04:56.000"
    },
    "2918": {
        "category": "음수량",
        "log_status": "20",
        "log_date": "2026-04-26 16:10:53.000"
    },
    "2930": {
        "category": "급여량",
        "log_status": "107",
        "log_date": "2026-04-26 17:16:51.000"
    },
    "2942": {
        "category": "산책",
        "log_status": "48",
        "log_date": "2026-04-26 18:48:54.000"
    },
    "2957": {
        "category": "급여량",
        "log_status": "82",
        "log_date": "2026-04-27 13:07:51.000"
    },
    "2968": {
        "category": "음수량",
        "log_status": "27",
        "log_date": "2026-04-27 16:36:04.000"
    },
    "2983": {
        "category": "급여량",
        "log_status": "109",
        "log_date": "2026-04-27 17:47:51.000"
    },
    "2991": {
        "category": "산책",
        "log_status": "42",
        "log_date": "2026-04-27 20:14:10.000"
    },
    "3008": {
        "category": "급여량",
        "log_status": "72",
        "log_date": "2026-04-28 13:15:09.000"
    },
    "3023": {
        "category": "음수량",
        "log_status": "28",
        "log_date": "2026-04-28 15:12:29.000"
    },
    "3034": {
        "category": "급여량",
        "log_status": "107",
        "log_date": "2026-04-28 16:41:03.000"
    },
    "3039": {
        "category": "산책",
        "log_status": "52",
        "log_date": "2026-04-28 18:15:46.000"
    },
    "3055": {
        "category": "급여량",
        "log_status": "79",
        "log_date": "2026-04-29 13:24:54.000"
    },
    "3061": {
        "category": "음수량",
        "log_status": "20",
        "log_date": "2026-04-29 15:24:40.000"
    },
    "3068": {
        "category": "급여량",
        "log_status": "115",
        "log_date": "2026-04-29 16:59:47.000"
    },
    "3082": {
        "category": "산책",
        "log_status": "42",
        "log_date": "2026-04-29 18:26:01.000"
    },
    "3096": {
        "category": "급여량",
        "log_status": "77",
        "log_date": "2026-04-30 12:07:47.000"
    },
    "3103": {
        "category": "음수량",
        "log_status": "25",
        "log_date": "2026-04-30 16:14:06.000"
    },
    "3118": {
        "category": "급여량",
        "log_status": "115",
        "log_date": "2026-04-30 17:13:27.000"
    },
    "3133": {
        "category": "산책",
        "log_status": "49",
        "log_date": "2026-04-30 20:48:26.000"
    },
    "3148": {
        "category": "급여량",
        "log_status": "82",
        "log_date": "2026-05-01 12:57:26.000"
    },
    "3160": {
        "category": "음수량",
        "log_status": "22",
        "log_date": "2026-05-01 15:49:10.000"
    },
    "3166": {
        "category": "급여량",
        "log_status": "109",
        "log_date": "2026-05-01 16:37:27.000"
    },
    "3180": {
        "category": "산책",
        "log_status": "55",
        "log_date": "2026-05-01 20:15:57.000"
    },
    "3190": {
        "category": "급여량",
        "log_status": "73",
        "log_date": "2026-05-02 13:53:10.000"
    },
    "3205": {
        "category": "음수량",
        "log_status": "29",
        "log_date": "2026-05-02 16:55:54.000"
    },
    "3212": {
        "category": "급여량",
        "log_status": "115",
        "log_date": "2026-05-02 16:47:33.000"
    },
    "3223": {
        "category": "산책",
        "log_status": "47",
        "log_date": "2026-05-02 19:37:36.000"
    },
    "3239": {
        "category": "급여량",
        "log_status": "78",
        "log_date": "2026-05-03 13:58:20.000"
    },
    "3245": {
        "category": "음수량",
        "log_status": "20",
        "log_date": "2026-05-03 16:51:42.000"
    },
    "3253": {
        "category": "급여량",
        "log_status": "115",
        "log_date": "2026-05-03 16:26:22.000"
    },
    "3258": {
        "category": "산책",
        "log_status": "54",
        "log_date": "2026-05-03 19:19:51.000"
    },
    "3277": {
        "category": "급여량",
        "log_status": "72",
        "log_date": "2026-05-04 13:22:42.000"
    },
    "3290": {
        "category": "음수량",
        "log_status": "19",
        "log_date": "2026-05-04 16:02:39.000"
    },
    "3298": {
        "category": "급여량",
        "log_status": "111",
        "log_date": "2026-05-04 16:24:08.000"
    },
    "3310": {
        "category": "산책",
        "log_status": "55",
        "log_date": "2026-05-04 19:34:39.000"
    },
    "3330": {
        "category": "급여량",
        "log_status": "80",
        "log_date": "2026-05-05 12:27:47.000"
    },
    "3338": {
        "category": "음수량",
        "log_status": "26",
        "log_date": "2026-05-05 15:51:40.000"
    },
    "3344": {
        "category": "급여량",
        "log_status": "111",
        "log_date": "2026-05-05 17:10:43.000"
    },
    "3355": {
        "category": "산책",
        "log_status": "48",
        "log_date": "2026-05-05 19:10:32.000"
    },
    "3367": {
        "category": "급여량",
        "log_status": "76",
        "log_date": "2026-05-06 12:04:33.000"
    },
    "3374": {
        "category": "음수량",
        "log_status": "27",
        "log_date": "2026-05-06 16:15:14.000"
    },
    "3381": {
        "category": "급여량",
        "log_status": "110",
        "log_date": "2026-05-06 16:03:14.000"
    },
    "3386": {
        "category": "산책",
        "log_status": "58",
        "log_date": "2026-05-06 19:14:12.000"
    },
    "3401": {
        "category": "급여량",
        "log_status": "79",
        "log_date": "2026-05-07 12:45:16.000"
    },
    "3410": {
        "category": "음수량",
        "log_status": "19",
        "log_date": "2026-05-07 16:08:39.000"
    },
    "3425": {
        "category": "급여량",
        "log_status": "115",
        "log_date": "2026-05-07 16:40:29.000"
    },
    "3434": {
        "category": "산책",
        "log_status": "43",
        "log_date": "2026-05-07 20:19:44.000"
    },
    "3454": {
        "category": "급여량",
        "log_status": "76",
        "log_date": "2026-05-08 12:35:18.000"
    },
    "3461": {
        "category": "음수량",
        "log_status": "22",
        "log_date": "2026-05-08 16:02:08.000"
    },
    "3475": {
        "category": "급여량",
        "log_status": "105",
        "log_date": "2026-05-08 16:56:56.000"
    },
    "3485": {
        "category": "산책",
        "log_status": "51",
        "log_date": "2026-05-08 19:29:42.000"
    }
}