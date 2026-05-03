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
    async def load_products(page, product_list, product_image_size, sort=None):
        products = await get_shop_product_list(page, sort=sort)

        if not products:
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
            print("상품 리스트 출력")
            product_list.content = ft.Column(
                controls=dogdog.products(
                    page,
                    products,
                    product_image_size
                )
            )

        product_list.update()

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
    async def get_feeding_data(page, pet_id):
        from domains.shop.controller.shop_api import get_feeding_guide
        data = await get_feeding_guide(page, int(pet_id))
        if not data:
            return None
        
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

        # 천 단위 콤마 적용 및 딕셔너리 반환
        g_val = float(data.get('adjusted_daily_food_g', 0))
        daily_food_g = f"{int(g_val):,}" if g_val == int(g_val) else f"{g_val:,.1f}"
        
        k_val = float(data.get('daily_total_kcal', 0))
        total_kcal = f"{k_val:,.1f}"  # 소수점 첫째 자리까지 표시

        res = {
            "daily_food_g": daily_food_g,
            "schedule": schedule,
            "total_kcal": total_kcal,
            "kcal_per_kg": f"{int(data.get('kcal_per_kg', 0)):,}", # 수치만 반환 (UI에서 kcal/kg 붙임)
            "pet_name": page.session.store.get("customer_pet_name") or "반려견"
        }
        return res
