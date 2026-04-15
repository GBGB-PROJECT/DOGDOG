import flet as ft
from components.common.registration_popup import custom_popup # 모듈 불러오기

def main(page: ft.Page):
    page.title = "GaeBobGaeBob 시스템"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # 팝업 클래스 인스턴스 생성
    popup = custom_popup(page)

    # 버튼 클릭 시 팝업 띄우기
    page.add(
        ft.Button("성공 팝업 보기", on_click=lambda _: popup.confirm_popupbox()),
        ft.Button("에러 팝업 보기", on_click=lambda _: popup.error_popup()),
    )

ft.app(target=main, assets_dir='components/assets')