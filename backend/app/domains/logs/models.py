from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Numeric, Boolean, SmallInteger
from sqlalchemy.sql import func
from db import Base

class CustomerFood(Base):
    __tablename__ = "customer_food"
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), primary_key=True)
    total_weight = Column(SmallInteger, nullable=False)
    feeding_start = Column(Date, nullable=False)
    total_intake = Column(SmallInteger, default=0)
    food_count = Column(SmallInteger, default=0)
    # DB에서 자동 계산되는 컬럼 (Generated)
    left_food_count = Column(Numeric(4, 1)) 
    left_intake = Column(Numeric(5, 1))
    last_update = Column(DateTime, server_default=func.now())

class PetProductFeeding(Base):
    __tablename__ = "pet_product_feeding"
    pet_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, primary_key=True)
    is_feeding_check = Column(Boolean, default=True)
    one_gram_calories = Column(Numeric(4, 2), nullable=False) # 1g당 열량

class FeedingLog(Base):
    __tablename__ = "pet_food"
    pet_food_id = Column(Integer, primary_key=True, autoincrement=True)
    feeding_date = Column(Date, primary_key=True, server_default=func.current_date())
    pet_id = Column(Integer, nullable=False)
    customer_id = Column(Integer, nullable=False)
    food_type = Column(String(30))
    amount = Column(SmallInteger, nullable=False)
    calories = Column(SmallInteger)
    last_update = Column(DateTime, server_default=func.now())

    # 만약 계속 에러가 난다면, 아래 생성자를 직접 추가해주는 것이 가장 확실합니다.
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)