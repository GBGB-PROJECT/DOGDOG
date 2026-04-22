from db.db import SessionLocal
from db.models import OpdProductDetail
from backend.erp.common.query_utils import model_to_dict, like_keyword


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
