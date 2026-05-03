from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.subscriptions.repository.subscriptions_repository import *

# 구독 내역 조회 ------------------------------------------------------------------
def read_subscription_service(db: Session, customer_id: int):
    subscription_row = get_active_subscription_by_customer_id(
        db=db,
        customer_id=customer_id,
    )

    if subscription_row is None:
        return {
            "is_subscribed": False,
            "subscription": None,
        }

    subs, subs_plan, subs_detail, subs_item = subscription_row

    recipient = None

    if subs_detail is not None:
        recipient = {
            "name": subs_detail.name,
            "phone": subs_detail.phone,
            "address": subs_detail.address,
            "detail_address": subs_detail.detail_address,
            "postal_code": subs_detail.postal_code,
        }

    return {
        "is_subscribed": True,
        "subscription": {
            "subs_id": subs.subs_id,
            "is_auto_delivery": subs.is_auto_delivery,
            "is_subs_status": subs.is_subs_status,
            "delivery_cycle": subs_plan.delivery_cycle,
            "subs_day": subs.subs_day,
            "subs_item": subs_item.product_id,
            "recipient": recipient,
        },
    }

# 구독 생성 ---------------------------------------------------------------------
def create_subscription_service(
        db: Session,
        customer_id: int,
        body):

    try:
        # 7. 중복 구독 확인
        if check_active_subscription(db, customer_id):
            return JSONResponse(
                status_code=409,
                content={
                    "success": False,
                    "error_code": "ACTIVE_SUBSCRIPTION_EXISTS",
                    "message": "이미 활성화된 구독이 존재합니다.",
                },
            )

        # 1. 상품 ID 유효성 검증
        if body.product_id <= 0:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error_code": "INVALID_PRODUCT_ID",
                    "message": "유효하지 않은 상품 ID입니다.",
                },
            )

        # 2. 상품 조회
        product_row = get_product(db, body.product_id)
        if not product_row:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error_code": "PRODUCT_NOT_FOUND",
                    "message": "상품이 존재하지 않거나 비활성 상태입니다.",
                },
            )

        product, product_name = product_row

        # 3. 수량 검증
        if body.quantity <= 0:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error_code": "INVALID_QUANTITY",
                    "message": "유효하지 않은 상품 수량입니다.",
                },
            )

        # 4. 배송주기 검증
        if body.delivery_cycle:
            if body.delivery_cycle not in [2, 4]:
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "error_code": "INVALID_DELIVERY_CYCLE",
                        "message": "배송주기는 2 또는 4만 선택 가능합니다.",
                    },
                )

        # 5. 결제수단 ID 유효성 검증
        # if body.payment_billing_id <= 0:
        #     return JSONResponse(
        #         status_code=400,
        #         content={
        #             "success": False,
        #             "error_code": "INVALID_PAYMENT_BILLING_ID",
        #             "message": "유효하지 않은 결제수단 ID입니다.",
        #         },
        #     )

        # 6. 결제수단 확인
        billing = get_payment_billing(db, customer_id)
        if not billing:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error_code": "PAYMENT_BILLING_NOT_FOUND",
                    "message": "결제수단이 존재하지 않거나 사용할 권한이 없습니다.",
                },
            )

        # 8. 포인트 검증
        used_point = body.used_point or 0
        if used_point < 0:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error_code": "INVALID_POINT",
                    "message": "사용할 수 없는 적립금입니다.",
                },
            )

        # 9. 쿠폰 검증
        # if body.coupon_id is not None and body.coupon_id <= 0:
        #     return JSONResponse(
        #         status_code=400,
        #         content={
        #             "success": False,
        #             "error_code": "INVALID_COUPON",
        #             "message": "사용할 수 없는 쿠폰입니다.",
        #         },
        #     )

        # 10. 가격 계산
        retail_price = int(product.retail_price)
        total_price = retail_price * body.quantity
        discount = int(total_price * 0.1)
        final_price = total_price - discount
        final_amount = final_price - used_point

        if final_amount < 0:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error_code": "INVALID_POINT",
                    "message": "사용 적립금이 결제 금액보다 클 수 없습니다.",
                },
            )

        # 11. subs 생성
        if body.is_auto_delivery is False:
            subs_plan = get_subs_plan(db, body.delivery_cycle)
            if not subs_plan:
                return JSONResponse(
                    status_code=404,
                    content={
                        "success": False,
                        "error_code": "SUBS_PLAN_NOT_FOUND",
                        "message": "배송주기에 해당하는 구독 플랜이 존재하지 않습니다.",
                    },
                )

            subs = create_subs(
                db=db,
                customer_id=customer_id,
                subs_plan_id=subs_plan.subs_plan_id,
                is_auto_delivery=body.is_auto_delivery,
            )
            print("정기배송: 생성된 subs_id:", subs.subs_id)
            print("subs", subs.customer_id)

        else:
            subs = create_subs(
                db=db,
                customer_id=customer_id,
                subs_plan_id=None,
                is_auto_delivery=body.is_auto_delivery,
            )
            print("자동배송: 생성된 subs_id:", subs.subs_id)
            print("subs", subs.customer_id)

        # 12. detail 생성
        create_subs_detail(db, subs.subs_id, billing.payment_billing_id, body)

        # 13. item 생성
        create_subs_item(
            db,
            subs.subs_id,
            body.product_id,
            body.quantity,
            retail_price,
            final_price,
        )
        
        # 14. payment 생성
        create_payment(db, subs.subs_id, final_amount)

        # 15. delivery 생성
        create_delivery(db, subs.subs_id)

        # 16. notification 설정 변경
        update_notification(db, customer_id)

        db.commit()

        return {
            "success": True,
            "message": "구독이 생성되었습니다.",
            "data": {
                "subs_id": subs.subs_id,
                "product_id": body.product_id,
                "product_name": product_name,
                "quantity": body.quantity,
                "delivery_cycle": body.delivery_cycle,
                "is_auto_delivery": body.is_auto_delivery,
                "is_subs_status": True,
                "product_price": total_price,
                "subscription_discount": discount,
                "coupon_discount": 0,
                "used_point": used_point,
                "delivery_fee": 0,
                "final_amount": final_amount,
            },
        }

    except Exception as e:
        db.rollback()
        print("구독 생성 실패:", e)

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message": "서버 내부 오류가 발생했습니다.",
            },
        )