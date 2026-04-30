# =========================================================
# ☑️ 상품 마스터 정보 등록 필드
# - 현재 상품마스터 화면도 OPD.product_detail 기반으로 조회됨
# - DB에 없는 product_code / manufacturer / barcode / stock_unit 등은 제거
# =========================================================
PRODUCT_MASTER_FIELDS = [
    {"label": "타입", "key": "type", "type": "text", "required": True, "max_length": 9},
    {"label": "브랜드", "key": "brand", "type": "text", "required": True, "max_length": 255},
    {"label": "상품명", "key": "product_name", "type": "text", "required": True, "max_length": 100},
    {
        "label": "생애주기",
        "key": "life",
        "type": "text",
        "required": True,
        "max_length": 6,
        "allowed_values": ["전연령", "퍼피", "어덜트", "시니어"],
    },
    {"label": "주원료", "key": "main_protein", "type": "text", "required": False, "max_length": 30},
    {"label": "알갱이 크기", "key": "kibble_size", "type": "text", "required": False, "max_length": 20},
    {"label": "칼로리", "key": "calories", "type": "float", "required": False, "max_length": 10},
]


# =========================================================
# ☑️ 상품 상세 정보 등록 필드
# - OPD.product_detail + OPD.product JOIN 화면 기준
# - 상세 정보 등록 시 product_detail 저장 후 product 옵션 1건도 함께 저장
# =========================================================
PRODUCT_DETAIL_FIELDS = [
    {"label": "타입", "key": "type", "type": "text", "required": True, "max_length": 9},
    {"label": "브랜드", "key": "brand", "type": "text", "required": True, "max_length": 255},
    {"label": "상품명", "key": "product_name", "type": "text", "required": True, "max_length": 100},
    {"label": "기능", "key": "function", "type": "text", "required": False, "max_length": 200},
    {"label": "설명", "key": "description", "type": "text", "required": False, "max_length": 500},
    {"label": "조단백", "key": "crude_protein", "type": "float", "required": False, "max_length": 10},
    {"label": "조지방", "key": "crude_fat", "type": "float", "required": False, "max_length": 10},
    {"label": "칼로리", "key": "calories", "type": "float", "required": False, "max_length": 10},
    {"label": "썸네일 URL", "key": "thumbnail", "type": "url", "required": False, "max_length": 300},
    {"label": "알갱이 크기", "key": "kibble_size", "type": "text", "required": False, "max_length": 20},
    {
        "label": "생애주기",
        "key": "life",
        "type": "text",
        "required": True,
        "max_length": 6,
        "allowed_values": ["전연령", "퍼피", "어덜트", "시니어"],
    },
    {"label": "단백질 유형", "key": "protein_type", "type": "text", "required": False, "max_length": 9},
    {"label": "주원료", "key": "main_protein", "type": "text", "required": False, "max_length": 30},
    {"label": "인증", "key": "certified", "type": "text", "required": False, "max_length": 30},
    {"label": "방부제", "key": "preservative", "type": "text", "required": False, "max_length": 30},
    {"label": "사료 형태", "key": "feedshape", "type": "text", "required": False, "max_length": 20},
    {"label": "중량(g)", "key": "weight", "type": "int", "required": True, "max_length": 10, "min_value": 1},
    {"label": "판매가", "key": "retail_price", "type": "int", "required": True, "max_length": 10, "min_value": 0},
    {"label": "수량(ea)", "key": "quantity", "type": "int", "required": True, "max_length": 10, "min_value": 1},
    {"label": "판매상태", "key": "active", "type": "bool", "required": True, "max_length": 10},
]


# =========================================================
# ☑️ 고객 등록 필드
# - Companion.customer 실제 컬럼 기준
# =========================================================
CUSTOMER_FIELDS = [
    {"label": "고객ID", "key": "customer_id", "type": "int", "required": True, "max_length": 10, "min_value": 1},
    {"label": "구독여부", "key": "is_subscribed", "type": "bool", "required": True, "max_length": 10},
    {"label": "구독횟수", "key": "subs_count", "type": "int", "required": True, "max_length": 10, "min_value": 0},
    {"label": "권한", "key": "permission", "type": "int", "required": True, "max_length": 10, "min_value": 0},
    {"label": "상태", "key": "active", "type": "bool", "required": True, "max_length": 10},
]


# =========================================================
# ☑️ 사원 등록 필드
# - ERP.employee 실제 컬럼 기준
# =========================================================
EMPLOYEE_FIELDS = [
    {"label": "사원ID", "key": "employee_id", "type": "int", "required": True, "max_length": 10, "min_value": 1},
    {"label": "계정", "key": "account_id", "type": "text", "required": True, "max_length": 255},
    {"label": "비밀번호", "key": "password", "type": "password", "required": True, "max_length": 255},
    {"label": "이름", "key": "username", "type": "name", "required": True, "max_length": 10},
    {"label": "입사일", "key": "hire_date", "type": "date", "required": True, "max_length": 10},
    {"label": "퇴사일", "key": "quit_date", "type": "date", "required": False, "max_length": 10},
    {"label": "직급ID", "key": "emp_position_id", "type": "int", "required": False, "max_length": 10, "min_value": 1},
    {"label": "관리자ID", "key": "manager_id", "type": "int", "required": False, "max_length": 10, "min_value": 1},
    {"label": "이메일", "key": "email", "type": "email", "required": True, "max_length": 255},
    {"label": "전화번호", "key": "phone", "type": "phone", "required": True, "max_length": 13},
    {"label": "주소", "key": "address", "type": "text", "required": True, "max_length": 255},
    {"label": "우편번호", "key": "postal_code", "type": "postal", "required": True, "max_length": 5},
    {"label": "재직여부", "key": "active", "type": "bool", "required": True, "max_length": 10},
]


# =========================================================
# ☑️ 거래처 등록 필드
# - ERP.supplier 실제 컬럼 기준
# =========================================================
SUPPLIER_FIELDS = [
    {"label": "거래처명", "key": "supplier_name", "type": "text", "required": True, "max_length": 30},
    {"label": "사업자번호", "key": "brn", "type": "bizno", "required": True, "max_length": 12},
    {"label": "연락상태", "key": "is_contact_status", "type": "bool", "required": True, "max_length": 10},
    {"label": "지정결제일", "key": "designated_payment_date", "type": "day", "required": True, "max_length": 2},
    {"label": "예정결제일", "key": "scheduled_payment_date", "type": "date", "required": True, "max_length": 10},
    {"label": "담당자ID", "key": "employee_id", "type": "int", "required": True, "max_length": 10, "min_value": 1},
    {"label": "메모", "key": "memo", "type": "text", "required": False, "max_length": 300},
    {"label": "담당자명", "key": "sup_manager", "type": "name", "required": True, "max_length": 10},
    {"label": "전화번호", "key": "phone", "type": "phone", "required": True, "max_length": 13},
]