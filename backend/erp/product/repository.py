from backend.db.db import SessionLocal
from backend.db.models import OpdProductDetail
from backend.erp.common.query_utils import model_to_dict, like_keyword
from backend.erp.common.mutation_utils import clean_text, to_float_or_none, require_text


# =========================================================
# ☑️ 상품관리 Repository
# - OPD.product_detail ORM 모델 기반 조회
# - 상품명 / 타입 / 브랜드 / 기능 / 급여단계 / 주원료 검색 처리
# - 상품마스터정보관리와 상품 상세 정보 관리가 함께 사용
# - count + limit/offset 페이지네이션 처리
# =========================================================

PRODUCT_DETAIL_COLUMNS = [
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


def _apply_product_detail_filter(query, search_type: str, keyword: str):
    clean = (keyword or "").strip()

    if not clean:
        return query

    if search_type == "product_name":
        return query.filter(OpdProductDetail.product_name.ilike(like_keyword(clean)))

    if search_type == "type":
        return query.filter(OpdProductDetail.type.ilike(like_keyword(clean)))

    if search_type == "brand":
        return query.filter(OpdProductDetail.brand.ilike(like_keyword(clean)))

    if search_type == "function":
        return query.filter(OpdProductDetail.function.ilike(like_keyword(clean)))

    if search_type == "life":
        return query.filter(OpdProductDetail.life.ilike(like_keyword(clean)))

    if search_type == "main_protein":
        return query.filter(OpdProductDetail.main_protein.ilike(like_keyword(clean)))

    return query


def count_product_details(search_type="product_name", keyword=""):
    db = SessionLocal()
    try:
        query = db.query(OpdProductDetail)
        query = _apply_product_detail_filter(query, search_type, keyword)
        return query.count()
    finally:
        db.close()


def fetch_product_details(search_type="product_name", keyword="", limit=50, offset=0):
    db = SessionLocal()
    try:
        query = db.query(OpdProductDetail)
        query = _apply_product_detail_filter(query, search_type, keyword)
        rows = (
            query.order_by(OpdProductDetail.product_name.asc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [model_to_dict(row, PRODUCT_DETAIL_COLUMNS) for row in rows]
    finally:
        db.close()


# =========================================================
# ☑️ 상품 상세 등록
# - 상품마스터/상품상세 화면 모두 OPD.product_detail 기준으로 등록
# =========================================================
def create_product_detail(data: dict):
    db = SessionLocal()
    try:
        life = require_text(data.get("life"), "생애주기")
        if life not in {"전연령", "퍼피", "어덜트", "시니어"}:
            raise ValueError("생애주기는 전연령, 퍼피, 어덜트, 시니어 중 하나여야 합니다.")

        product_type = require_text(data.get("type"), "타입")
        brand = require_text(data.get("brand"), "브랜드")
        product_name = require_text(data.get("product_name"), "상품명")

        if db.query(OpdProductDetail).filter(
            OpdProductDetail.type == product_type,
            OpdProductDetail.brand == brand,
            OpdProductDetail.product_name == product_name,
        ).first():
            raise ValueError("동일한 타입/브랜드/상품명이 이미 존재합니다.")

        product_detail = OpdProductDetail(
            type=product_type,
            brand=brand,
            product_name=product_name,
            function=clean_text(data.get("function")),
            description=clean_text(data.get("description")),
            crude_protein=to_float_or_none(data.get("crude_protein")),
            crude_fat=to_float_or_none(data.get("crude_fat")),
            calories=to_float_or_none(data.get("calories")),
            thumbnail=clean_text(data.get("thumbnail")),
            kibble_size=clean_text(data.get("kibble_size")),
            life=life,
            protein_type=clean_text(data.get("protein_type")),
            main_protein=clean_text(data.get("main_protein")),
            certified=clean_text(data.get("certified")),
            preservative=clean_text(data.get("preservative")),
            feedshape=clean_text(data.get("feedshape")),
        )
        db.add(product_detail)
        db.commit()
        db.refresh(product_detail)
        return model_to_dict(product_detail, PRODUCT_DETAIL_COLUMNS)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
