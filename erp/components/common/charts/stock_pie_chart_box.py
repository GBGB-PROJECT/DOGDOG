import flet as ft
#from erp.domain.controller.home.erp_home_input import get_home_view_data
from components import common as cm
import flet_charts as fch
import datetime

def _legend_item(color: str, label: str, percent: str):
    return ft.Container(
        padding=ft.padding.symmetric(vertical=4),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Container(
                            width=10,
                            height=10,
                            border_radius=999,
                            bgcolor=color,
                        ),
                        ft.Text(
                            label,
                            size=12,
                            color=cm.TEXT_PRIMARY,
                            weight=ft.FontWeight.W_600,
                        ),
                    ],
                ),
                ft.Text(
                    percent,
                    size=12,
                    color=cm.TEXT_SECONDARY,
                    weight=ft.FontWeight.W_600,
                ),
            ],
        ),
    )


def build_stock_pie_chart_box(feed_data: dict):
    # 오늘 날짜 동적 생성
    today_str = datetime.date.today().strftime("%Y/%m/%d")

    # 동적으로 넣기 위한 색상 팔레트
    color_categories = [
        "#00C49F",  # 청록색 (Teal)
        "#FF9F40",  # 주황색 (Orange)
        "#0088FE",  # 파란색 (Blue)
        "#FFBB28",  # 노란색 (Yellow)
        "#FF8042",  # 다홍색 (Coral)
        "#8884d8",  # 보라색 (Purple)
    ]

    # 빈 데이터를 받을 경우 빈 차트가 나오는 것을 방지
    if not feed_data:
        categories = [(cm.PIE_LIGHT, "데이터 없음", "100")]
    else:
    # 4. feed_data 딕셔너리를 순회하며 (색상, 라벨, 값) 튜플 리스트 생성
        categories = []
        for i, (label, value) in enumerate(feed_data.items()):
            # 데이터 개수가 팔레트 색상 수보다 많으면 색상을 순환해서 사용
            color = color_categories[i % len(color_categories)]
            categories.append((color, label, value))

    ## 5개 씩 나누기
    first_col_items = categories[:5]
    second_col_items = categories[5:]

    ## 각 열을 구성하는 함수
    def create_legend_column(items):
        return ft.Column(
            spacing=5,
            controls=[_legend_item(clr, lbl, f"{val}%") for clr, lbl, val in items]
        )
    
    legend_content = ft.Row(
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=20,
        controls=[
            ft.Container(expand=True, content=create_legend_column(first_col_items)),
        ]
    )
    ## 6개일 경우 2번째 열
    if second_col_items:
        legend_content.controls.append(ft.Container(expand=True, content=create_legend_column(second_col_items)))

    



    return ft.Container(
        width=480,  # ☑️ 수정: 기존 440 -> 480 / 카드 전체 조금 더 확대
        height=320,  # ☑️ 수정: 기존 250 -> 270 / 카드 높이도 확대
        bgcolor=cm.CARD_BG,
        border_radius=16,
        border=ft.border.all(1, "#E0E1E2"),
        padding=18,  # ☑️ 수정: 기존 16 -> 18 / 내부 여백 확대
        content=ft.Column(
            spacing=18,  # ☑️ 수정: 기존 16 -> 18 / 내부 간격 확대
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            f"재고 현황 ({today_str})",
                            size=19,  # ☑️ 수정: 기존 18 -> 19
                            weight=ft.FontWeight.W_700,
                            color=cm.TEXT_PRIMARY,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            icon_size=24,  # ☑️ 수정: 기존 22 -> 24
                            icon_color=cm.TEXT_PRIMARY,
                            on_click=lambda e: e.page.go("/stock/product/status")
                        ),
                    ],
                ),
                ft.Row(
                    spacing=14,  # ☑️ 수정: 기존 12 -> 14 / 차트-범례 사이 간격 확대
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=160,  # ☑️ 수정: 기존 140 -> 160 / 차트 영역 확대
                            height=140,  # ☑️ 수정: 기존 120 -> 140
                            alignment=ft.Alignment(0, 0),
                            content=fch.PieChart(
                                sections= [fch.PieChartSection(value=val, color=clr, radius=17) for clr, lbl, val in categories],
                                sections_space=4,
                                center_space_radius=46,  # ☑️ 수정: 기존 40 -> 46 / 가운데 반경 확대
                                center_space_color=cm.CARD_BG,
                            ),
                        ),
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.START,
                                spacing=9,  # ☑️ 수정: 기존 8 -> 9 / 범례 간격 소폭 확대
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text("카테고리",size=12,color=cm.TEXT_MUTED),
                                            ft.Text("%",size=12,color=cm.TEXT_MUTED),
                                        ],
                                    ),
                                    ft.Container(
                                        expand=True,
                                        content=ft.Column( # 💡 리스트 대신 'Column'이라는 바구니 하나를 통째로 넣습니다.
                                        scroll=ft.ScrollMode.AUTO, # 혹시 아이템이 많아지면 스크롤도 가능하게!
                                        controls=[
                                        # 구분선이 빠졌다면 여기에 추가해주는 게 예쁩니다.
                                        ft.Container(height=1, bgcolor="#D1D5DB"), 
                                        # 리스트 컴프리헨션으로 만든 아이템들을 여기에 풉니다.
                                        legend_content
                                    ]
                                    )
                                )
                                
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )