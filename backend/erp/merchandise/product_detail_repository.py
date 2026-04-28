from db.db import SessionLocal
from db.models import OpdProduct, OpdProductDetail
from ..common.query_utils import like_keyword, model_to_dict
from ..common.mutation_utils import (
    clean_text,
    to_float_or_none,
    to_int_or_none,
    to_bool_or_none,
    require_text,
    require_int,
    require_bool,
)
from sqlalchemy import String


# =========================================================
# ☑️ 상품관리 Repository
# - 상품 상세 정보 조회 화면은 OPD.product + OPD.product_detail JOIN 기준
# - product_detail_id 로 조인하여 판매옵션(weight / retail_price / quantity)까지 함께 조회
# - pdi 는 화면에서 사용하지 않으므로 조회 응답에서 제외
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

PRODUCT_JOIN_COLUMNS = [
    "product_id",
    "product_detail_id",
    "quantity",
    "retail_price",
    "weight",
    "is_sample",
    "active",
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


def _build_join_query(db):
    return (
        db.query(OpdProduct, OpdProductDetail)
        .join(
            OpdProductDetail,
            OpdProduct.product_detail_id == OpdProductDetail.product_detail_id,
        )
    )


def _normalize_numeric_keyword(keyword: str):
    return (keyword or "").replace(",", "").replace("g", "").replace("G", "").strip()


def _apply_product_join_filter(query, search_type: str, keyword: str):
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

    if search_type == "weight":
        numeric = _normalize_numeric_keyword(clean)
        if numeric.isdigit():
            return query.filter(OpdProduct.weight == int(numeric))
        return query.filter(OpdProduct.weight.cast(String).ilike(like_keyword(numeric)))

    if search_type == "retail_price":
        numeric = _normalize_numeric_keyword(clean)
        if numeric.isdigit():
            return query.filter(OpdProduct.retail_price == int(numeric))
        return query.filter(OpdProduct.retail_price.cast(String).ilike(like_keyword(numeric)))

    if search_type == "quantity":
        numeric = _normalize_numeric_keyword(clean)
        if numeric.isdigit():
            return query.filter(OpdProduct.quantity == int(numeric))
        return query.filter(OpdProduct.quantity.cast(String).ilike(like_keyword(numeric)))

    return query


def _product_join_row_to_dict(product, detail):
    row = {
        "product_id": getattr(product, "product_id", ""),
        "product_detail_id": getattr(product, "product_detail_id", ""),
        "quantity": getattr(product, "quantity", ""),
        "retail_price": getattr(product, "retail_price", ""),
        "weight": getattr(product, "weight", ""),
        "is_sample": getattr(product, "is_sample", ""),
        "active": getattr(product, "active", ""),
        "type": getattr(detail, "type", ""),
        "brand": getattr(detail, "brand", ""),
        "product_name": getattr(detail, "product_name", ""),
        "function": getattr(detail, "function", ""),
        "description": getattr(detail, "description", ""),
        "crude_protein": getattr(detail, "crude_protein", ""),
        "crude_fat": getattr(detail, "crude_fat", ""),
        "calories": getattr(detail, "calories", ""),
        "thumbnail": getattr(detail, "thumbnail", ""),
        "kibble_size": getattr(detail, "kibble_size", ""),
        "life": getattr(detail, "life", ""),
        "protein_type": getattr(detail, "protein_type", ""),
        "main_protein": getattr(detail, "main_protein", ""),
        "certified": getattr(detail, "certified", ""),
        "preservative": getattr(detail, "preservative", ""),
        "feedshape": getattr(detail, "feedshape", ""),
        "last_update": getattr(product, "last_update", None) or getattr(detail, "last_update", None),
    }
    return row


def count_product_join_rows(search_type="product_name", keyword=""):
    db = SessionLocal()
    try:
        query = _build_join_query(db)
        query = _apply_product_join_filter(query, search_type, keyword)
        return query.count()
    finally:
        db.close()


def fetch_product_join_rows(search_type="product_name", keyword="", limit=50, offset=0):
    db = SessionLocal()
    try:
        query = _build_join_query(db)
        query = _apply_product_join_filter(query, search_type, keyword)
        rows = (
            query.order_by(
                OpdProductDetail.product_name.asc(),
                OpdProduct.weight.asc(),
                OpdProduct.product_id.asc(),
            )
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [_product_join_row_to_dict(product, detail) for product, detail in rows]
    finally:
        db.close()


# =========================================================
# ☑️ 상품 상세 등록
# - 상품상세 등록 시 OPD.product_detail 1건 + OPD.product 1건 함께 저장
# - 저장 직후 JOIN 목록에 바로 노출될 수 있도록 판매옵션도 동시에 생성
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

        weight = require_int(data.get("weight"), "중량(g)")
        retail_price = require_int(data.get("retail_price"), "판매가")
        quantity = require_int(data.get("quantity"), "수량(ea)")
        active = require_bool(data.get("active"), "판매상태")

        if weight < 1:
            raise ValueError("중량(g)은 1 이상이어야 합니다.")
        if retail_price < 0:
            raise ValueError("판매가는 0 이상이어야 합니다.")
        if quantity < 1:
            raise ValueError("수량(ea)은 1 이상이어야 합니다.")

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
        db.flush()

        product = OpdProduct(
            product_detail_id=product_detail.product_detail_id,
            quantity=quantity,
            retail_price=retail_price,
            weight=weight,
            is_sample=to_bool_or_none(data.get("is_sample"), False),
            active=active,
        )
        db.add(product)

        db.commit()
        db.refresh(product_detail)
        db.refresh(product)

        return {
            "product_detail": model_to_dict(product_detail, PRODUCT_DETAIL_COLUMNS),
            "product": {
                "product_id": getattr(product, "product_id", None),
                "product_detail_id": getattr(product, "product_detail_id", None),
                "quantity": getattr(product, "quantity", None),
                "retail_price": getattr(product, "retail_price", None),
                "weight": getattr(product, "weight", None),
                "is_sample": getattr(product, "is_sample", None),
                "active": getattr(product, "active", None),
                "last_update": getattr(product, "last_update", None),
            },
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()