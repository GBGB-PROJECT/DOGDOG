import flet as ft

# 파이썬이 여기서부터 출발하므로, erp. 으로 시작하는 경로를 완벽하게 이해합니다!
from domain.erp_homeframe import ErpFrame 
# (만약 파일 이름이나 경로가 조금 다르다면 건형님 환경에 맞게 수정해주세요)

def main(page: ft.Page):
    page.title = "개밥개밥푸드 ERP"
    page.window_resizable = False
    page.width = 1280
    page.height = 800
    page.padding = 0
    page.bgcolor = ft.Colors.WHITE
    
    # 우리가 멋지게 만들어둔 프레임(뼈대)을 불러와서 화면에 딱 얹어줍니다.
    app_frame = ErpFrame(page)
    page.add(app_frame)

if __name__ == "__main__":
    ft.app(target=main)