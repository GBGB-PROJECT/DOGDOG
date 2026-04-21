class Breed:
    #############################################
    # pet breed
    #############################################

    # =========================================================
    # ☑️ 품종 전체 조회
    # - breed 테이블에서 breed_id, breed 컬럼 조회
    # =========================================================
    breed_list_query\
        = """
        SELECT breed_id, breed
        FROM "Companion".breed
        -- ORDER BY breed ASC
        """

    # =========================================================
    # ☑️ 품종 검색 조회
    # - 입력한 검색어(%s)를 breed 컬럼에 LIKE 검색
    # =========================================================
    breed_search_query\
        = """
        SELECT breed_id, breed
        FROM "Companion".breed
        WHERE LOWER(breed) LIKE LOWER(%s)
        ORDER BY breed ASC
        """


class Product:
    #############################################
    # pet product
    #############################################

    # =========================================================
    # ☑️ 상품명 목록 조회
    # - product_detail 테이블에서 상품 id, 상품명만 조회
    # =========================================================
    product_list_query\
        = """
        SELECT product_detail_id, product_name
        FROM "OPD".product_detail
        ORDER BY product_name ASC
        """

    # =========================================================
    # ☑️ 상품명 검색 조회
    # - 입력한 검색어(%s)를 상품명에 LIKE 검색
    # =========================================================
    product_search_query\
        = """
        SELECT product_detail_id, product_name
        FROM "OPD".product_detail
        WHERE LOWER(product_name) LIKE LOWER(%s)
        ORDER BY product_name ASC
        """

    # =========================================================
    # ☑️ 상품 중량 목록 조회
    # - product 테이블에서 특정 product_detail_id에 연결된
    #   활성(active = TRUE) 상품의 weight 목록을 조회
    # =========================================================
    product_weight_list\
        = """
        SELECT product_id, weight
        FROM "OPD".product
        WHERE product_detail_id = %s
        AND active IS TRUE
        ORDER BY weight ASC
        """


class ProductDetail:
    #############################################
    # product detail
    #############################################

    # =========================================================
    # ☑️ 상품 상세 전체 조회
    # =========================================================
    list_query\
        = """
        SELECT
            product_detail_id,
            type,
            brand,
            product_name,
            function,
            description,
            crude_protein,
            crude_fat,
            calories,
            thumbnail,
            kibble_size,
            life,
            protein_type,
            main_protein,
            certified,
            preservative,
            feedshape,
            last_update
        FROM "OPD".product_detail
        ORDER BY product_name ASC
        """

    # =========================================================
    # ☑️ 상품 상세 검색 조회
    # =========================================================
    search_query\
        = """
        SELECT
            product_detail_id,
            type,
            brand,
            product_name,
            function,
            description,
            crude_protein,
            crude_fat,
            calories,
            thumbnail,
            kibble_size,
            life,
            protein_type,
            main_protein,
            certified,
            preservative,
            feedshape,
            last_update
        FROM "OPD".product_detail
        WHERE
            LOWER(product_name) LIKE LOWER(%s)
            OR LOWER(COALESCE(brand, '')) LIKE LOWER(%s)
            OR LOWER(COALESCE(type, '')) LIKE LOWER(%s)
            OR LOWER(COALESCE(function, '')) LIKE LOWER(%s)
            OR LOWER(COALESCE(main_protein, '')) LIKE LOWER(%s)
        ORDER BY product_name ASC
        """


