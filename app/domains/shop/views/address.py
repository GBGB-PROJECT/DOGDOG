import flet as ft
#flet run --web domains/shop/views/address.py


def main(page: ft.Page, on_complete=None):
    import requests
    # =======================================
    # 1단계) 페이지 초기의 세팅
    # =======================================
    page.title = "주소 검색기"

    api_url = "https://business.juso.go.kr/addrlink/addrLinkApi.do"
    api_key = "devU01TX0FVVEgyMDI2MDMxNzExNDQwNzExNzc0MjM="

    # =======================================
    # 2단계) 단일UI요소 준비하기
    # =======================================
    ## 2-1 단일 UI
    result_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True) # 결과 내역
    search_input = ft.TextField(label="도로명 주소, 건물명 검색", expand=True, autofocus=True) # 찾기 창(input)
    error_label = ft.Text(size=15, color="red") # 에러 라벨 자체
    # search_button = ft.Button("검색", icon=ft.Icons.SEARCH) # 찾기 버튼
    search_button = ft.IconButton(ft.Icons.SEARCH, icon_size=30) # 찾기 버튼
    ## 팝업 UI 컴포넌트를 미리 생성해줌
    check_popup = ft.AlertDialog(
        modal=True,
        title=ft.Text("주소 확인", weight='bold'),
        actions_alignment=ft.MainAxisAlignment.END
    )

    ## 3-4. 유효성 이후(validation_test_keyword) 클릭 이후의 서버에서의 유효성 검사와, 통과 후 검색 결과를 도출
    def click_event(e):
        click_keyword = search_input.value.strip()
        result_column.controls.clear()
        result_column.controls.append(ft.ProgressRing())

        try:
            params = {  ## 최초 api에 접근하기 위한 인증 params
                "confmKey": api_key,
                "currentPage": 1,
                "countPerPage": 50,
                "keyword": click_keyword,
                "resultType": "json"
            }
            response = requests.get(api_url, params=params)
            data = response.json()
            common = data.get("results", {}).get("common", {}) 

            if common.get("errorCode") != "0":
                error_message_common = common.get("errorMessage")
                print(f"에러 발생: {common.get('errorCode')}")
                search_input.error_text = "API 에러 발생! 다시 입력하세요"
                result_column.controls.clear()
                result_column.controls.append(ft.Text(error_message_common, size=15, color="red"))
                return

            page_juso = data.get("results", {}).get("juso", [])
            result_column.controls.clear()

            if not page_juso:
                result_column.controls.append(ft.Text("검색 결과가 없습니다.", size=15, color="red"))
            else: 
                for juso in page_juso:
                    result1 = juso.get('zipNo')
                    result2 = juso.get('bdNm') if juso.get('bdNm') else f"{juso.get('roadAddr')}"
                    result3 = f"지번 | {juso.get('jibunAddr')}" 

                    ### 들여쓰기 완벽 교정: for문 안쪽에 맞춰서 컨테이너 조립
                    result_column.controls.append(
                        ft.Container(
                            width=float("inf"),
                            ink=True,
                            on_hover=True,
                            data={
                                "zip": juso.get('zipNo'),
                                "road": juso.get('roadAddr'),
                                "jibun": juso.get('jibunAddr'),
                                "result2_name":result2
                            },
                            on_click=on_address_select,
                            padding=15,
                            content=ft.Column(
                                tight=True,
                                spacing=5,
                                controls=[
                                    ft.Text(result1, size=20, color="red"),
                                    ft.Text(result2, size=16, weight="bold"),
                                    ft.Text(result3, size=13, color="gray")
                                ]
                            )
                        )
                    )
                    result_column.controls.append(ft.Divider())
                    
        except Exception as ex:
            result_column.controls.clear()
            result_column.controls.append(ft.Text("시스템 오류입니다. 다시 검색하세요.", size=15, color="red"))
            print(f"서버API오류 발생: {ex}")

    ## 3-5. 기존 검색창에에서 주소를 클릭하면 입력모드로 변경상세주소하기
    async def on_address_select(e):
        ## send_page 전송 목적으로 data를 준비해준다.
        search_input.data = e.control.data
        #print("상세페이지 on_address_select도착")

        ### 펍업에서 Yes를 눌렀을 경우 => 상세 입력 페이지로 이동함
        async def comfirm_popup(click_e):
            check_popup.open = False

            ### 기존 검색창 -> 선택한 주소를 미리 작성 후 띄어쓰기 1칸 추가하기
            search_input.value = ""

            ### 안내문구를 변경시켜주기
            search_input.label = "상세 주소(ex. 한라원앤디 타워 A동 306동)"
            await search_input.focus()

            ### 버튼 또한 검색에서 완료로 변경하기
            search_button.text = "확인"
            search_button.on_click = send_page
            search_input.on_submit = send_page

            ### 밑의 검색 결과를 지우고 메시지를 출력시킨다.
            result_column.controls.clear()
            result_column.controls.append(ft.Text("상세 주소를 입력하시고 [확인] 혹은 Enter를 눌러주세요!"))
            search_input.error_text = "" # 선택 시점에 기존 에러내역을 지워줌
            result_column.controls.append(ft.Text(f"선택하신 주소: \n{e.control.data.get('jibun')}", weight="bold", color="blue"))
        
        ### 팝업창에서 No를 눌렀을 경우 
        async def cancel_popup(click_e):
            check_popup.open = False

        ### popup_check 컴포넌트에 내용물을 담기
        check_popup.content = ft.Column(
            tight=True,
            spacing=5,
            controls=[
                ft.Text(f"{search_input.data.get('result2_name')}", weight='bold', size=16),
                ft.Text(f"이 주소가 확실한가요?", size=15)
            ]
        )

        check_popup.actions = [
        ft.TextButton("네", on_click=comfirm_popup),
        ft.TextButton("아니오", on_click=cancel_popup)
        ]
        #### pop_up 창을 실제로 띄움
        page.show_dialog(check_popup)

    ## 3-6. 최종 입력한 데이터를 print하고 바로 close
    def send_page(e):
        # search_input의 3가지 데이터 정보 꺼내기
        save_data = search_input.data
        # 사용자 입력한 상세 주소 분리해주기
        full_text = search_input.value
        detail_addr = full_text.replace(save_data.get('road'),"").strip()

        result = {
            "zip": save_data.get('zip'),
            "road": save_data.get('road'),
            "jibun": save_data.get('jibun'),
            "detail": detail_addr,
            "full_address": f'{save_data.get('road')} {detail_addr}'.strip(),
        }

        print(f"우편번호: {save_data.get('zip')}")
        print(f"지번주소: {save_data.get('jibun')}")
        print(f"상세주소: {detail_addr}")

        if on_complete:
            on_complete(result)
            
        else:
            page.clean()

    ## 3-8. input 내용이 변경될때마다 적용하는 함수로: error 텍스트가 None되도록 하는 함수이다.
    def on_input_change(e):
        if error_label.value:
            error_label.value=""

    # =================================
    # 4단계) 화면에 배치하기 
    # =================================
    search_button.on_click = click_event
    search_input.on_submit = click_event
    search_input.on_change = on_input_change

    ### 페이지에 BottomSheet를 등록하기
    bottom_tip_sheet = ft.BottomSheet(
        content=ft.Container(
            padding=20,
            # height=450,
            content=ft.Column(
                tight=True,
                controls=[
                    ft.Text("주소 검색 Tip", size=22, weight="bold"),
                    ft.Divider(),
                    ft.Text("아래와 같은 조합으로 검색하시면 결과를 가장 정확하게 찾을 수 있습니다.", size=15),
                    ft.Container(height=10), # 여백 주며 숨 돌리기

                    # 1. 도로명 검색 (가장 권장됨)
                    ft.Text("1. 도로명 + 건물번호", size=16, weight="bold"),
                    ft.Text("ex) 서울 금천구 가산디지털2로 101", size=14, color="blue"),
                    ft.Container(height=2),

                    # 2. 지번 검색 (구 주소)
                    ft.Text("2. 지역명(동/리) + 번지", size=16, weight="bold"),
                    ft.Text("ex) 가산동 549-1", size=14, color="blue"),
                    ft.Container(height=12),
                    ft.Button("확인했어요!", on_click=lambda e:bottom_close(e), width=float("inf"), style=ft.ButtonStyle(color="white", bgcolor="blue"))
                ],
            ),
        )
    )

    def bottom_close(e):
        bottom_tip_sheet.open = False

    # ==================================
    #  5단계) 최종 조립 - 실제 출력될 부분
    # ==================================
    content = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        controls=[
            ft.Text("주소 검색", size=20, weight="bold"),
            ft.Row(
                controls=[
                    search_input,
                    search_button
                ]
            ),
            ft.Divider(),
            result_column
        ]
    )
    page.show_dialog(bottom_tip_sheet)
    page.add(content)
    

if __name__ == "__main__":
    # ft.run(main)
    import webbrowser, os
    if os.getenv("FLET_NO_BROWSER"):
        webbrowser.open = lambda *args, **kwargs: None
    ft.run(main, assets_dir="assets", view=ft.AppView.WEB_BROWSER, port=34636) # test