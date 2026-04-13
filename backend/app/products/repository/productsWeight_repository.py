from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import OpdProduct

def get_product_weight(db: Session, product_detail_id: int):
    query = (
        select(OpdProduct.product_id,  
                OpdProduct.weight,
                OpdProduct.active
                )
        .where(OpdProduct.active == True, OpdProduct.product_detail_id == product_detail_id)
    )

    result = db.execute(query)
    # products = result.scalars().all()
    # products = result.mappings().all()
    products = result.all()

    return products