class Employee:
    #############################################
    # employee
    #############################################

    list_query\
        = """
        SELECT
            employee_id,
            account_id,
            username,
            hire_date,
            quit_date,
            emp_position_id,
            manager_id,
            email,
            phone,
            address,
            postal_code,
            active
        FROM "ERP".employee
        ORDER BY employee_id ASC
        """

    search_query\
        = """
        SELECT
            employee_id,
            account_id,
            username,
            hire_date,
            quit_date,
            emp_position_id,
            manager_id,
            email,
            phone,
            address,
            postal_code,
            active
        FROM "ERP".employee
        WHERE
            LOWER(COALESCE(username, '')) LIKE LOWER(%s)
            OR CAST(employee_id AS TEXT) LIKE %s
            OR LOWER(COALESCE(account_id, '')) LIKE LOWER(%s)
            OR CAST(emp_position_id AS TEXT) LIKE %s
            OR LOWER(COALESCE(phone, '')) LIKE LOWER(%s)
            OR LOWER(COALESCE(email, '')) LIKE LOWER(%s)
        ORDER BY employee_id ASC
        """


class Customer:
    #############################################
    # customer
    #############################################

    # =========================================================
    # ☑️ 고객 전체 개수 조회
    # =========================================================
    count_query\
        = """
        SELECT COUNT(*) AS total_count
        FROM "Companion".customer
        """

    # =========================================================
    # ☑️ 고객 전체 조회
    # =========================================================
    list_query\
        = """
        SELECT
            customer_id,
            is_subscribed,
            subs_count,
            permission,
            active,
            last_update
        FROM "Companion".customer
        ORDER BY customer_id ASC
        """

    # =========================================================
    # ☑️ 고객ID 검색 개수 조회
    # =========================================================
    search_customer_id_count_query\
        = """
        SELECT COUNT(*) AS total_count
        FROM "Companion".customer
        WHERE CAST(customer_id AS TEXT) LIKE %s
        """

    # =========================================================
    # ☑️ 고객ID 검색 조회
    # =========================================================
    search_customer_id_query\
        = """
        SELECT
            customer_id,
            is_subscribed,
            subs_count,
            permission,
            active,
            last_update
        FROM "Companion".customer
        WHERE CAST(customer_id AS TEXT) LIKE %s
        ORDER BY customer_id ASC
        """

    # =========================================================
    # ☑️ 구독여부 검색 개수 조회
    # =========================================================
    search_is_subscribed_count_query\
        = """
        SELECT COUNT(*) AS total_count
        FROM "Companion".customer
        WHERE LOWER(CAST(is_subscribed AS TEXT)) LIKE LOWER(%s)
        """

    # =========================================================
    # ☑️ 구독여부 검색 조회
    # =========================================================
    search_is_subscribed_query\
        = """
        SELECT
            customer_id,
            is_subscribed,
            subs_count,
            permission,
            active,
            last_update
        FROM "Companion".customer
        WHERE LOWER(CAST(is_subscribed AS TEXT)) LIKE LOWER(%s)
        ORDER BY customer_id ASC
        """

    # =========================================================
    # ☑️ 구독횟수 검색 개수 조회
    # =========================================================
    search_subs_count_count_query\
        = """
        SELECT COUNT(*) AS total_count
        FROM "Companion".customer
        WHERE CAST(subs_count AS TEXT) LIKE %s
        """

    # =========================================================
    # ☑️ 구독횟수 검색 조회
    # =========================================================
    search_subs_count_query\
        = """
        SELECT
            customer_id,
            is_subscribed,
            subs_count,
            permission,
            active,
            last_update
        FROM "Companion".customer
        WHERE CAST(subs_count AS TEXT) LIKE %s
        ORDER BY customer_id ASC
        """

    # =========================================================
    # ☑️ 권한 검색 개수 조회
    # =========================================================
    search_permission_count_query\
        = """
        SELECT COUNT(*) AS total_count
        FROM "Companion".customer
        WHERE CAST(permission AS TEXT) LIKE %s
        """

    # =========================================================
    # ☑️ 권한 검색 조회
    # =========================================================
    search_permission_query\
        = """
        SELECT
            customer_id,
            is_subscribed,
            subs_count,
            permission,
            active,
            last_update
        FROM "Companion".customer
        WHERE CAST(permission AS TEXT) LIKE %s
        ORDER BY customer_id ASC
        """

    # =========================================================
    # ☑️ 상태 검색 개수 조회
    # =========================================================
    search_active_count_query\
        = """
        SELECT COUNT(*) AS total_count
        FROM "Companion".customer
        WHERE LOWER(CAST(active AS TEXT)) LIKE LOWER(%s)
        """

    # =========================================================
    # ☑️ 상태 검색 조회
    # =========================================================
    search_active_query\
        = """
        SELECT
            customer_id,
            is_subscribed,
            subs_count,
            permission,
            active,
            last_update
        FROM "Companion".customer
        WHERE LOWER(CAST(active AS TEXT)) LIKE LOWER(%s)
        ORDER BY customer_id ASC
        """
    
