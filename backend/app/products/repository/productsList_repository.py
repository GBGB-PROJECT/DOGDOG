from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from db.models import OpdProductDetail, OpdProduct

VALID_SORTS = {"price_desc", "price_asc", "weight_desc", "weight_asc"}

def get_product_detail_list(db: Session, keyword: str | None = None):
    query = (
        select(OpdProductDetail.product_detail_id, 
                OpdProductDetail.product_name, 
            )
    )

    if keyword is not None and keyword.strip() != "": # 키워드가 있을때
        query = query.where(OpdProductDetail.product_name.ilike(f"%{keyword.strip()}%"))

    result = db.execute(query)
    # products = result.scalars().all()
    products = result.all()

    return products

def get_product_list(
        db: Session, 
        keyword: str | None = None,
        sort: str | None = None,
    ):
    query = (
        select(
            OpdProduct.product_id.label("product_id"),
            OpdProductDetail.product_detail_id.label("product_detail_id"),
            OpdProductDetail.thumbnail.label("thumbnail"), 
            OpdProductDetail.product_name.label("product_name"), 
            OpdProductDetail.brand.label("brand"),
            OpdProductDetail.type.label("type"),
            OpdProductDetail.function.label("function"),
            OpdProduct.retail_price.label("retail_price"),
            OpdProduct.weight.label("weight"),
            OpdProduct.quantity.label("quantity"),
            OpdProduct.is_sample.label("is_sample")
        )
        .join(
            OpdProductDetail,
            OpdProduct.product_detail_id == OpdProductDetail.product_detail_id
        )
        .where(OpdProduct.active == True)
    )

    # # 검색
    # if keyword is not None and keyword.strip() != "": # 키워드가 있을때
    #     query = query.where(OpdProductDetail.product_name.ilike(f"%{keyword.strip()}%"))

    # 검색
    if keyword is not None and keyword.strip() != "":
        keyword_pattern = f"%{keyword.strip()}%"
        query = query.where(
            or_(
                OpdProductDetail.product_name.ilike(keyword_pattern),
                OpdProductDetail.brand.ilike(keyword_pattern),
                OpdProductDetail.function.ilike(keyword_pattern),
                OpdProductDetail.type.ilike(keyword_pattern),
                OpdProductDetail.life.ilike(keyword_pattern),
                OpdProductDetail.main_protein.ilike(keyword_pattern),
                OpdProductDetail.protein_type.ilike(keyword_pattern),
                OpdProductDetail.preservative.ilike(keyword_pattern)
            )
        )

    # 정렬
    if sort == "price_desc":
        query = query.order_by(
            OpdProduct.retail_price.desc(),
            OpdProduct.product_id.asc(),
        )
    elif sort == "price_asc":
        query = query.order_by(
            OpdProduct.retail_price.asc(),
            OpdProduct.product_id.asc(),
        )
    elif sort == "weight_desc":
        query = query.order_by(
            OpdProduct.weight.desc(),
            OpdProduct.product_id.asc(),
        )
    elif sort == "weight_asc":
        query = query.order_by(
            OpdProduct.weight.asc(),
            OpdProduct.product_id.asc(),
        )
    else:
        # 기본 정렬: 등록순 느낌으로 product_id ASC
        query = query.order_by(
            OpdProductDetail.product_name.asc(),
            OpdProduct.product_id.asc(),
        )


    result = db.execute(query)
    # products = result.scalars().all()
    products = result.all()

    return products