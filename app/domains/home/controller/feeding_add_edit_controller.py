import flet as ft
from datetime import datetime
from api_client import ApiClient


class FeedingAddEditController:
    """
    [Controller] FeedingAddEditController
    역할: 사료의 신규 등록 및 수정을 전담하는 컨트롤러입니다.
    - 데이터 검증, API 통신, 세션 관리 및 삭제 확인 팝업 로직을 포함합니다.
    - [QA 수정] 상태 동기화 및 비동기 처리 안정화 로직이 적용되었습니다.
    """

    def __init__(self, page: ft.Page, popup=None):
        self.page = page
        self.popup = popup
        self.api_client = ApiClient(page)
        self.storage = page.session.store

    def _clear_feeding_session(self):
        """
        [QA 수정] 등록/삭제 성공 시 세션의 사료 관련 정보를 강제로 청소합니다.
        유령 데이터(과거 세션 캐시)를 방지하고 최신 서버 데이터를 가져오게 합니다.
        """
        keys_to_clear = [
            "select_feeding_data", 
            "select_customer_food_id",
            "food_text", 
            "product_id", 
            "food_weight",
            "feeding_start"
        ]
        for key in keys_to_clear:
            if self.storage.contains_key(key):
                self.storage.remove(key)
        
        # [신규 추가] 세션 데이터 완벽 제거 (None 강제 할당)
        self.storage.set("pet_food_detail", None)
        self.storage.set("dashboard_data", None) # 홈 진입 시 강제 fetch를 위한 플래그 초기화

        # 대시보드 인벤토리 및 사료 정보 즉시 초기화
        customer_detail = self.storage.get("customer_detail") or {}
        if "dashboard_sync" in customer_detail:
            customer_detail["dashboard_sync"]["food_inventory"] = {}
            customer_detail["dashboard_sync"]["current_food_info"] = None
            self.storage.set("customer_detail", customer_detail)
        
        # [보정] 사료 정보 변경 시 모든 팝업, 다이얼로그, 오버레이 강제 초기화 (Zero-Base)
        self.page.dialog = None  # 활성화된 다이얼로그 객체 파괴
        self.page.banner = None  # 배너 제거
        self.page.overlay.clear() # 오버레이에 쌓인 모든 유령 UI 제거
        
        # [Step 1] 홈 화면에 새로고침 신호 저장 (store.set 사용)
        self.storage.set('needs_refresh', True)
        
        # UI 상태 동기화를 위해 페이지 업데이트
        self.page.update()

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
                # [ISSUE] 부분 업데이트 이슈로 인한 홈 화면 리셋 임시 조치 (2026-05-05)
                # [TODO] 팝업 연동 및 부분 업데이트 로직 고도화 필요
                
                # [수정 1] 네비게이션 전 대시보드 갱신 예약 및 홈 직행
                self.storage.set('needs_refresh', True)
                
                # [해결 2] 팝업 실행 시퀀스 조정 (홈 진입 시 트리거되도록 플래그 설정)
                self.storage.set("trigger_feeding_guide_popup", True)
                
                self.page.pubsub.send_all("update_dashboard")
                self.page.pubsub.send_all("refresh_feeding_list")
                
                self.page.overlay.clear()
                self.page.dialog = None
                
                # [핵심 지침 1] 네비게이션 전 강제 대기 (DB 동기화 확보)
                import asyncio
                await asyncio.sleep(0.2)
                
                # [수정] 홈 화면으로 즉시 이동하여 강제 리셋 및 팝업 유도
                self.page.go("/home")

                return True, "사료가 성공적으로 등록되었습니다."
            else:
                # 상세 에러 로그 기록 (res.text)
                detail = res.json().get("detail", "알 수 없는 오류")
                print(f"❌ [로그] 컨트롤러: 등록 실패 ({res.status_code})")
                print(f"❌ [로그] 서버 응답 상세: {res.text}")
                return False, f"등록 실패: {detail}"
        except Exception as e:
            print(f"❌ [로그] 컨트롤러: 등록 API 통신 오류 - {str(e)}")
            return False, f"서버 통신 오류: {str(e)}"

    async def update_feeding_product(self, f_weight, f_date):
        """
        [Step 3] 기존 사료 제품 정보를 수정(PATCH /pets/{pet_id}/pet_food)합니다.
        """
        pet_id = self.storage.get("current_pet_id")
        product_id = self.storage.get("product_id")

        if not pet_id:
            return False, "반려견 정보를 찾을 수 없습니다."
        if not product_id:
            return False, "상품 정보를 찾을 수 없습니다."

        payload = {
            "product_id": int(product_id),
            "total_weight": int(f_weight),
            "effective_date": f_date
        }

        try:
            print(f"👉 [로그] 컨트롤러: 사료 수정 API 호출 (PATCH /pets/{pet_id}/pet_food)")
            print(f"👉 [로그] 페이로드: {payload}")

            res = await self.api_client.patch(
                f"/pets/{pet_id}/pet_food", data=payload
            )
            if res.status_code == 200:
                # [ISSUE] 부분 업데이트 시 UI 레이스 컨디션 및 하얀 화면 발생 (2026-05-05)
                # [TODO] 향후 PubSub 기반의 부분 업데이트 로직으로 고도화 필요. 현재는 안정성을 위해 홈 직행 리셋 방식 사용.

                # [수정 1] 네비게이션 전 대시보드 갱신 예약 및 홈 직행
                self.storage.set('needs_refresh', True)
                self.page.pubsub.send_all("update_dashboard")
                self.page.pubsub.send_all("refresh_feeding_list")
                
                self.page.overlay.clear()
                self.page.dialog = None

                # [핵심 지침 1] 네비게이션 전 강제 대기 (DB 동기화 확보)
                import asyncio
                await asyncio.sleep(0.2)
                
                # [기존] 목록 화면으로 복귀
                # self.page.go("/feeding")
                
                # [수정] 홈 화면으로 즉시 이동
                self.page.go("/home")
                
                return True, "사료 정보가 수정되었습니다."
            else:
                detail = res.json().get("detail", "알 수 없는 오류")
                print(f"❌ [로그] 컨트롤러: 수정 실패 ({res.status_code}) - {res.text}")
                return False, f"수정 실패: {detail}"
        except Exception as e:
            print(f"❌ [로그] 컨트롤러: 수정 API 통신 오류 - {str(e)}")
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

            # [QA 수정] 2. 404 응답을 성공으로 간주 (Idempotency 보장)
            if res.status_code in [200, 404]:
                if res.status_code == 404:
                    print(f"⚠️ [로그] 컨트롤러: 삭제 대상이 이미 존재하지 않음 (404) - {res.text}")
                else:
                    print("👉 [로그] 컨트롤러: 삭제 성공 (200)")
                return True, "삭제되었습니다."
            else:
                detail = res.json().get("detail", "알 수 없는 오류")
                print(f"❌ [로그] 컨트롤러: 삭제 실패 ({res.status_code}) - {res.text}")
                return False, f"삭제 실패: {detail}"
        except Exception as e:
            print(f"❌ [로그] 컨트롤러: 삭제 API 통신 오류 - {str(e)}")
            return False, f"서버 통신 오류: {str(e)}"

    def show_delete_confirm_dialog(self, on_success_callback=None):
        """
        [QA 수정] 삭제 확인용 경고창을 띄우고, 확인 시 실제 API 연동을 처리합니다.
        """
        print("👉 [로그] 컨트롤러: 삭제 확인 다이얼로그 함수 진입")

        async def on_confirm(e):
            print("👉 [로그] 컨트롤러: 삭제 확인 버튼 클릭 - API 연동 시작")
            success, msg = await self.delete_feeding_product()

            if success:
                dialog.open = False
                self.page.update()

                # 스낵바 알림
                self.page.snack_bar = ft.SnackBar(
                    ft.Text(msg), bgcolor=ft.Colors.GREEN_400
                )
                self.page.snack_bar.open = True

                # [QA 수정] 1. 세션 캐시 강제 무효화
                self._clear_feeding_session()

                # [ISSUE] 부분 업데이트 시 UI 레이스 컨디션 및 하얀 화면 발생 (2026-05-05)
                # [TODO] 향후 PubSub 기반의 부분 업데이트 로직으로 고도화 필요. 현재는 안정성을 위해 홈 직행 리셋 방식 사용.

                # [해결 과제 1] 삭제 로직 내 강제 신호 발송
                self.storage.set('needs_refresh', True)
                self.page.pubsub.send_all("update_dashboard")
                self.page.pubsub.send_all("refresh_feeding_list")

                # [해결 과제 3] 팝업 잔상 물리적 소거
                self.page.overlay.clear()
                self.page.dialog = None
                self.page.update()

                # [핵심 지침 1] 네비게이션 전 강제 대기 (DB 동기화 확보)
                import asyncio
                await asyncio.sleep(0.2)
                
                # [기존] 리스트 화면으로 복귀
                # self.page.go("/feeding")
                
                # [수정] 홈 화면으로 즉시 이동
                self.page.go("/home")

                # [QA 수정] 3. 비동기 콜백 예약 (await 제거 - Flet 0.81.0 준수)
                if on_success_callback:
                    self.page.run_task(on_success_callback)
            else:
                needs_refresh = self.page.session.store.get('needs_refresh')
                if needs_refresh:
                    pet_id = self.page.session.store.get("current_pet_id")
                    if pet_id:
                        print(f"👉 [Home] 대시보드 갱신 예약 감지. Zero-Base 재건축 시작.")
                        
                        # [수정 2] 기존 객체 완전 삭제 및 재건축 (문지기 로직)
                        self.page.body_column.controls.clear()
                        self.page.body_scroll_column.controls.clear()
                        self.page.main_container_content.clear()
                        
                        # 데이터 강제 재요청
                        await self.controller.fetch_dashboard_data(pet_id)
                        
                        # 세션 정합성 재검증
                        customer_detail = self.page.session.store.get("customer_detail")
                        if not customer_detail or "dashboard_sync" not in customer_detail:
                            await self.controller.fetch_dashboard_data(pet_id)

                        self.page.session.store.set('needs_refresh', False)
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

        if dialog not in self.page.overlay:
            self.page.overlay.append(dialog)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_duplicate_error_dialog(self):
        """
        중복 등록 방지 알림창을 띄웁니다.
        """
        def on_close(e):
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

        if dialog not in self.page.overlay:
            self.page.overlay.append(dialog)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
