import flet as ft
from datetime import datetime
from api_client import ApiClient


class FeedingAddEditController:
    """
    [Controller] FeedingAddEditController
    역할: 사료의 신규 등록 및 수정을 전담하는 컨트롤러입니다.
    - 데이터 검증, API 통신, 세션 관리 및 삭제 확인 팝업 로직을 포함합니다.
    """

    def __init__(self, page: ft.Page, popup=None):
        self.page = page
        self.popup = popup
        self.api_client = ApiClient(page)
        self.storage = page.session.store

    def get_initial_data(self, view_mode: str):
        """
        수정 모드일 때 세션에서 기존 데이터를 가져와 반환합니다.
        """
        if view_mode == "edit":
            return self.storage.get("select_feeding_data") or {}
        return {}

    async def save_feeding_product(self, product_id, total_weight):
        """
        [QA 수정] 신규 사료 제품을 등록합니다.
        API: POST /pets/{pet_id}/pet_food
        (기존 사료가 있다면 서버에서 자동으로 종료 처리하고 새 사료를 등록함)
        """
        pet_id = self.storage.get("current_pet_id")
        if not pet_id:
            return False, "반려견 정보를 찾을 수 없습니다."

        # 최신 API 명세에 맞춰 필수 필드만 포함한 페이로드 (POST 방식)
        payload = {
            "product_id": int(product_id),
            "total_weight": int(total_weight),
            "effective_date": datetime.now().strftime("%Y-%m-%d")
        }

        try:
            print(f"👉 [로그] 컨트롤러: 사료 등록 API 호출 (POST /pets/{pet_id}/pet_food)")
            print(f"👉 [로그] 페이로드: {payload}")

            res = await self.api_client.post(f"/pets/{pet_id}/pet_food", data=payload)

            if res.status_code in [200, 201]:
                # 성공 시 세션 정리 (목록 갱신 유도)
                if self.storage.contains_key("pet_food_detail"):
                    self.storage.remove("pet_food_detail")
                if self.storage.contains_key("select_feeding_data"):
                    self.storage.remove("select_feeding_data")

                customer_detail = self.storage.get("customer_detail") or {}
                if "dashboard_sync" in customer_detail:
                    customer_detail["dashboard_sync"]["food_inventory"] = {}
                    self.storage.set("customer_detail", customer_detail)

                return True, "사료가 성공적으로 등록되었습니다."
            else:
                # [QA 수정] 3. 상세 에러 로그 기록 (res.text)
                detail = res.json().get("detail", "알 수 없는 오류")
                print(f"❌ [로그] 컨트롤러: 등록 실패 ({res.status_code})")
                print(f"❌ [로그] 서버 응답 상세: {res.text}")
                return False, f"등록 실패: {detail}"
        except Exception as e:
            print(f"❌ [로그] 컨트롤러: 등록 API 통신 오류 - {str(e)}")
            return False, f"서버 통신 오류: {str(e)}"

    async def update_feeding_product(self, customer_food_id, left_intake):
        """
        기존 사료 제품 정보를 수정(잔여량 등)합니다.
        """
        payload = {"total_weight": int(left_intake)}

        try:
            # PATCH /api/v1/customer_food/{id} (가정)
            res = await self.api_client.patch(
                f"/customer_food/{customer_food_id}", data=payload
            )
            if res.status_code == 200:
                return True, "사료 정보가 수정되었습니다."
            else:
                return (
                    False,
                    f"수정 실패: {res.json().get('detail', '알 수 없는 오류')}",
                )
        except Exception as e:
            return False, f"서버 통신 오류: {str(e)}"

    async def delete_feeding_product(self):
        """
        [QA 수정] 급여 중인 사료 제품을 삭제합니다.
        API: DELETE /pets/{pet_id}/pet_food
        """
        pet_id = self.storage.get("current_pet_id")
        if not pet_id:
            print("👉 [로그] 컨트롤러: pet_id가 세션에 없습니다.")
            return False, "반려견 정보를 찾을 수 없습니다."

        try:
            print(f"👉 [로그] 컨트롤러: 삭제 API 호출 시작 (pet_id: {pet_id})")
            res = await self.api_client.delete(f"/pets/{pet_id}/pet_food")

            if res.status_code == 200:
                print("👉 [로그] 컨트롤러: 삭제 성공")
                return True, "삭제되었습니다."
            else:
                detail = res.json().get("detail", "알 수 없는 오류")
                print(f"👉 [로그] 컨트롤러: 삭제 실패 ({res.status_code}) - {detail}")
                return False, f"삭제 실패: {detail}"
        except Exception as e:
            print(f"👉 [로그] 컨트롤러: 삭제 API 통신 오류 - {str(e)}")
            return False, f"서버 통신 오류: {str(e)}"

    def show_delete_confirm_dialog(self, on_success_callback=None):
        """
        [QA 수정] 삭제 확인용 경고창을 띄우고, 확인 시 실제 API 연동을 처리합니다.
        """
        print("👉 [로그] 컨트롤러: 삭제 확인 다이얼로그 함수 진입")

        async def on_confirm(e):
            print("👉 [로그] 컨트롤러: 삭제 확인 버튼 클릭 - API 연동 시작")
            # 1. API 호출
            success, msg = await self.delete_feeding_product()

            if success:
                # 2. 성공 시 처리
                dialog.open = False
                self.page.update()

                # 스낵바 알림
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(msg), bgcolor=ft.Colors.GREEN_400
                )
                self.page.snack_bar.open = True

                # 3. 데이터 동기화 및 세션 정리 (빈 상태 반영)
                self.storage.remove("pet_food_detail")
                if self.storage.contains_key("select_feeding_data"):
                    self.storage.remove("select_feeding_data")
                if self.storage.contains_key("select_customer_food_id"):
                    self.storage.remove("select_customer_food_id")

                # 대시보드 통계 정보에서도 사료 관련 정보를 초기화하기 위해 전체 동기화 권장
                customer_detail = self.storage.get("customer_detail") or {}
                if "dashboard_sync" in customer_detail:
                    customer_detail["dashboard_sync"]["food_inventory"] = {}
                    self.storage.set("customer_detail", customer_detail)

                # 4. 화면 이동 (사료 리스트로 복귀)
                self.page.go("/feeding")

                # 대시보드 갱신 알림 (PubSub)
                self.page.pubsub.send_all("update_dashboard")

                if on_success_callback:
                    self.page.run_task(on_success_callback)
            else:
                # 4. 실패 시 처리
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(msg), bgcolor=ft.Colors.RED_400
                )
                self.page.snack_bar.open = True
                self.page.update()

        def on_cancel(e):
            print("👉 [로그] 컨트롤러: 삭제 취소 버튼 클릭")
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("상품 삭제", weight="bold"),
            content=ft.Text("급여 중인 사료 정보를 삭제하시겠습니까?"),
            actions=[
                ft.TextButton("취소", on_click=on_cancel),
                ft.TextButton("확인", on_click=on_confirm),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # [강력한 업데이트 방식] Overlay 추가 및 할당
        if dialog not in self.page.overlay:
            self.page.overlay.append(dialog)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_duplicate_error_dialog(self):
        """
        중복 등록 방지 알림창을 띄웁니다.
        """
        print("👉 [로그] 컨트롤러: 중복 등록 에러 다이얼로그 함수 진입")

        def on_close(e):
            print("👉 [로그] 컨트롤러: 중복 에러 확인 버튼 클릭")
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("알림", weight="bold"),
            content=ft.Text("급여 중인 상품이 있는 경우 신규 상품 등록이 불가합니다.\n삭제 또는 수정하여 진행해주세요."),
            actions=[
                ft.TextButton("확인", on_click=on_close),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # [강력한 업데이트 방식] Overlay 추가 및 할당 (Flet 0.81.0 대응)
        if dialog not in self.page.overlay:
            self.page.overlay.append(dialog)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
