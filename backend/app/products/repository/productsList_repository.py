from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import OpdProductDetail

def get_product_list(db: Session, keyword: str | None = None):
    query = (
        select(OpdProductDetail.product_detail_id, 
                OpdProductDetail.product_name, 
                )
        # .options(joinedload(Product.product_detail))
        # .join(Product_Detail, Product.product_detail_id == Product_Detail.product_detail_id)
        # .where(Product.active == True)
    )

    if keyword is not None and keyword.strip() != "": # 키워드가 있을때
        query = query.where(OpdProductDetail.product_name.ilike(f"%{keyword.strip()}%"))

    result = db.execute(query)
    # products = result.scalars().all()
    products = result.all()

    return products