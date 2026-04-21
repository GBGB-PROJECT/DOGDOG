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
    # ☑️ 고객 검색 개수 조회
    # =========================================================
    search_count_query\
        = """
        SELECT COUNT(*) AS total_count
        FROM "Companion".customer
        WHERE
            CAST(customer_id AS TEXT) LIKE %s
            OR LOWER(CAST(is_subscribed AS TEXT)) LIKE LOWER(%s)
            OR CAST(subs_count AS TEXT) LIKE %s
            OR CAST(permission AS TEXT) LIKE %s
            OR LOWER(CAST(active AS TEXT)) LIKE LOWER(%s)
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
    # ☑️ 고객 검색 조회
    # =========================================================
    search_query\
        = """
        SELECT
            customer_id,
            is_subscribed,
            subs_count,
            permission,
            active,
            last_update
        FROM "Companion".customer
        WHERE
            CAST(customer_id AS TEXT) LIKE %s
            OR LOWER(CAST(is_subscribed AS TEXT)) LIKE LOWER(%s)
            OR CAST(subs_count AS TEXT) LIKE %s
            OR CAST(permission AS TEXT) LIKE %s
            OR LOWER(CAST(active AS TEXT)) LIKE LOWER(%s)
        ORDER BY customer_id ASC
        """