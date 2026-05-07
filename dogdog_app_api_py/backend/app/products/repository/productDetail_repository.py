from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import OpdProduct, OpdProductDetail


def get_active_product_by_id(db: Session, product_id: int):
    """
    활성 상품 1건 조회
    """
    query = (
        select(OpdProduct)
        .where(
            OpdProduct.product_id == product_id,
            OpdProduct.active == True
        )
    )
    result = db.execute(query)
    return result.scalar_one_or_none()


def get_product_detail_by_id(db: Session, product_detail_id: int):
    """
    상품 상세 본문 1건 조회
    """
    query = (
        select(OpdProductDetail)
        .where(OpdProductDetail.product_detail_id == product_detail_id)
    )
    result = db.execute(query)
    return result.scalar_one_or_none()