class Supplier:
    #############################################
    # supplier
    #############################################

    count_query\
        = """
        SELECT COUNT(*) AS total_count
        FROM "ERP".supplier
        """

    list_query\
        = """
        SELECT
            supplier_id,
            supplier_name,
            brn,
            is_contact_status,
            designated_payment_date,
            scheduled_payment_date,
            employee_id,
            memo,
            sup_manager,
            phone,
            last_update
        FROM "ERP".supplier
        ORDER BY supplier_id ASC
        """

    search_supplier_id_count_query\
        = """
        SELECT COUNT(*) AS total_count
        FROM "ERP".supplier
        WHERE CAST(supplier_id AS TEXT) LIKE %s
        """

    search_supplier_id_query\
        = """
        SELECT
            supplier_id,
            supplier_name,
            brn,
            is_contact_status,
            designated_payment_date,
            scheduled_payment_date,
            employee_id,
            memo,
            sup_manager,
            phone,
            last_update
        FROM "ERP".supplier
        WHERE CAST(supplier_id AS TEXT) LIKE %s
        ORDER BY supplier_id ASC
        """

    search_supplier_name_count_query\
        = """
        SELECT COUNT(*) AS total_count
        FROM "ERP".supplier
        WHERE LOWER(COALESCE(supplier_name, '')) LIKE LOWER(%s)
        """

    search_supplier_name_query\
        = """
        SELECT
            supplier_id,
            supplier_name,
            brn,
            is_contact_status,
            designated_payment_date,
            scheduled_payment_date,
            employee_id,
            memo,
            sup_manager,
            phone,
            last_update
        FROM "ERP".supplier
        WHERE LOWER(COALESCE(supplier_name, '')) LIKE LOWER(%s)
        ORDER BY supplier_id ASC
        """

    search_brn_count_query\
        = """
        SELECT COUNT(*) AS total_count
        FROM "ERP".supplier
        WHERE LOWER(COALESCE(brn, '')) LIKE LOWER(%s)
        """

    search_brn_query\
        = """
        SELECT
            supplier_id,
            supplier_name,
            brn,
            is_contact_status,
            designated_payment_date,
            scheduled_payment_date,
            employee_id,
            memo,
            sup_manager,
            phone,
            last_update
        FROM "ERP".supplier
        WHERE LOWER(COALESCE(brn, '')) LIKE LOWER(%s)
        ORDER BY supplier_id ASC
        """

    search_is_contact_status_count_query\
        = """
        SELECT COUNT(*) AS total_count
        FROM "ERP".supplier
        WHERE LOWER(CAST(is_contact_status AS TEXT)) LIKE LOWER(%s)
        """

    search_is_contact_status_query\
        = """
        SELECT
            supplier_id,
            supplier_name,
            brn,
            is_contact_status,
            designated_payment_date,
            scheduled_payment_date,
            employee_id,
            memo,
            sup_manager,
            phone,
            last_update
        FROM "ERP".supplier
        WHERE LOWER(CAST(is_contact_status AS TEXT)) LIKE LOWER(%s)
        ORDER BY supplier_id ASC
        """

    search_sup_manager_count_query\
        = """
        SELECT COUNT(*) AS total_count
        FROM "ERP".supplier
        WHERE LOWER(COALESCE(sup_manager, '')) LIKE LOWER(%s)
        """

    search_sup_manager_query\
        = """
        SELECT
            supplier_id,
            supplier_name,
            brn,
            is_contact_status,
            designated_payment_date,
            scheduled_payment_date,
            employee_id,
            memo,
            sup_manager,
            phone,
            last_update
        FROM "ERP".supplier
        WHERE LOWER(COALESCE(sup_manager, '')) LIKE LOWER(%s)
        ORDER BY supplier_id ASC
        """

    search_phone_count_query\
        = """
        SELECT COUNT(*) AS total_count
        FROM "ERP".supplier
        WHERE LOWER(COALESCE(phone, '')) LIKE LOWER(%s)
        """

    search_phone_query\
        = """
        SELECT
            supplier_id,
            supplier_name,
            brn,
            is_contact_status,
            designated_payment_date,
            scheduled_payment_date,
            employee_id,
            memo,
            sup_manager,
            phone,
            last_update
        FROM "ERP".supplier
        WHERE LOWER(COALESCE(phone, '')) LIKE LOWER(%s)
        ORDER BY supplier_id ASC
        """


