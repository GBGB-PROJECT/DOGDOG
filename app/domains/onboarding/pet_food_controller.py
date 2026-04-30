import flet as ft
from api_client import ApiClient

class PetFoodController:
    """
    [Controller] PetFoodController
    역할: 사료 검색 API, 사료 용량 API 연동 및 상태 저장(Debouncing 검색 포함)
    """
    def __init__(self, page: ft.Page, popup):
        self.page = page
        self.popup = popup
        self.storage = page.session.store
        self._search_task = None
        self.selected_product_detail_id = None

    def open_food_bottom_sheet(self, e, food_search_field, food_list_column):
        food_search_field.value = ""
        food_list_column.controls.clear()
        
        food_bottom_sheet = self.popup.bottom_sheet_popup
        if food_bottom_sheet not in self.page.overlay:
            self.page.overlay.append(food_bottom_sheet)
        else:
            self.page.overlay.clear()
            self.page.overlay.append(food_bottom_sheet)
        food_bottom_sheet.open = True
        self.page.update()

    async def on_food_search_change(self, e, food_list_column, select_food_callback):
        import asyncio
        import components as dogdog
        
        keyword = e.control.value

        if self._search_task:
            self._search_task.cancel()

        async def search_with_debounce():
            try:
                await asyncio.sleep(0.5)

                if not keyword or len(keyword) < 1:
                    food_list_column.controls.clear()
                    food_list_column.controls.append(dogdog.basic_text(value="검색어를 입력해 주세요.", size=14))
                    self.page.update()
                    return

                food_list_column.controls.clear()
                food_list_column.controls.append(dogdog.basic_text(value="검색 중...", size=14))
                self.page.update()

                api_client = ApiClient(self.page)
                res_name = await api_client.get("/products/name", params={"keyword": keyword})
                
                if res_name.status_code != 200:
                    food_list_column.controls.clear()
                    food_list_column.controls.append(dogdog.basic_text(value="검색 결과를 가져올 수 없습니다.", size=14))
                    self.page.update()
                    return

                products = res_name.json().get("data", [])
                if not products:
                    food_list_column.controls.clear()
                    food_list_column.controls.append(dogdog.basic_text(value="검색 결과가 없습니다.", size=14))
                    self.page.update()
                    return

                search_list = [[str(p.get("product_detail_id")), p.get("product_name")] for p in products]

                dogdog.update_item_list(
                    list_column=food_list_column,
                    search_data=search_list,
                    select_key=self.selected_product_detail_id,
                    select_value=select_food_callback,
                    keyword=keyword,
                )
                self.page.update()

            except asyncio.CancelledError:
                pass
            except Exception as err:
                print(f"[API Error] 사료 이름 검색 실패: {err}")
                food_list_column.controls.clear()
                food_list_column.controls.append(dogdog.basic_text(value="서버 오류가 발생했습니다.", size=14))
                self.page.update()

        self._search_task = asyncio.create_task(search_with_debounce())

    async def select_food(self, product_detail_id, product_name, food_picker_field, product_weight_list):
        if not product_detail_id:
            return

        import components as dogdog
        try:
            self.selected_product_detail_id = product_detail_id
            self.popup.bottom_sheet_popup.open = False
            self.page.update()

            food_picker_field.content.controls[0].value = f"{product_name} (용량 확인 중...)"
            self.page.update()

            api_client = ApiClient(self.page)
            res_w = await api_client.get("/products/weights", params={"product_detail_id": product_detail_id})

            if res_w.status_code == 200:
                weights_data = res_w.json().get("data", [])
                if not weights_data:
                    food_picker_field.content.controls[0].value = f"{product_name} (선택 가능한 용량 없음)"
                    product_weight_list.visible = False
                    self.page.update()
                    return

                product_weight_list.options = [
                    dogdog.dropdown_menu_option(key=str(w.get("product_id")), text=f"{w.get('weight')}g")
                    for w in weights_data if w.get("active")
                ]
                
                food_picker_field.content.controls[0].value = product_name
                self.storage.set("food_text", product_name)
                product_weight_list.visible = True
                product_weight_list.value = None
                self.page.update()
            else:
                food_picker_field.content.controls[0].value = f"{product_name} (정보 조회 실패)"
                self.page.update()
        except Exception as e:
            print(f"[UI Error] 사료 상세 조회 처리 실패: {e}")

    def food_product_weight_set(self, e, product_weight_list):
        selected_product_id = e.control.value
        if not selected_product_id:
            return

        self.storage.set("product_id", int(selected_product_id))
        selected_option = next((opt for opt in product_weight_list.options if opt.key == selected_product_id), None)
        
        if selected_option:
            try:
                weight_val = selected_option.text.replace("g", "")
                self.storage.set("product_weight", int(float(weight_val)))
            except (ValueError, TypeError):
                pass
        self.page.update()

    def update_field(self, key: str, value):
        if value is None or str(value).strip() == "":
            self.storage.remove(key)
        else:
            self.storage.set(key, value)
