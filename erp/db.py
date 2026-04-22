import os
from pathlib import Path
from decimal import Decimal
from datetime import datetime, date
from urllib.parse import quote_plus

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    Numeric,
    String,
    Text,
    create_engine,
    cast,
    func,
    case,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.types import String as SAString


# =========================================================
# ☑️ .env 파일 로드
# - erp/.env 파일의 DB 접속정보를 환경변수로 올림
# - python-dotenv 없이 표준 라이브러리만 사용
# =========================================================
def load_env_file():
    env_path = Path(__file__).resolve().parent / ".env"

    if not env_path.exists():
        return

    with env_path.open("r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file()


def get_required_env(key: str):
    value = os.getenv(key)

    if value is None or value.strip() == "":
        raise RuntimeError(
            f"DB 환경변수 {key} 값이 없습니다. erp/.env 파일에 {key}=... 형식으로 추가해주세요."
        )

    return value.strip()


# =========================================================
# ☑️ SQLAlchemy ORM 연결 설정
# - 기존 psycopg2 직접 연결 대신 SQLAlchemy engine/session 사용
# =========================================================
def get_db_url():
    user = quote_plus(get_required_env("DB_USER"))
    password = quote_plus(get_required_env("DB_PASSWORD"))
    host = get_required_env("DB_HOST")
    port = get_required_env("DB_PORT")
    dbname = get_required_env("DB_NAME")

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"


engine = create_engine(
    get_db_url(),
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# =========================================================
# ☑️ ORM 모델 정의
# - 실제 DB 테이블을 Python class로 매핑
# - 조회에 필요한 컬럼만 우선 정의
# =========================================================
class CustomerModel(Base):
    __tablename__ = "customer"
    __table_args__ = {"schema": "Companion"}

    customer_id = Column(BigInteger, primary_key=True)
    is_subscribed = Column(Boolean)
    subs_count = Column(Integer)
    permission = Column(Integer)
    active = Column(Boolean)
    last_update = Column(DateTime)


class EmployeeModel(Base):
    __tablename__ = "employee"
    __table_args__ = {"schema": "ERP"}

    employee_id = Column(BigInteger, primary_key=True)
    account_id = Column(String)
    username = Column(String)
    hire_date = Column(Date)
    quit_date = Column(Date)
    emp_position_id = Column(BigInteger)
    manager_id = Column(BigInteger)
    email = Column(String)
    phone = Column(String)
    address = Column(Text)
    postal_code = Column(String)
    active = Column(Boolean)


class ProductDetailModel(Base):
    __tablename__ = "product_detail"
    __table_args__ = {"schema": "OPD"}

    product_detail_id = Column(BigInteger, primary_key=True)
    type = Column(String)
    brand = Column(String)
    product_name = Column(String)
    function = Column(Text)
    description = Column(Text)
    crude_protein = Column(Numeric)
    crude_fat = Column(Numeric)
    calories = Column(Numeric)
    thumbnail = Column(Text)
    kibble_size = Column(String)
    life = Column(String)
    protein_type = Column(String)
    main_protein = Column(String)
    certified = Column(String)
    preservative = Column(String)
    feedshape = Column(String)
    last_update = Column(DateTime)


class SupplierModel(Base):
    __tablename__ = "supplier"
    __table_args__ = {"schema": "ERP"}

    supplier_id = Column(BigInteger, primary_key=True)
    supplier_name = Column(String)
    brn = Column(String)
    is_contact_status = Column(Boolean)
    designated_payment_date = Column(Date)
    scheduled_payment_date = Column(Date)
    employee_id = Column(BigInteger)
    memo = Column(Text)
    sup_manager = Column(String)
    phone = Column(String)
    last_update = Column(DateTime)


# =========================================================
# ☑️ Flet 표시용 값 변환
# - Decimal/date/datetime을 화면에서 쓰기 쉬운 타입으로 변환
# =========================================================
def sanitize_for_flet(value):
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (datetime, date)):
        return str(value)

    if isinstance(value, dict):
        return {key: sanitize_for_flet(val) for key, val in value.items()}

    if isinstance(value, list):
        return [sanitize_for_flet(item) for item in value]

    if isinstance(value, tuple):
        return tuple(sanitize_for_flet(item) for item in value)

    return value


def model_to_dict(obj, keys):
    return sanitize_for_flet({key: getattr(obj, key, None) for key in keys})


def like_value(keyword: str):
    return f"%{(keyword or '').strip()}%"


# =========================================================
# ☑️ 고객관리 ORM 조회
# =========================================================
def apply_customer_filter(query, search_type: str, keyword: str):
    clean = (keyword or "").strip()
    if not clean:
        return query

    if search_type == "customer_id":
        return query.filter(cast(CustomerModel.customer_id, SAString).like(like_value(clean)))

    if search_type == "is_subscribed":
        lowered = clean.lower()
        if lowered in ["y", "yes", "true", "1", "구독", "사용", "활성"]:
            return query.filter(CustomerModel.is_subscribed.is_(True))
        if lowered in ["n", "no", "false", "0", "미구독", "비구독", "비활성"]:
            return query.filter(CustomerModel.is_subscribed.is_(False))
        label_expr = case((CustomerModel.is_subscribed.is_(True), "Y"), else_="N")
        return query.filter(func.lower(label_expr).like(func.lower(like_value(clean))))

    if search_type == "subs_count":
        return query.filter(cast(CustomerModel.subs_count, SAString).like(like_value(clean)))

    if search_type == "permission":
        return query.filter(cast(CustomerModel.permission, SAString).like(like_value(clean)))

    if search_type == "active":
        lowered = clean.lower()
        if lowered in ["활성", "사용", "y", "yes", "true", "1"]:
            return query.filter(CustomerModel.active.is_(True))
        if lowered in ["비활성", "미사용", "n", "no", "false", "0"]:
            return query.filter(CustomerModel.active.is_(False))
        label_expr = case((CustomerModel.active.is_(True), "활성"), else_="비활성")
        return query.filter(func.lower(label_expr).like(func.lower(like_value(clean))))

    return query


def count_customers(search_type="customer_id", keyword=""):
    with SessionLocal() as session:
        query = session.query(CustomerModel)
        query = apply_customer_filter(query, search_type, keyword)
        return query.count()


def fetch_customers(search_type="customer_id", keyword="", limit=50, offset=0):
    keys = ["customer_id", "is_subscribed", "subs_count", "permission", "active", "last_update"]
    with SessionLocal() as session:
        query = session.query(CustomerModel)
        query = apply_customer_filter(query, search_type, keyword)
        rows = query.order_by(CustomerModel.customer_id.asc()).limit(limit).offset(offset).all()
        return [model_to_dict(row, keys) for row in rows]


# =========================================================
# ☑️ 인사관리 ORM 조회
# =========================================================
def apply_employee_filter(query, search_type: str, keyword: str):
    clean = (keyword or "").strip()
    if not clean:
        return query

    if search_type == "username":
        return query.filter(func.lower(func.coalesce(EmployeeModel.username, "")).like(func.lower(like_value(clean))))
    if search_type == "employee_id":
        return query.filter(cast(EmployeeModel.employee_id, SAString).like(like_value(clean)))
    if search_type == "account_id":
        return query.filter(func.lower(func.coalesce(EmployeeModel.account_id, "")).like(func.lower(like_value(clean))))
    if search_type == "emp_position_id":
        return query.filter(cast(EmployeeModel.emp_position_id, SAString).like(like_value(clean)))
    if search_type == "phone":
        return query.filter(func.lower(func.coalesce(EmployeeModel.phone, "")).like(func.lower(like_value(clean))))
    if search_type == "email":
        return query.filter(func.lower(func.coalesce(EmployeeModel.email, "")).like(func.lower(like_value(clean))))

    return query


def count_employees(search_type="username", keyword=""):
    with SessionLocal() as session:
        query = session.query(EmployeeModel)
        query = apply_employee_filter(query, search_type, keyword)
        return query.count()


def fetch_employees(search_type="username", keyword="", limit=50, offset=0):
    keys = [
        "employee_id",
        "account_id",
        "username",
        "hire_date",
        "quit_date",
        "emp_position_id",
        "manager_id",
        "email",
        "phone",
        "address",
        "postal_code",
        "active",
    ]
    with SessionLocal() as session:
        query = session.query(EmployeeModel)
        query = apply_employee_filter(query, search_type, keyword)
        rows = query.order_by(EmployeeModel.employee_id.asc()).limit(limit).offset(offset).all()
        return [model_to_dict(row, keys) for row in rows]


# =========================================================
# ☑️ 상품 상세 / 상품마스터 ORM 조회
# =========================================================
def apply_product_detail_filter(query, search_type: str, keyword: str):
    clean = (keyword or "").strip()
    if not clean:
        return query

    column_map = {
        "product_name": ProductDetailModel.product_name,
        "type": ProductDetailModel.type,
        "brand": ProductDetailModel.brand,
        "function": ProductDetailModel.function,
        "life": ProductDetailModel.life,
        "main_protein": ProductDetailModel.main_protein,
    }
    column = column_map.get(search_type, ProductDetailModel.product_name)
    return query.filter(func.lower(func.coalesce(column, "")).like(func.lower(like_value(clean))))


def count_product_details(search_type="product_name", keyword=""):
    with SessionLocal() as session:
        query = session.query(ProductDetailModel)
        query = apply_product_detail_filter(query, search_type, keyword)
        return query.count()


def fetch_product_details(search_type="product_name", keyword="", limit=50, offset=0):
    keys = [
        "product_detail_id",
        "type",
        "brand",
        "product_name",
        "function",
        "description",
        "crude_protein",
        "crude_fat",
        "calories",
        "thumbnail",
        "kibble_size",
        "life",
        "protein_type",
        "main_protein",
        "certified",
        "preservative",
        "feedshape",
        "last_update",
    ]
    with SessionLocal() as session:
        query = session.query(ProductDetailModel)
        query = apply_product_detail_filter(query, search_type, keyword)
        rows = query.order_by(ProductDetailModel.product_name.asc()).limit(limit).offset(offset).all()
        return [model_to_dict(row, keys) for row in rows]


# =========================================================
# ☑️ 거래처관리 ORM 조회
# =========================================================
def apply_supplier_filter(query, search_type: str, keyword: str, start_date=None, end_date=None):
    clean = (keyword or "").strip()

    if clean:
        if search_type == "supplier_id":
            query = query.filter(cast(SupplierModel.supplier_id, SAString).like(like_value(clean)))
        elif search_type == "supplier_name":
            query = query.filter(func.lower(func.coalesce(SupplierModel.supplier_name, "")).like(func.lower(like_value(clean))))
        elif search_type == "brn":
            query = query.filter(func.lower(func.coalesce(SupplierModel.brn, "")).like(func.lower(like_value(clean))))
        elif search_type == "sup_manager":
            query = query.filter(func.lower(func.coalesce(SupplierModel.sup_manager, "")).like(func.lower(like_value(clean))))
        elif search_type == "phone":
            query = query.filter(func.lower(func.coalesce(SupplierModel.phone, "")).like(func.lower(like_value(clean))))
        elif search_type == "is_contact_status":
            lowered = clean.lower()
            if lowered in ["활성", "가능", "사용", "y", "yes", "true", "1"]:
                query = query.filter(SupplierModel.is_contact_status.is_(True))
            elif lowered in ["비활성", "불가", "미사용", "n", "no", "false", "0"]:
                query = query.filter(SupplierModel.is_contact_status.is_(False))
            else:
                label_expr = case((SupplierModel.is_contact_status.is_(True), "활성"), else_="비활성")
                query = query.filter(func.lower(label_expr).like(func.lower(like_value(clean))))

    if start_date:
        query = query.filter(cast(SupplierModel.last_update, Date) >= start_date)

    if end_date:
        query = query.filter(cast(SupplierModel.last_update, Date) <= end_date)

    return query


def count_suppliers(search_type="supplier_name", keyword="", start_date=None, end_date=None):
    with SessionLocal() as session:
        query = session.query(SupplierModel)
        query = apply_supplier_filter(query, search_type, keyword, start_date, end_date)
        return query.count()


def fetch_suppliers(search_type="supplier_name", keyword="", limit=50, offset=0, start_date=None, end_date=None):
    keys = [
        "supplier_id",
        "supplier_name",
        "brn",
        "is_contact_status",
        "designated_payment_date",
        "scheduled_payment_date",
        "employee_id",
        "memo",
        "sup_manager",
        "phone",
        "last_update",
    ]
    with SessionLocal() as session:
        query = session.query(SupplierModel)
        query = apply_supplier_filter(query, search_type, keyword, start_date, end_date)
        rows = query.order_by(SupplierModel.supplier_id.asc()).limit(limit).offset(offset).all()
        return [model_to_dict(row, keys) for row in rows]


# =========================================================
# ☑️ 기존 이름 호환용
# - 혹시 다른 파일이 get_connection/fetch_all/fetch_one을 import하면 바로 깨지지 않도록 둠
# - 주요 ORM 전환 화면에서는 아래 함수들을 사용하지 않음
# =========================================================
def get_connection():
    return engine.connect()


def fetch_all(query: str, params=None):
    raise RuntimeError("SQLAlchemy ORM 전환 후에는 fetch_all 대신 ORM 조회 함수를 사용해주세요.")


def fetch_one(query: str, params=None):
    raise RuntimeError("SQLAlchemy ORM 전환 후에는 fetch_one 대신 ORM 조회 함수를 사용해주세요.")


def execute(query: str, params=None):
    raise RuntimeError("현재는 조회 전용 모드입니다. INSERT / UPDATE / DELETE 는 막아둔 상태입니다.")