# =========================================================
# ☑️ 추가/수정: DB 직접 페이지네이션 조회용 쿼리
# - 기존 쿼리는 최대한 보존하고, 관리화면에서 필요한 count/search 쿼리만 추가함
# - 화면에서 LIMIT / OFFSET을 붙여서 50개씩 조회할 수 있게 구성
# =========================================================

# =========================================================
# ☑️ 추가: 상품 상세 전체 개수 조회
# =========================================================
ProductDetail.count_query = """
SELECT COUNT(*) AS total_count
FROM "OPD".product_detail
"""

# =========================================================
# ☑️ 추가: 상품 상세 검색 개수/조회 쿼리
# - 화면 검색조건별로 DB에서 바로 필터링하기 위한 쿼리
# =========================================================
ProductDetail.search_product_name_count_query = """
SELECT COUNT(*) AS total_count
FROM "OPD".product_detail
WHERE LOWER(COALESCE(product_name, '')) LIKE LOWER(%s)
"""

ProductDetail.search_product_name_query = """
SELECT
    product_detail_id,
    type,
    brand,
    product_name,
    function,
    description,
    crude_protein,
    crude_fat,
    calories,
    thumbnail,
    kibble_size,
    life,
    protein_type,
    main_protein,
    certified,
    preservative,
    feedshape,
    last_update
FROM "OPD".product_detail
WHERE LOWER(COALESCE(product_name, '')) LIKE LOWER(%s)
ORDER BY product_name ASC
"""

ProductDetail.search_type_count_query = """
SELECT COUNT(*) AS total_count
FROM "OPD".product_detail
WHERE LOWER(COALESCE(type, '')) LIKE LOWER(%s)
"""

ProductDetail.search_type_query = """
SELECT
    product_detail_id,
    type,
    brand,
    product_name,
    function,
    description,
    crude_protein,
    crude_fat,
    calories,
    thumbnail,
    kibble_size,
    life,
    protein_type,
    main_protein,
    certified,
    preservative,
    feedshape,
    last_update
FROM "OPD".product_detail
WHERE LOWER(COALESCE(type, '')) LIKE LOWER(%s)
ORDER BY product_name ASC
"""

ProductDetail.search_brand_count_query = """
SELECT COUNT(*) AS total_count
FROM "OPD".product_detail
WHERE LOWER(COALESCE(brand, '')) LIKE LOWER(%s)
"""

