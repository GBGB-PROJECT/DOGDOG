import flet as ft
import components as dogdog
import httpx

class AddressSearcher:
    def __init__(self, page: ft.Page, on_complete=None):
        self.page = page
        self.on_complete = on_complete
        
        # =======================================
        # 1단계) API 및 레이아웃 설정
        # =======================================
        self.api_url = "https://business.juso.go.kr/addrlink/addrLinkApi.do"
        self.api_key = "devU01TX0FVVEgyMDI2MDMxNzExNDQwNzExNzc0MjM="

        # =======================================
        # 2단계) UI 요소 준비
        # =======================================
        self.result_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self.result_column.controls.append(ft.Divider())
        self.search_input = ft.TextField(
            label="도로명 주소, 건물명 검색", 
            expand=True, 
            autofocus=True,
            on_submit=self.click_event,
            on_change=self.on_input_change
        )
        self.error_label = dogdog.basic_text(size=15, color=ft.Colors.RED)
        
        self.search_button = ft.IconButton(
            icon=ft.Icons.SEARCH, 
            icon_size=30,
            on_click=self.click_event
        )
        
        # 팝업 UI 컴포넌트
        self.check_popup = ft.AlertDialog(
            modal=True,
            title=dogdog.basic_text("주소 확인", weight="bold"),
            actions_alignment=ft.MainAxisAlignment.END
        )

        # =======================================
        # 3단계) 화면 조립
        # =======================================
        self.content = [
            ft.Row(
                controls=[
                    self.search_input,
                    self.search_button
                ]
            ),
            self.result_column
        ]

    # =======================================
    # 4단계) 이벤트 메서드
    # =======================================
    async def click_event(self, e):
        click_keyword = self.search_input.value.strip()
        self.result_column.controls.clear()
        self.result_column.controls.append(ft.ProgressRing())
        self.page.update() # 로딩 UI 즉시 반영

        try:
            params = {
                "confmKey": self.api_key,
                "currentPage": 1,
                "countPerPage": 50,
                "keyword": click_keyword,
                "resultType": "json"
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(self.api_url, params=params)
                data = response.json()
            common = data.get("results", {}).get("common", {}) 

            if common.get("errorCode") != "0":
                error_message_common = common.get("errorMessage")
                # print(f"에러 발생: {common.get('errorCode')}")
                # self.search_input.error_text = "API 에러 발생! 다시 입력하세요"
                self.result_column.controls.clear()
                self.result_column.controls.append(dogdog.basic_text(error_message_common, size=15, color=ft.Colors.RED))
                self.page.update()
                return

            page_juso = data.get("results", {}).get("juso", [])
            self.result_column.controls.clear()

            if not page_juso:
                self.result_column.controls.append(dogdog.basic_text("검색 결과가 없습니다.", size=15, color=ft.Colors.RED))
            else: 
                for juso in page_juso:
                    result1 = juso.get('zipNo')
                    result2 = juso.get('bdNm') if juso.get('bdNm') else f"{juso.get('roadAddr')}"
                    result3 = f"지번 | {juso.get('jibunAddr')}" 

                    self.result_column.controls.append(
                        ft.Container(
                            width=float("inf"),
                            ink=True,
                            data={
                                "zip": juso.get('zipNo'),
                                "road": juso.get('roadAddr'),
                                "jibun": juso.get('jibunAddr'),
                                "result2_name": result2
                            },
                            on_click=self.on_address_select,
                            padding=15,
                            content=ft.Column(
                                tight=True,
                                spacing=5,
                                controls=[
                                    dogdog.basic_text(result1, size=20, color=ft.Colors.RED),
                                    dogdog.basic_text(result2, size=16, weight="bold"),
                                    dogdog.basic_text(result3, size=13, color=ft.Colors.GREY_600)
                                ]
                            )
                        )
                    )
                    self.result_column.controls.append(ft.Divider())
                    
        except Exception as ex:
            self.result_column.controls.clear()
            self.result_column.controls.append(dogdog.basic_text("시스템 오류입니다. 다시 검색하세요.", size=15, color=ft.Colors.RED))
            # print(f"서버API오류 발생: {ex}")
            
        self.page.update()

    async def on_address_select(self, e):
        # 선택한 주소 데이터 저장
        self.search_input.data = e.control.data
        
        self.check_popup.content = ft.Column(
            tight=True,
            spacing=5,
            controls=[
                dogdog.basic_text(f"{self.search_input.data.get('result2_name')}", weight='bold', size=16),
                dogdog.basic_text("이 주소가 확실한가요?", size=15)
            ]
        )

        self.check_popup.actions = [
            ft.TextButton("네", on_click=self.confirm_popup),
            ft.TextButton("아니오", on_click=self.cancel_popup)
        ]
        
        self.page.show_dialog(self.check_popup)

    async def confirm_popup(self, click_e):
        self.check_popup.open = False
        
        # 상세 주소 입력 모드로 변경
        self.search_input.value = ""
        self.search_input.label = "상세 주소(ex. 한라원앤디 타워 A동 306호)"
        
        # 버튼을 '검색'에서 '확인(체크마크)' 모양으로 변경
        self.search_button.icon = ft.Icons.CHECK
        self.search_button.tooltip = "입력 완료"
        
        self.search_button.on_click = self.send_page
        self.search_input.on_submit = self.send_page

        self.result_column.controls.clear()
        self.result_column.controls.append(dogdog.basic_text("상세 주소를 입력하시고 우측 체크버튼 혹은 Enter를 눌러주세요!"))
        # self.search_input.error_text = ""
        self.result_column.controls.append(
            dogdog.basic_text(f"선택하신 주소: \n{self.search_input.data.get('road')}", weight="bold", color=ft.Colors.BLUE)
        )
        
        self.page.update()
        
        # 포커스 이동 (비동기 처리에 맞게 사용)
        if hasattr(self.search_input, 'focus_async'):
            await self.search_input.focus()
        else:
            await self.search_input.focus()

    async def cancel_popup(self, click_e):
        self.check_popup.open = False
        self.page.update()

    def send_page(self, e):
        save_data = self.search_input.data
        full_text = self.search_input.value
        
        # 입력된 값에서 안내 문구가 포함되어 있다면 제거 후 상세주소만 추출
        detail_addr = full_text.replace(save_data.get('road', ''), "").strip()

        result = {
            "zip": save_data.get('zip'),
            "road": save_data.get('road'),
            "jibun": save_data.get('jibun'),
            "detail": detail_addr,
            "full_address": f"{save_data.get('road')} {detail_addr}".strip(),
        }

        # print(f"우편번호: {save_data.get('zip')}")
        # print(f"지번주소: {save_data.get('jibun')}")
        # print(f"상세주소: {detail_addr}")

        if self.on_complete:
            self.on_complete(result)
        else:
            self.page.clean()

    def on_input_change(self, e):
        if self.error_label.value:
            self.error_label.value = ""
            self.page.update()


# =======================================
# 사용 예시 (Main)
# =======================================
def address_view(page: ft.Page):
    
    def handle_address_complete(result_data):
        # print("최종 반환된 데이터:", result_data)
        page.session.store.set("order_address", result_data.get('full_address'))
        page.views.pop()
        page.go(page.views[-1].route)

    # 객체 지향으로 만든 컴포넌트 인스턴스화 후 화면에 추가
    address_component = AddressSearcher(page=page, on_complete=handle_address_complete)
    
    return ft.Container(
        padding=20,
        bgcolor="#ffffff",
        content=ft.Column(controls=address_component.content) # type: ignore
    )