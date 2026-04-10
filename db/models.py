from sqlalchemy import (
    Column,
    Integer,
    SmallInteger,
    String,
    Text,
    Boolean,
    Date,
    DateTime,
    Time,
    Numeric,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Computed,
    text,
)
from sqlalchemy.orm import declarative_base, relationship, foreign
from sqlalchemy.dialects.postgresql import UUID, INET
from pgvector.sqlalchemy import Vector

Base = declarative_base()

# NOTE
# - This version adds SQLAlchemy ORM relationships on top of the ERD-based models.
# - Relationships backed by real FK constraints use back_populates.
# - A few partition-related tables in the ERD intentionally do not have FK constraints.
#   For those, manual primaryjoin relationships are added as viewonly=True where it is still useful.
# - DB triggers / partitions / DB functions remain DB-level behavior.


class CompanionCustomer(Base):
    __tablename__ = "customer"
    __table_args__ = {"schema": "Companion"}

    customer_id = Column(Integer, primary_key=True)
    is_subscribed = Column(Boolean, nullable=False, server_default=text("false"))
    subs_count = Column(
        SmallInteger, nullable=False, index=True, server_default=text("0")
    )
    permission = Column(SmallInteger, nullable=False, server_default=text("1"))
    active = Column(Boolean, nullable=False, server_default=text("true"))
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    customer_detail = relationship(
        "CompanionCustomerDetail",
        back_populates="customer",
        uselist=False,
        primaryjoin="CompanionCustomer.customer_id == CompanionCustomerDetail.customer_id",
    )
    butlers = relationship("CompanionButler", back_populates="customer")
    pet_log_boolean_entries = relationship(
        "CompanionPetLogBoolean", back_populates="customer"
    )
    pet_log_numeric_entries = relationship(
        "CompanionPetLogNumeric", back_populates="customer"
    )
    pet_food_logs = relationship("CompanionPetFood", back_populates="customer")


class CompanionCustomerDetail(Base):
    __tablename__ = "customer_detail"
    __table_args__ = (
        CheckConstraint(
            "oauth_type in ('google','kakao','naver')",
            name="ck_customer_detail_oauth_type",
        ),
        {"schema": "Companion"},
    )

    customer_id = Column(
        Integer,
        ForeignKey("Companion.customer.customer_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    email = Column(String(255), nullable=False, unique=True, index=True)
    oauth_type = Column(String(6))
    password = Column(String(255))
    nickname = Column(String(10), nullable=False)
    phone = Column(String(13))
    create_date = Column(Date, nullable=False, server_default=text("current_date"))
    last_connect_date = Column(
        Date, nullable=False, server_default=text("current_date")
    )
    memo = Column(Text)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    customer = relationship(
        "CompanionCustomer",
        back_populates="customer_detail",
        primaryjoin="CompanionCustomerDetail.customer_id == CompanionCustomer.customer_id",
    )


class CompanionCustomerFood(Base):
    __tablename__ = "customer_food"
    __table_args__ = {"schema": "Companion"}

    pet_id = Column(
        Integer,
        ForeignKey("Companion.pet.pet_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    total_weight = Column(SmallInteger, nullable=False)
    feeding_start = Column(Date, nullable=False)
    total_intake = Column(SmallInteger, server_default=text("0"))
    food_count = Column(SmallInteger, server_default=text("0"))
    left_food_count = Column(
        Computed(
            "case when total_intake > 0 and food_count > 0 and feeding_start is not null "
            "then (total_weight / (total_intake / food_count::numeric)) - food_count else null end",
            persisted=True,
        )
    )
    left_intake = Column(
        Computed(
            "case when total_intake > 0 and food_count > 0 and total_weight is not null "
            "then total_weight - total_intake else null end",
            persisted=True,
        )
    )
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    pet = relationship("CompanionPet", back_populates="customer_food")


class CompanionButler(Base):
    __tablename__ = "butler"
    __table_args__ = {"schema": "Companion"}

    pet_id = Column(
        Integer, ForeignKey("Companion.pet.pet_id"), primary_key=True, nullable=False
    )
    customer_id = Column(
        Integer,
        ForeignKey("Companion.customer.customer_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    is_main_butler = Column(Boolean, nullable=False, server_default=text("false"))
    butler_date = Column(Date, nullable=False, server_default=text("current_date"))
    active = Column(Boolean, nullable=False, server_default=text("true"))
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    pet = relationship("CompanionPet", back_populates="butlers")
    customer = relationship("CompanionCustomer", back_populates="butlers")


class CompanionPet(Base):
    __tablename__ = "pet"
    __table_args__ = (
        CheckConstraint("sex in (1,2)", name="ck_pet_sex"),
        {"schema": "Companion"},
    )

    pet_id = Column(Integer, primary_key=True)
    nickname = Column(String(10), nullable=False)
    birth_day = Column(Date)
    profile_image = Column(Text)
    breed_id = Column(
        Integer, ForeignKey("Companion.breed.breed_id"), nullable=False, index=True
    )
    sex = Column(SmallInteger, nullable=False, index=True)
    is_neutered = Column(Boolean, nullable=False, index=True)
    weight = Column(Numeric(5, 2), nullable=False)
    bcs = Column(SmallInteger, nullable=False)
    daily_walks = Column(SmallInteger, nullable=False)
    feeding_count = Column(SmallInteger, nullable=False)
    feeding_intake = Column(SmallInteger)
    water_intake = Column(SmallInteger)
    pregnancy = Column(Boolean)
    lactation_count = Column(SmallInteger)
    supps = Column(Text)
    medication = Column(Text)
    allergies = Column(Text)
    diseases = Column(Text)
    active = Column(Boolean, nullable=False, server_default=text("true"))
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    breed = relationship("CompanionBreed", back_populates="pets")
    customer_food = relationship(
        "CompanionCustomerFood", back_populates="pet", uselist=False
    )
    butlers = relationship("CompanionButler", back_populates="pet")
    pet_log_boolean_entries = relationship(
        "CompanionPetLogBoolean", back_populates="pet"
    )
    pet_log_numeric_entries = relationship(
        "CompanionPetLogNumeric", back_populates="pet"
    )
    current_feeding_products = relationship(
        "CompanionPetProductFeeding", back_populates="pet"
    )
    feeding_guides = relationship("CompanionFeedingGuide", back_populates="pet")
    pet_food_logs = relationship("CompanionPetFood", back_populates="pet")


class CompanionPetLogBoolean(Base):
    __tablename__ = "pet_log_boolean"
    __table_args__ = {"schema": "Companion"}

    pet_log_boolean_id = Column(Integer, primary_key=True)
    pet_id = Column(
        Integer, ForeignKey("Companion.pet.pet_id"), nullable=False, index=True
    )
    customer_id = Column(
        Integer,
        ForeignKey("Companion.customer.customer_id"),
        nullable=False,
        index=True,
    )
    category = Column(String(18), nullable=False, index=True)
    is_status = Column(Boolean, nullable=False, server_default=text("true"))
    memo = Column(Text)
    log_date = Column(
        DateTime, primary_key=True, nullable=False, server_default=text("now()")
    )
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    pet = relationship("CompanionPet", back_populates="pet_log_boolean_entries")
    customer = relationship(
        "CompanionCustomer", back_populates="pet_log_boolean_entries"
    )


class CompanionPetLogNumeric(Base):
    __tablename__ = "pet_log_numeric"
    __table_args__ = {"schema": "Companion"}

    pet_log_numeric_id = Column(Integer, primary_key=True)
    pet_id = Column(
        Integer, ForeignKey("Companion.pet.pet_id"), nullable=False, index=True
    )
    customer_id = Column(
        Integer,
        ForeignKey("Companion.customer.customer_id"),
        nullable=False,
        index=True,
    )
    category = Column(String(18), nullable=False, index=True)
    log_status = Column(Numeric(5, 2))
    memo = Column(Text)
    log_date = Column(
        DateTime, primary_key=True, nullable=False, server_default=text("now()")
    )
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    pet = relationship("CompanionPet", back_populates="pet_log_numeric_entries")
    customer = relationship(
        "CompanionCustomer", back_populates="pet_log_numeric_entries"
    )


class CompanionPetProductFeeding(Base):
    __tablename__ = "pet_product_feeding"
    __table_args__ = {"schema": "Companion"}

    pet_id = Column(
        Integer,
        ForeignKey("Companion.pet.pet_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    product_id = Column(
        Integer, ForeignKey("OPD.product.product_id"), nullable=False, index=True
    )
    is_feeding_check = Column(Boolean, nullable=False, server_default=text("true"))
    feeding_false_date = Column(Date)
    record_date = Column(Date, nullable=False, server_default=text("current_date"))
    one_gram_calories = Column(Numeric(4, 2))
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    pet = relationship("CompanionPet", back_populates="current_feeding_products")
    product = relationship("OpdProduct", back_populates="pet_product_feedings")


class CompanionFeedingGuide(Base):
    __tablename__ = "feeding_guide"
    __table_args__ = {"schema": "Companion"}

    pet_id = Column(
        Integer, ForeignKey("Companion.pet.pet_id"), nullable=False, primary_key=True
    )
    base_intake = Column(SmallInteger)
    guide_intake = Column(SmallInteger)
    guide_date = Column(Date, nullable=False, server_default=text("current_date"))

    pet = relationship("CompanionPet", back_populates="feeding_guides")


class CompanionBreed(Base):
    __tablename__ = "breed"
    __table_args__ = (
        CheckConstraint(
            "breed_size in ('XS', 'S', 'M', 'L', 'XL')", name="ck_breed_breed_size"
        ),
        {"schema": "Companion"},
    )

    breed_id = Column(Integer, primary_key=True)
    breed = Column(String(30), nullable=False)
    breed_size = Column(String(2), nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    pets = relationship("CompanionPet", back_populates="breed")


class CompanionPetFood(Base):
    __tablename__ = "pet_food"
    __table_args__ = {"schema": "Companion"}

    pet_food_id = Column(Integer, primary_key=True, autoincrement=True)
    pet_id = Column(
        Integer, ForeignKey("Companion.pet.pet_id"), nullable=False, index=True
    )
    customer_id = Column(
        Integer,
        ForeignKey("Companion.customer.customer_id"),
        nullable=False,
        index=True,
    )
    food_type = Column(String(30), index=True)
    amount = Column(SmallInteger)
    calories = Column(SmallInteger)
    memo = Column(Text)
    feeding_date = Column(
        Date, primary_key=True, nullable=False, server_default=text("current_date")
    )
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    pet = relationship("CompanionPet", back_populates="pet_food_logs")
    customer = relationship("CompanionCustomer", back_populates="pet_food_logs")


class CompanionLifeStage(Base):
    __tablename__ = "life_stage"
    __table_args__ = (
        CheckConstraint(
            "breed_size in ('XS', 'S', 'M', 'L', 'XL')", name="ck_life_stage_breed_size"
        ),
        CheckConstraint(
            "life in ('전연령', '퍼피', '어덜트', '시니어')", name="ck_life_stage_life"
        ),
        {"schema": "Companion"},
    )

    life_id = Column(Integer, primary_key=True)
    breed_size = Column(String(2), nullable=False)
    life = Column(String(6), nullable=False)
    life_start = Column(SmallInteger, nullable=False)
    life_end = Column(SmallInteger, nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))


class ErpEmployee(Base):
    __tablename__ = "employee"
    __table_args__ = {"schema": "ERP"}

    employee_id = Column(Integer, primary_key=True)
    account_id = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    username = Column(String(10), nullable=False)
    hire_date = Column(Date, nullable=False)
    quit_date = Column(Date)
    emp_position_id = Column(
        Integer, ForeignKey("ERP.emp_position.emp_position_id"), index=True
    )
    manager_id = Column(Integer, ForeignKey("ERP.employee.employee_id"), index=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(13), nullable=False)
    address = Column(String(255), nullable=False)
    postal_code = Column(String(5), nullable=False)
    profile_image = Column(Text)
    active = Column(Boolean, nullable=False, server_default=text("true"))
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    emp_position = relationship("ErpEmpPosition", back_populates="employees")
    manager = relationship(
        "ErpEmployee", remote_side=[employee_id], back_populates="subordinates"
    )
    subordinates = relationship("ErpEmployee", back_populates="manager")
    attendances = relationship("ErpAttendance", back_populates="employee")
    erp_connect_logs = relationship("ErpErpConnect", back_populates="employee")
    purchase_orders = relationship("ErpPurchaseOrder", back_populates="employee")
    inbounds = relationship("ErpInbound", back_populates="employee")
    suppliers = relationship("ErpSupplier", back_populates="employee")
    deliveries = relationship("OpdDelivery", back_populates="employee")
    return_orders = relationship("OpdReturnOrder", back_populates="employee")


class ErpEmpPosition(Base):
    __tablename__ = "emp_position"
    __table_args__ = {"schema": "ERP"}

    emp_position_id = Column(Integer, primary_key=True)
    position_name = Column(String(30), nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    employees = relationship("ErpEmployee", back_populates="emp_position")


class ErpAttendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("employee_id", "work_date"),
        {"schema": "ERP"},
    )

    attendance_id = Column(Integer, primary_key=True)
    employee_id = Column(
        Integer, ForeignKey("ERP.employee.employee_id"), nullable=False, index=True
    )
    work_date = Column(Date, nullable=False, server_default=text("current_date"))
    start_time = Column(Time, nullable=False)
    end_time = Column(Time)
    memo = Column(Text)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    employee = relationship("ErpEmployee", back_populates="attendances")


class ErpErpConnect(Base):
    __tablename__ = "erp_connect"
    __table_args__ = {"schema": "ERP"}

    erp_connect_id = Column(Integer, primary_key=True)
    employee_id = Column(
        Integer, ForeignKey("ERP.employee.employee_id"), nullable=False, index=True
    )
    white_list_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ERP.white_list.white_list_id"),
        nullable=False,
        index=True,
    )
    login_date = Column(DateTime, nullable=False, server_default=text("now()"))
    logout_date = Column(DateTime)
    log = Column(Text)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    employee = relationship("ErpEmployee", back_populates="erp_connect_logs")
    white_list = relationship("ErpWhiteList", back_populates="erp_connect_logs")


class ErpWhiteList(Base):
    __tablename__ = "white_list"
    __table_args__ = {"schema": "ERP"}

    white_list_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    ip = Column(INET, nullable=False, unique=True)
    access_location = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("false"))
    create_date = Column(DateTime, nullable=False, server_default=text("now()"))
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    erp_connect_logs = relationship("ErpErpConnect", back_populates="white_list")


class ErpPurchaseOrder(Base):
    __tablename__ = "purchase_order"
    __table_args__ = (
        CheckConstraint(
            "pay_status in ('scheduled', 'completed')",
            name="ck_purchase_order_pay_status",
        ),
        {"schema": "ERP"},
    )

    purchase_order_id = Column(Integer, primary_key=True)
    supplier_id = Column(
        Integer, ForeignKey("ERP.supplier.supplier_id"), nullable=False, index=True
    )
    contract_date = Column(Date, nullable=False)
    inbound_scheduled_date = Column(Date)
    pay_status = Column(String(20), nullable=False, server_default=text("'scheduled'"))
    adjustment_date = Column(DateTime)
    is_purchase_order_cancel = Column(
        Boolean, nullable=False, server_default=text("false")
    )
    employee_id = Column(
        Integer, ForeignKey("ERP.employee.employee_id"), nullable=False, index=True
    )
    order_form_file_path = Column(Text)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    supplier = relationship("ErpSupplier", back_populates="purchase_orders")
    employee = relationship("ErpEmployee", back_populates="purchase_orders")
    items = relationship("ErpPurchaseOrderItem", back_populates="purchase_order")
    inbounds = relationship("ErpInbound", back_populates="purchase_order")


class ErpPurchaseOrderItem(Base):
    __tablename__ = "purchase_order_item"
    __table_args__ = (
        CheckConstraint(
            "storage_method in ('냉동', '냉장', '실온')",
            name="ck_purchase_order_item_storage_method",
        ),
        {"schema": "ERP"},
    )

    purchase_order_id = Column(
        Integer,
        ForeignKey("ERP.purchase_order.purchase_order_id"),
        primary_key=True,
        nullable=False,
    )
    product_id = Column(
        Integer,
        ForeignKey("OPD.product.product_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    storage_method = Column(String(7))
    quantity = Column(Integer, nullable=False)
    purchase_price = Column(Integer, nullable=False)
    total_amount = Column(Computed("quantity * purchase_price", persisted=True))
    defective = Column(Integer, nullable=False, server_default=text("0"))
    final_amount = Column(Integer)
    memo = Column(Text)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    purchase_order = relationship("ErpPurchaseOrder", back_populates="items")
    product = relationship("OpdProduct", back_populates="purchase_order_items")


class ErpInbound(Base):
    __tablename__ = "inbound"
    __table_args__ = {"schema": "ERP"}

    inbound_id = Column(Integer, primary_key=True)
    purchase_order_id = Column(
        Integer,
        ForeignKey("ERP.purchase_order.purchase_order_id"),
        nullable=False,
        index=True,
    )
    inbound_status_id = Column(
        SmallInteger,
        ForeignKey("ERP.inbound_status.inbound_status_id"),
        nullable=False,
        index=True,
        server_default=text("101"),
    )
    inbound_start = Column(DateTime)
    inbound_complete = Column(DateTime)
    employee_id = Column(Integer, ForeignKey("ERP.employee.employee_id"), index=True)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    purchase_order = relationship("ErpPurchaseOrder", back_populates="inbounds")
    inbound_status = relationship("ErpInboundStatus", back_populates="inbounds")
    employee = relationship("ErpEmployee", back_populates="inbounds")
    stocks = relationship("ErpStock", back_populates="inbound")
    subs_items = relationship("OpdSubsItem", back_populates="inbound")
    sales_order_items = relationship("OpdSalesOrderItem", back_populates="inbound")
    return_items = relationship("OpdReturnItem", back_populates="inbound")


class ErpStock(Base):
    __tablename__ = "stock"
    __table_args__ = {"schema": "ERP"}

    product_id = Column(
        Integer, ForeignKey("OPD.product.product_id"), primary_key=True, nullable=False
    )
    inbound_id = Column(
        Integer,
        ForeignKey("ERP.inbound.inbound_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    save_stock = Column(Integer, nullable=False, server_default=text("0"))
    sale_stock = Column(Integer, nullable=False, server_default=text("0"))
    scrap_stock = Column(Integer, nullable=False, server_default=text("0"))
    stock_available = Column(
        Computed("save_stock - sale_stock - scrap_stock", persisted=True)
    )
    expiration_date = Column(Date)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    product = relationship("OpdProduct", back_populates="stocks")
    inbound = relationship("ErpInbound", back_populates="stocks")


class ErpInboundStatus(Base):
    __tablename__ = "inbound_status"
    __table_args__ = {"schema": "ERP"}

    inbound_status_id = Column(SmallInteger, primary_key=True)
    status = Column(String(30), nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    inbounds = relationship("ErpInbound", back_populates="inbound_status")


class ErpSupplier(Base):
    __tablename__ = "supplier"
    __table_args__ = {"schema": "ERP"}

    supplier_id = Column(Integer, primary_key=True)
    supplier_name = Column(String(30), nullable=False)
    brn = Column(String(12), nullable=False)
    is_contact_status = Column(Boolean, nullable=False, server_default=text("true"))
    designated_payment_date = Column(SmallInteger, nullable=False)
    scheduled_payment_date = Column(Date, nullable=False)
    employee_id = Column(
        Integer, ForeignKey("ERP.employee.employee_id"), nullable=False, index=True
    )
    memo = Column(Text)
    sup_manager = Column(String(10), nullable=False)
    phone = Column(String(13), nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    employee = relationship("ErpEmployee", back_populates="suppliers")
    purchase_orders = relationship("ErpPurchaseOrder", back_populates="supplier")


class OpdCustomer(Base):
    __tablename__ = "customer"
    __table_args__ = {"schema": "OPD"}

    customer_id = Column(Integer, primary_key=True)
    is_subscribed = Column(Boolean, nullable=False, server_default=text("false"))
    subs_count = Column(
        SmallInteger, nullable=False, index=True, server_default=text("0")
    )
    permission = Column(SmallInteger, nullable=False, server_default=text("1"))
    active = Column(Boolean, nullable=False, server_default=text("true"))
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    customer_detail = relationship(
        "OpdCustomerDetail", back_populates="customer", uselist=False
    )
    payment_billings = relationship("OpdPaymentBilling", back_populates="customer")
    subscriptions = relationship("OpdSubs", back_populates="customer")
    wishlists = relationship("OpdWishlist", back_populates="customer")
    carts = relationship("OpdCart", back_populates="customer")
    sales_orders = relationship("OpdSalesOrder", back_populates="customer")


class OpdCustomerDetail(Base):
    __tablename__ = "customer_detail"
    __table_args__ = (
        CheckConstraint(
            "oauth_type in ('google','kakao','naver')",
            name="ck_customer_detail_oauth_type",
        ),
        {"schema": "OPD"},
    )

    customer_id = Column(
        Integer,
        ForeignKey("OPD.customer.customer_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    email = Column(String(255), nullable=False, unique=True)
    oauth_type = Column(String(6))
    oauth_token = Column(String(255))
    password = Column(String(255))
    nickname = Column(String(10), nullable=False)
    phone = Column(String(13))
    create_date = Column(Date, nullable=False, server_default=text("current_date"))
    last_connect_date = Column(
        Date, nullable=False, server_default=text("current_date")
    )
    memo = Column(Text)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    customer = relationship("OpdCustomer", back_populates="customer_detail")


class OpdFinancialCompany(Base):
    __tablename__ = "financial_company"
    __table_args__ = {"schema": "OPD"}

    financial_company_id = Column(Integer, primary_key=True)
    company = Column(String(30), nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    payment_billings = relationship(
        "OpdPaymentBilling", back_populates="financial_company"
    )


class OpdPaymentBilling(Base):
    __tablename__ = "payment_billing"
    __table_args__ = (
        UniqueConstraint("customer_id", "financial_company_id"),
        {"schema": "OPD"},
    )

    payment_billing_id = Column(Integer, primary_key=True)
    customer_id = Column(
        Integer, ForeignKey("OPD.customer.customer_id"), nullable=False, index=True
    )
    financial_company_id = Column(
        Integer,
        ForeignKey("OPD.financial_company.financial_company_id"),
        nullable=False,
        index=True,
    )
    billing_key_name = Column(String(10))
    billing_key = Column(String(255), nullable=False, unique=True)
    is_default_card = Column(Boolean, nullable=False, server_default=text("false"))
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    customer = relationship("OpdCustomer", back_populates="payment_billings")
    financial_company = relationship(
        "OpdFinancialCompany", back_populates="payment_billings"
    )
    subs_details = relationship("OpdSubsDetail", back_populates="payment_billing")
    sales_orders = relationship("OpdSalesOrder", back_populates="payment_billing")


class OpdProduct(Base):
    __tablename__ = "product"
    __table_args__ = {"schema": "OPD"}

    product_id = Column(Integer, primary_key=True)
    product_detail_id = Column(
        Integer,
        ForeignKey("OPD.product_detail.product_detail_id"),
        nullable=False,
        index=True,
    )
    quantity = Column(SmallInteger, nullable=False)
    retail_price = Column(Integer, nullable=False)
    weight = Column(SmallInteger, nullable=False)
    is_sample = Column(Boolean, nullable=False, server_default=text("false"))
    active = Column(Boolean, nullable=False, server_default=text("true"))
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    product_detail = relationship("OpdProductDetail", back_populates="products")
    pet_product_feedings = relationship(
        "CompanionPetProductFeeding", back_populates="product"
    )
    purchase_order_items = relationship(
        "ErpPurchaseOrderItem", back_populates="product"
    )
    stocks = relationship("ErpStock", back_populates="product")
    subs_items = relationship("OpdSubsItem", back_populates="product")
    wishlists = relationship("OpdWishlist", back_populates="product")
    carts = relationship("OpdCart", back_populates="product")
    sales_order_items = relationship("OpdSalesOrderItem", back_populates="product")
    return_items = relationship("OpdReturnItem", back_populates="product")


class OpdProductDetail(Base):
    __tablename__ = "product_detail"
    __table_args__ = (
        CheckConstraint(
            "life in ('전연령', '퍼피', '어덜트', '시니어')",
            name="ck_product_detail_life",
        ),
        {"schema": "OPD"},
    )

    product_detail_id = Column(Integer, primary_key=True)
    type = Column(String(9), nullable=False)
    brand = Column(String(255), nullable=False)
    product_name = Column(Text, nullable=False)
    function = Column(Text)
    description = Column(Text)
    crude_protein = Column(Numeric(4, 2))
    crude_fat = Column(Numeric(4, 2))
    calories = Column(Numeric(4, 2))
    thumbnail = Column(Text)
    pdi = Column(Text)
    # vector_embed = Column(Vector(384))
    kibble_size = Column(String(20))
    life = Column(String(6), nullable=False)
    protein_type = Column(String(9))
    main_protein = Column(String(30))
    certified = Column(String(30))
    preservative = Column(String(30))
    feedshape = Column(String(20))
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    products = relationship("OpdProduct", back_populates="product_detail")


class OpdSubsPlan(Base):
    __tablename__ = "subs_plan"
    __table_args__ = {"schema": "OPD"}

    subs_plan_id = Column(Integer, primary_key=True)
    delivery_cycle = Column(SmallInteger, nullable=False, server_default=text("1"))
    subs_sale = Column(Numeric(2, 1), nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    subscriptions = relationship("OpdSubs", back_populates="subs_plan")


class OpdSubs(Base):
    __tablename__ = "subs"
    __table_args__ = {"schema": "OPD"}

    subs_id = Column(Integer, primary_key=True)
    customer_id = Column(
        Integer, ForeignKey("OPD.customer.customer_id"), nullable=False, index=True
    )
    subs_plan_id = Column(
        Integer, ForeignKey("OPD.subs_plan.subs_plan_id"), nullable=False, index=True
    )
    subs_date = Column(
        DateTime, primary_key=True, nullable=False, server_default=text("now()")
    )
    is_auto_delivery = Column(Boolean, nullable=False, server_default=text("false"))
    is_subs_status = Column(
        Boolean, nullable=False, index=True, server_default=text("true")
    )
    subs_day = Column(
        String(10),
        nullable=False,
        server_default=text(
            "case when to_char(now(),'fmday') in ('saturday','sunday') then 'monday' else to_char(now(),'fmday') end"
        ),
    )
    cancel_reason = Column(Text)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    customer = relationship("OpdCustomer", back_populates="subscriptions")
    subs_plan = relationship("OpdSubsPlan", back_populates="subscriptions")
    subs_detail = relationship(
        "OpdSubsDetail",
        primaryjoin="OpdSubs.subs_id == foreign(OpdSubsDetail.subs_id)",
        back_populates="subscription",
        uselist=False,
        viewonly=True,
    )
    items = relationship(
        "OpdSubsItem",
        primaryjoin="OpdSubs.subs_id == foreign(OpdSubsItem.subs_id)",
        back_populates="subscription",
        viewonly=True,
    )
    payments = relationship(
        "OpdPayment",
        primaryjoin="OpdSubs.subs_id == foreign(OpdPayment.subs_id)",
        back_populates="subscription",
        viewonly=True,
    )
    deliveries = relationship(
        "OpdDelivery",
        primaryjoin="OpdSubs.subs_id == foreign(OpdDelivery.subs_id)",
        back_populates="subscription",
        viewonly=True,
    )
    return_orders = relationship(
        "OpdReturnOrder",
        primaryjoin="OpdSubs.subs_id == foreign(OpdReturnOrder.subs_id)",
        back_populates="subscription",
        viewonly=True,
    )


class OpdSubsDetail(Base):
    __tablename__ = "subs_detail"
    __table_args__ = {"schema": "OPD"}

    subs_id = Column(Integer, primary_key=True, nullable=False, index=True)
    payment_billing_id = Column(
        Integer, ForeignKey("OPD.payment_billing.payment_billing_id"), nullable=False
    )
    address = Column(String(255), nullable=False)
    detail_address = Column(String(255), nullable=False)
    postal_code = Column(String(5), nullable=False)
    memo = Column(Text)
    name = Column(String(10), nullable=False)
    phone = Column(String(13), nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    payment_billing = relationship("OpdPaymentBilling", back_populates="subs_details")
    subscription = relationship(
        "OpdSubs",
        primaryjoin="foreign(OpdSubsDetail.subs_id) == OpdSubs.subs_id",
        back_populates="subs_detail",
        viewonly=True,
    )


class OpdSubsItem(Base):
    __tablename__ = "subs_item"
    __table_args__ = {"schema": "OPD"}

    subs_id = Column(Integer, primary_key=True, nullable=False)
    inbound_id = Column(
        Integer,
        ForeignKey("ERP.inbound.inbound_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    product_id = Column(
        Integer, ForeignKey("OPD.product.product_id"), nullable=False, index=True
    )
    quantity = Column(SmallInteger, nullable=False)
    retail_price = Column(Integer, nullable=False)
    total_amount = Column(Integer, nullable=False)
    final_amount = Column(Integer, nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    inbound = relationship("ErpInbound", back_populates="subs_items")
    product = relationship("OpdProduct", back_populates="subs_items")
    subscription = relationship(
        "OpdSubs",
        primaryjoin="foreign(OpdSubsItem.subs_id) == OpdSubs.subs_id",
        back_populates="items",
        viewonly=True,
    )


class OpdWishlist(Base):
    __tablename__ = "wishlist"
    __table_args__ = {"schema": "OPD"}

    customer_id = Column(
        Integer,
        ForeignKey("OPD.customer.customer_id"),
        primary_key=True,
        nullable=False,
    )
    product_id = Column(
        Integer,
        ForeignKey("OPD.product.product_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    customer = relationship("OpdCustomer", back_populates="wishlists")
    product = relationship("OpdProduct", back_populates="wishlists")


class OpdCart(Base):
    __tablename__ = "cart"
    __table_args__ = {"schema": "OPD"}

    customer_id = Column(
        Integer,
        ForeignKey("OPD.customer.customer_id"),
        primary_key=True,
        nullable=False,
    )
    product_id = Column(
        Integer,
        ForeignKey("OPD.product.product_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    quantity = Column(SmallInteger, nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    customer = relationship("OpdCustomer", back_populates="carts")
    product = relationship("OpdProduct", back_populates="carts")


class OpdSalesOrder(Base):
    __tablename__ = "sales_order"
    __table_args__ = {"schema": "OPD"}

    sales_order_id = Column(Integer, primary_key=True)
    order_number = Column(
        String(12), nullable=False, server_default=text("unique_number()")
    )
    order_date = Column(
        DateTime, primary_key=True, nullable=False, server_default=text("now()")
    )
    address = Column(String(255), nullable=False)
    detail_address = Column(String(255), nullable=False)
    postal_code = Column(String(5), nullable=False)
    customer_id = Column(
        Integer, ForeignKey("OPD.customer.customer_id"), nullable=False, index=True
    )
    memo = Column(Text)
    recipient = Column(String(10), nullable=False)
    phone = Column(String(13), nullable=False)
    payment_billing_id = Column(
        Integer, ForeignKey("OPD.payment_billing.payment_billing_id")
    )
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    customer = relationship("OpdCustomer", back_populates="sales_orders")
    payment_billing = relationship("OpdPaymentBilling", back_populates="sales_orders")
    items = relationship(
        "OpdSalesOrderItem",
        primaryjoin="OpdSalesOrder.sales_order_id == foreign(OpdSalesOrderItem.sales_order_id)",
        back_populates="sales_order",
        viewonly=True,
    )
    payments = relationship(
        "OpdPayment",
        primaryjoin="OpdSalesOrder.sales_order_id == foreign(OpdPayment.sales_order_id)",
        back_populates="sales_order",
        viewonly=True,
    )
    deliveries = relationship(
        "OpdDelivery",
        primaryjoin="OpdSalesOrder.sales_order_id == foreign(OpdDelivery.sales_order_id)",
        back_populates="sales_order",
        viewonly=True,
    )
    return_orders = relationship(
        "OpdReturnOrder",
        primaryjoin="OpdSalesOrder.sales_order_id == foreign(OpdReturnOrder.sales_order_id)",
        back_populates="sales_order",
        viewonly=True,
    )


class OpdSalesOrderItem(Base):
    __tablename__ = "sales_order_item"
    __table_args__ = {"schema": "OPD"}

    sales_order_id = Column(Integer, primary_key=True, nullable=False)
    inbound_id = Column(
        Integer,
        ForeignKey("ERP.inbound.inbound_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    product_id = Column(
        Integer,
        ForeignKey("OPD.product.product_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    quantity = Column(SmallInteger, nullable=False)
    retail_price = Column(Integer, nullable=False)
    total_amount = Column(Integer, nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    inbound = relationship("ErpInbound", back_populates="sales_order_items")
    product = relationship("OpdProduct", back_populates="sales_order_items")
    sales_order = relationship(
        "OpdSalesOrder",
        primaryjoin="foreign(OpdSalesOrderItem.sales_order_id) == OpdSalesOrder.sales_order_id",
        back_populates="items",
        viewonly=True,
    )


class OpdPayment(Base):
    __tablename__ = "payment"
    __table_args__ = {"schema": "OPD"}

    payment_id = Column(Integer, primary_key=True)
    sales_order_id = Column(Integer, index=True)
    subs_id = Column(Integer, index=True)
    payment_status_id = Column(
        SmallInteger,
        ForeignKey("OPD.payment_status.payment_status_id"),
        nullable=False,
        index=True,
        server_default=text("101"),
    )
    pay_number = Column(
        String(12), nullable=False, server_default=text("unique_number()")
    )
    payment_date = Column(
        DateTime, primary_key=True, nullable=False, server_default=text("now()")
    )
    amount = Column(Integer, nullable=False)
    payment_plan = Column(SmallInteger)
    method = Column(String(15), nullable=False, index=True)
    is_cancel = Column(
        Boolean, nullable=False, index=True, server_default=text("false")
    )
    cancel_date = Column(DateTime)
    cancel_amount = Column(Integer)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    payment_status = relationship("OpdPaymentStatus", back_populates="payments")
    sales_order = relationship(
        "OpdSalesOrder",
        primaryjoin="foreign(OpdPayment.sales_order_id) == OpdSalesOrder.sales_order_id",
        back_populates="payments",
        viewonly=True,
    )
    subscription = relationship(
        "OpdSubs",
        primaryjoin="foreign(OpdPayment.subs_id) == OpdSubs.subs_id",
        back_populates="payments",
        viewonly=True,
    )


class OpdPaymentStatus(Base):
    __tablename__ = "payment_status"
    __table_args__ = {"schema": "OPD"}

    payment_status_id = Column(SmallInteger, primary_key=True)
    status = Column(String(30), nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    payments = relationship("OpdPayment", back_populates="payment_status")


class OpdDelivery(Base):
    __tablename__ = "delivery"
    __table_args__ = {"schema": "OPD"}

    delivery_id = Column(Integer, primary_key=True)
    delivery_status_id = Column(
        SmallInteger,
        ForeignKey("OPD.delivery_status.delivery_status_id"),
        nullable=False,
        index=True,
        server_default=text("101"),
    )
    sales_order_id = Column(Integer, index=True)
    subs_id = Column(Integer, index=True)
    employee_id = Column(Integer, ForeignKey("ERP.employee.employee_id"), index=True)
    insert_delivery_date = Column(
        DateTime, primary_key=True, nullable=False, server_default=text("now()")
    )
    order_start_date = Column(DateTime)
    invoice = Column(String(20))
    order_complete_date = Column(DateTime)
    delivery_date = Column(DateTime)
    delivery_complete_date = Column(DateTime)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    delivery_status = relationship("OpdDeliveryStatus", back_populates="deliveries")
    employee = relationship("ErpEmployee", back_populates="deliveries")
    sales_order = relationship(
        "OpdSalesOrder",
        primaryjoin="foreign(OpdDelivery.sales_order_id) == OpdSalesOrder.sales_order_id",
        back_populates="deliveries",
        viewonly=True,
    )
    subscription = relationship(
        "OpdSubs",
        primaryjoin="foreign(OpdDelivery.subs_id) == OpdSubs.subs_id",
        back_populates="deliveries",
        viewonly=True,
    )


class OpdReturnOrder(Base):
    __tablename__ = "return_order"
    __table_args__ = {"schema": "OPD"}

    return_order_id = Column(Integer, primary_key=True)
    delivery_status_id = Column(
        SmallInteger,
        ForeignKey("OPD.delivery_status.delivery_status_id"),
        nullable=False,
        index=True,
        server_default=text("401"),
    )
    sales_order_id = Column(Integer, index=True)
    subs_id = Column(Integer, index=True)
    employee_id = Column(Integer, ForeignKey("ERP.employee.employee_id"), index=True)
    insert_return_date = Column(
        DateTime, primary_key=True, nullable=False, server_default=text("now()")
    )
    invoice = Column(String(20))
    return_product_date = Column(DateTime)
    inspect_product_start = Column(DateTime)
    inspect_product_end = Column(DateTime)
    is_not_inspect = Column(Boolean, nullable=False, server_default=text("false"))
    memo = Column(Text)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    delivery_status = relationship("OpdDeliveryStatus", back_populates="return_orders")
    employee = relationship("ErpEmployee", back_populates="return_orders")
    items = relationship(
        "OpdReturnItem",
        primaryjoin="OpdReturnOrder.return_order_id == foreign(OpdReturnItem.return_order_id)",
        back_populates="return_order",
        viewonly=True,
    )
    sales_order = relationship(
        "OpdSalesOrder",
        primaryjoin="foreign(OpdReturnOrder.sales_order_id) == OpdSalesOrder.sales_order_id",
        back_populates="return_orders",
        viewonly=True,
    )
    subscription = relationship(
        "OpdSubs",
        primaryjoin="foreign(OpdReturnOrder.subs_id) == OpdSubs.subs_id",
        back_populates="return_orders",
        viewonly=True,
    )


class OpdReturnItem(Base):
    __tablename__ = "return_item"
    __table_args__ = {"schema": "OPD"}

    return_order_id = Column(Integer, primary_key=True, nullable=False)
    inbound_id = Column(
        Integer,
        ForeignKey("ERP.inbound.inbound_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    product_id = Column(
        Integer,
        ForeignKey("OPD.product.product_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    quantity = Column(SmallInteger, nullable=False)
    memo = Column(Text, nullable=False)
    non_refundable = Column(SmallInteger, nullable=False, server_default=text("0"))
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    inbound = relationship("ErpInbound", back_populates="return_items")
    product = relationship("OpdProduct", back_populates="return_items")
    return_order = relationship(
        "OpdReturnOrder",
        primaryjoin="foreign(OpdReturnItem.return_order_id) == OpdReturnOrder.return_order_id",
        back_populates="items",
        viewonly=True,
    )


class OpdDeliveryStatus(Base):
    __tablename__ = "delivery_status"
    __table_args__ = {"schema": "OPD"}

    delivery_status_id = Column(SmallInteger, primary_key=True)
    status = Column(String(30), nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=text("now()"))

    deliveries = relationship("OpdDelivery", back_populates="delivery_status")
    return_orders = relationship("OpdReturnOrder", back_populates="delivery_status")
