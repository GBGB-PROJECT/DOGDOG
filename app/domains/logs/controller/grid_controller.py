import flet as ft
from api_client import ApiClient
import datetime

class GridController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.storage = page.session.store
        self.api_client = ApiClient(page)

    async def get_one_time_feeding_amount(self, pet_id: int) -> str:
        """
        백엔드 API를 호출하여 1회 권장 급여량을 가져옵니다.
        """
        try:
            if not pet_id:
                return "?"

            res = await self.api_client.get(f"/calc_feeding/{pet_id}/one-time")
            if res.status_code == 200:
                data = res.json().get("data", {})
                amount = data.get("one_time_intake", 0)
                return f"{int(amount)}" if amount > 0 else "0"
            else:
                print(f"[GridController] API 호출 실패 ({res.status_code}): {res.text}")
                return "?"
        except Exception as e:
            print(f"[GridController] 1회 급여량 조회 중 오류: {e}")
            return "-"

    async def get_pet_food_info(self, pet_id: int):
        """
        반려견이 현재 먹고 있는 사료 정보를 가져옵니다.
        """
        try:
            if not pet_id:
                return None
            
            res = await self.api_client.get(f"/pets/{pet_id}/pet_food")
            if res.status_code == 200:
                return res.json().get("data")
            return None
        except Exception as e:
            print(f"[GridController] 사료 정보 조회 중 오류: {e}")
            return None

    async def save_feeding_api(self, call: str, on_refresh_callback=None):
        """
        급여 기록을 서버에 저장하고 결과에 따른 후처리를 수행합니다.
        """
        try:
            # 1. Payload 구성
            pet_id = (
                self.storage.get("pet_id")
                or self.storage.get("customer_pet_id")
                or self.storage.get("current_pet_id")
            )
            
            payload = {
                "pet_id": pet_id,
                "amount": self.storage.get(f"{call}_weight"),
                "feeding_date": self.storage.get(f"{call}_date"),
                "feeding_time": self.storage.get(f"{call}_time"),
                "memo": self.storage.get(f"{call}_memo")
            }

            print(f"[GridController] Feeding API 전송 시도: {payload}")
            
            # 2. API 호출
            res = await self.api_client.post("/logs/feeding", data=payload)
            
            if res.status_code in [200, 201]:
                print(f"[GridController] Feeding 저장 성공")
                import components as dogdog
                self.page.snack_bar = ft.SnackBar(
                    content=dogdog.basic_text("급여 기록이 저장되었습니다.", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.GREEN_400
                )
                self.page.snack_bar.open = True
                
                # [수정 3] 성공 콜백 실행 및 홈 화면 갱신 예약
                # [Step 2] 부분 업데이트: 전체 리셋 대신 특정 위젯만 콕 집어 업데이트
                try:
                    res_json = res.json()
                    new_inven = res_json.get("data", {}).get("inven", {})
                    left_intake = new_inven.get("left_intake")
                    
                    if left_intake is not None:
                        widget = self.storage.get("feeding_amount_widget")
                        if widget and hasattr(widget, "spans"):
                            # 첫 번째 span (현재 잔여량)만 교체
                            widget.spans[0].text = f"{int(left_intake):,}g"
                            widget.update()
                            print(f"✅ [GridController] 사료 잔량 위젯만 부분 업데이트 성공: {left_intake}g")
                except Exception as ue:
                    print(f"⚠️ [GridController] 부분 업데이트 실패 (폴백: 전체 갱신 신호 발송): {ue}")
                    self.storage.set('needs_refresh', True)
                
                self.page.pubsub.send_all('update_dashboard')
                
                if on_refresh_callback:
                    await on_refresh_callback()
                
                return True
            else:
                error_detail = res.json().get("detail", "알 수 없는 오류")
                print(f"[GridController] Feeding 저장 실패: {error_detail}")
                import components as dogdog
                self.page.snack_bar = ft.SnackBar(
                    content=dogdog.basic_text(f"저장에 실패했습니다: {error_detail}", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.RED_400
                )
                self.page.snack_bar.open = True
                return False

        except Exception as ex:
            print(f"[GridController] API 통신 중 예외 발생: {str(ex)}")
            import components as dogdog
            self.page.snack_bar = ft.SnackBar(
                content=dogdog.basic_text("서버 통신 중 오류가 발생했습니다.", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_400
            )
            self.page.snack_bar.open = True
            return False
        finally:
            self.page.update()
