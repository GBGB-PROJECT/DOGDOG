"""frame과 연결되어 frame의 내용물을 채우는 파일"""
import flet as ft

# erp_homecontent.view,     
MENU_ITEMS = {
    "홈": lambda: ft.Container(content=ft.Text("홈 준비 중")),  
    "매출관리": lambda: ft.Container(content=ft.Text("매출관리 준비 중")), 
    "원가관리": lambda: ft.Container(content=ft.Text("원가관리 준비 중")),
    "구매관리": lambda: ft.Container(content=ft.Text("구매관리 준비 중")),
    "상품관리": lambda: ft.Container(content=ft.Text("상품관리 준비 중")),
    "생산관리": lambda: ft.Container(content=ft.Text("생산관리 준비 중")),
    "재고관리": lambda: ft.Container(content=ft.Text("재고관리 준비 중")),
    "물류관리": lambda: ft.Container(content=ft.Text("물류관리 준비 중")),
    "고객관리": lambda: ft.Container(content=ft.Text("고객관리 준비 중")),
    "영업관리": lambda: ft.Container(content=ft.Text("영업관리 준비 중")),
    "회계관리": lambda: ft.Container(content=ft.Text("회계관리 준비 중")),
    "인사관리": lambda: ft.Container(content=ft.Text("인사관리 준비 중")),
    "시스템관리": lambda: ft.Container(content=ft.Text("시스템관리 준비 중")),
}