ProductDetail.search_brand_query = """
SELECT
    product_detail_id,
    type,
    brand,
    product_name,
    function,
    description,
    crude_protein,
    crude_fat,
    calories,
    thumbnail,
    kibble_size,
    life,
    protein_type,
    main_protein,
    certified,
    preservative,
    feedshape,
    last_update
FROM "OPD".product_detail
WHERE LOWER(COALESCE(brand, '')) LIKE LOWER(%s)
ORDER BY product_name ASC
"""

ProductDetail.search_function_count_query = """
SELECT COUNT(*) AS total_count
FROM "OPD".product_detail
WHERE LOWER(COALESCE(function, '')) LIKE LOWER(%s)
"""

ProductDetail.search_function_query = """
SELECT
    product_detail_id,
    type,
    brand,
    product_name,
    function,
    description,
    crude_protein,
    crude_fat,
    calories,
    thumbnail,
    kibble_size,
    life,
    protein_type,
    main_protein,
    certified,
    preservative,
    feedshape,
    last_update
FROM "OPD".product_detail
WHERE LOWER(COALESCE(function, '')) LIKE LOWER(%s)
ORDER BY product_name ASC
"""

ProductDetail.search_life_count_query = """
SELECT COUNT(*) AS total_count
FROM "OPD".product_detail
WHERE LOWER(COALESCE(life, '')) LIKE LOWER(%s)
"""

ProductDetail.search_life_query = """
SELECT
    product_detail_id,
    type,
    brand,
    product_name,
    function,
    description,
    crude_protein,
    crude_fat,
    calories,
    thumbnail,
    kibble_size,
    life,
    protein_type,
    main_protein,
    certified,
    preservative,
    feedshape,
    last_update
FROM "OPD".product_detail
WHERE LOWER(COALESCE(life, '')) LIKE LOWER(%s)
ORDER BY product_name ASC
"""

ProductDetail.search_main_protein_count_query = """
SELECT COUNT(*) AS total_count
FROM "OPD".product_detail
WHERE LOWER(COALESCE(main_protein, '')) LIKE LOWER(%s)
"""

ProductDetail.search_main_protein_query = """
SELECT
    product_detail_id,
    type,
    brand,
    product_name,
    function,
    description,
    crude_protein,
    crude_fat,
    calories,
    thumbnail,
    kibble_size,
    life,
    protein_type,
    main_protein,
    certified,
    preservative,
    feedshape,
    last_update
FROM "OPD".product_detail
WHERE LOWER(COALESCE(main_protein, '')) LIKE LOWER(%s)
ORDER BY product_name ASC
"""


# =========================================================
# ☑️ 추가: 사원 전체 개수 조회
# =========================================================
Employee.count_query = """
SELECT COUNT(*) AS total_count
FROM "ERP".employee
"""

# =========================================================
# ☑️ 추가: 사원 검색 개수/조회 쿼리
# =========================================================
Employee.search_username_count_query = """
SELECT COUNT(*) AS total_count
FROM "ERP".employee
WHERE LOWER(COALESCE(username, '')) LIKE LOWER(%s)
"""

Employee.search_username_query = """
SELECT
    employee_id,
    account_id,
    username,
    hire_date,
    quit_date,
    emp_position_id,
    manager_id,
    email,
    phone,
    address,
    postal_code,
    active
FROM "ERP".employee
WHERE LOWER(COALESCE(username, '')) LIKE LOWER(%s)
ORDER BY employee_id ASC
"""

Employee.search_employee_id_count_query = """
SELECT COUNT(*) AS total_count
FROM "ERP".employee
WHERE CAST(employee_id AS TEXT) LIKE %s
"""

Employee.search_employee_id_query = """
SELECT
    employee_id,
    account_id,
    username,
    hire_date,
    quit_date,
    emp_position_id,
    manager_id,
    email,
    phone,
    address,
    postal_code,
    active
FROM "ERP".employee
WHERE CAST(employee_id AS TEXT) LIKE %s
ORDER BY employee_id ASC
"""

