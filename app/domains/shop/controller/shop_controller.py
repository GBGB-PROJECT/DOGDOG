import flet as ft
import asyncio
import components as dogdog
from domains.shop.controller.shop_api import get_shop_product_list, get_recommended_foods

class ShopController:
    @staticmethod
    async def load_recommended_foods(page, product_guide, guide_image_size):
        storage = page.session.store
        pet_id = (
                storage.get("pet_id")
                or storage.get("customer_pet_id")
                or storage.get("current_pet_id")
            )

        if not pet_id:
            product_guide.content.controls[1].controls = [
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        dogdog.basic_text(
                            "반려견 정보를 찾을 수 없습니다.",
                            size=12,
                            color=ft.Colors.GREY_500
                        )
                    ]
                )
            ]
            product_guide.length = 1
            product_guide.update()
            return

        foods = await get_recommended_foods(page, int(pet_id))

        if not foods:
            product_guide.content.controls[1].controls = [
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        dogdog.basic_text(
                            "추천사료가 없습니다.",
                            size=12,
                            color=ft.Colors.GREY_500
                        )
                    ]
                )
            ]
            product_guide.length = 1
            product_guide.update()
            return

        recommended_views = dogdog.products(
            page,
            foods,
            guide_image_size
        )

        product_guide.content.controls[1].controls = recommended_views
        product_guide.length = len(recommended_views)
        product_guide.selected_index = 0
        product_guide.update()

    @staticmethod
    async def load_products(
        page,
        product_list,
        product_image_size,
        product_state,
        more_button,
        sort=None,
        reset=True,
        keyword=None,
    ):
        if product_state["is_loading"]:
            return

        product_state["is_loading"] = True
        more_button.visible = False

        if reset:
            product_state["items"] = {}
            product_state["offset"] = 0
            product_state["sort"] = sort
            product_state["keyword"] = keyword
            product_state["has_more"] = True

            product_list.content = ft.Column(
                controls=[
                    ft.Container(
                        alignment=ft.Alignment.CENTER,
                        content=ft.ProgressRing()
                    )
                ]
            )
            product_list.update()
            more_button.update()

        products = await get_shop_product_list(
            page,
            sort=product_state["sort"],
            keyword=product_state.get("keyword"),
            limit=product_state["limit"],
            offset=product_state["offset"],
        )

        if products:
            product_state["items"].update(products)
            product_state["offset"] += len(products)
            product_state["has_more"] = len(products) == product_state["limit"]
        else:
            product_state["has_more"] = False

        if not product_state["items"]:
            product_list.content = ft.Column(
                controls=[
                    dogdog.basic_text(
                        "상품이 없습니다.",
                        size=14,
                        color=ft.Colors.GREY_500
                    )
                ]
            )
        else:
            product_list.content = ft.Column(
                controls=dogdog.products(
                    page,
                    product_state["items"],
                    product_image_size
                )
            )

        product_state["is_loading"] = False
        more_button.visible = product_state["has_more"]

        product_list.update()
        more_button.update()


    @staticmethod
    def product_guide_page(product_guide, key):
        view_page_index = product_guide.selected_index
        if key == "forward":
            if product_guide.selected_index == product_guide.length - 1:
                product_guide.selected_index = 0
            else: product_guide.selected_index = view_page_index + 1
        elif key == "back":
            if product_guide.selected_index == 0: 
                product_guide.selected_index = product_guide.length - 1
            else: product_guide.selected_index = view_page_index - 1
        product_guide.update()

    @staticmethod
    async def shop_timesleep(product_guide):
        try:
            for i in range(999):
                await asyncio.sleep(5)
                ShopController.product_guide_page(product_guide, "forward")
        except: pass

    @staticmethod
    def check_food_status(page):
        """사료 등록 상태를 판별하는 비즈니스 규칙입니다."""
        storage = page.session.store
        pet_food_detail = storage.get("pet_food_detail")
        return (
            isinstance(pet_food_detail, dict) 
            and len(pet_food_detail) > 0 
            and (pet_food_detail.get("product_id") or pet_food_detail.get("pet_food_id"))
        )

    @staticmethod
    async def get_feeding_data(page, pet_id):
        from domains.shop.controller.shop_api import get_feeding_guide
        data = await get_feeding_guide(page, int(pet_id))
        
        # [Passive View] 사료 등록 상태 판별 (컨트롤러 담당)
        is_food_exist = ShopController.check_food_status(page)
        
        if not data:
            return {
                "is_food_exist": False,
                "pet_name": page.session.store.get("customer_pet_name") or "반려견",
                "daily_food_g": "??g",
                "schedule": "급여 중인 상품을 등록해주세요",
                "total_kcal": "0",
                "kcal_per_kg": "0",
                "is_kcal_visible": False
            }
        
        feeding_count = data.get("feeding_count", 0)
        per_meal = data.get("adjusted_per_meal_g", "0")
        
        # 배차 정보 생성
        if feeding_count == 1:
            schedule = f"일 1회 {per_meal}g"
        elif feeding_count == 2:
            schedule = f"아침 {per_meal}g, 저녁 {per_meal}g"
        elif feeding_count == 3:
            schedule = f"아침 {per_meal}g, 점심 {per_meal}g, 저녁 {per_meal}g"
        else:
            schedule = f"일 {feeding_count}회 분할 급여 (회당 {per_meal}g)"

        # 천 단위 콤마 적용
        g_val = float(data.get('adjusted_daily_food_g', 0))
        daily_food_g = f"{int(g_val):,}" if g_val == int(g_val) else f"{g_val:,.1f}"
        
        k_val = float(data.get('daily_total_kcal', 0))
        total_kcal = f"{k_val:,.1f}"

        # [Passive View] 뷰를 위한 최종 데이터 패키징
        res = {
            "is_food_exist": is_food_exist,
            "pet_name": page.session.store.get("customer_pet_name") or "반려견",
            "daily_food_g": f"{daily_food_g}g" if is_food_exist else "??g",
            "schedule": schedule if is_food_exist else "급여 중인 상품을 등록해주세요",
            "total_kcal": f"총 {total_kcal}kcal",
            "kcal_per_kg": f"제품의 열량 {int(data.get('kcal_per_kg', 0)):,}kcal/kg",
            "is_kcal_visible": is_food_exist
        }
        return res