Employee.search_account_id_count_query = """
SELECT COUNT(*) AS total_count
FROM "ERP".employee
WHERE LOWER(COALESCE(account_id, '')) LIKE LOWER(%s)
"""

Employee.search_account_id_query = """
SELECT
    employee_id,
    account_id,
    username,
    hire_date,
    quit_date,
    emp_position_id,
    manager_id,
    email,
    phone,
    address,
    postal_code,
    active
FROM "ERP".employee
WHERE LOWER(COALESCE(account_id, '')) LIKE LOWER(%s)
ORDER BY employee_id ASC
"""

Employee.search_emp_position_id_count_query = """
SELECT COUNT(*) AS total_count
FROM "ERP".employee
WHERE CAST(emp_position_id AS TEXT) LIKE %s
"""

Employee.search_emp_position_id_query = """
SELECT
    employee_id,
    account_id,
    username,
    hire_date,
    quit_date,
    emp_position_id,
    manager_id,
    email,
    phone,
    address,
    postal_code,
    active
FROM "ERP".employee
WHERE CAST(emp_position_id AS TEXT) LIKE %s
ORDER BY employee_id ASC
"""

Employee.search_phone_count_query = """
SELECT COUNT(*) AS total_count
FROM "ERP".employee
WHERE LOWER(COALESCE(phone, '')) LIKE LOWER(%s)
"""

Employee.search_phone_query = """
SELECT
    employee_id,
    account_id,
    username,
    hire_date,
    quit_date,
    emp_position_id,
    manager_id,
    email,
    phone,
    address,
    postal_code,
    active
FROM "ERP".employee
WHERE LOWER(COALESCE(phone, '')) LIKE LOWER(%s)
ORDER BY employee_id ASC
"""

Employee.search_email_count_query = """
SELECT COUNT(*) AS total_count
FROM "ERP".employee
WHERE LOWER(COALESCE(email, '')) LIKE LOWER(%s)
"""

Employee.search_email_query = """
SELECT
    employee_id,
    account_id,
    username,
    hire_date,
    quit_date,
    emp_position_id,
    manager_id,
    email,
    phone,
    address,
    postal_code,
    active
FROM "ERP".employee
WHERE LOWER(COALESCE(email, '')) LIKE LOWER(%s)
ORDER BY employee_id ASC
"""


# =========================================================
# ☑️ 수정: 고객 boolean 컬럼 검색을 화면 표시값 기준으로 변경
# - DB boolean true/false를 그대로 검색하면 화면의 Y/N, 활성/비활성과 안 맞음
# - 따라서 CASE로 화면 표시값을 만든 뒤 검색함
# =========================================================
Customer.search_is_subscribed_count_query = """
SELECT COUNT(*) AS total_count
FROM "Companion".customer
WHERE LOWER(
    CASE
        WHEN is_subscribed IS TRUE THEN 'Y'
        ELSE 'N'
    END
) LIKE LOWER(%s)
"""

Customer.search_is_subscribed_query = """
SELECT
    customer_id,
    is_subscribed,
    subs_count,
    permission,
    active,
    last_update
FROM "Companion".customer
WHERE LOWER(
    CASE
        WHEN is_subscribed IS TRUE THEN 'Y'
        ELSE 'N'
    END
) LIKE LOWER(%s)
ORDER BY customer_id ASC
"""

Customer.search_active_count_query = """
SELECT COUNT(*) AS total_count
FROM "Companion".customer
WHERE LOWER(
    CASE
        WHEN active IS TRUE THEN '활성'
        ELSE '비활성'
    END
) LIKE LOWER(%s)
"""

Customer.search_active_query = """
SELECT
    customer_id,
    is_subscribed,
    subs_count,
    permission,
    active,
    last_update
FROM "Companion".customer
WHERE LOWER(
    CASE
        WHEN active IS TRUE THEN '활성'
        ELSE '비활성'
    END
) LIKE LOWER(%s)
ORDER BY customer_id ASC
"""
