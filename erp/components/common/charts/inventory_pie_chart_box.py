import flet as ft
from service.erp_homeview_service import get_home_view_data
from components import common as cm
import flet_charts as fch

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


def build_inventory_pie_chart_box():
    sale_data, inventory_data, feed_data = get_home_view_data()

    categories = [
    (cm.PIE_BLUE, "건사료", feed_data.get("dry_feed", 0)),
    (cm.PIE_SKY, "습식사료", feed_data.get("wet_feed", 0)),
    (cm.PIE_LIGHT, "간식", feed_data.get("snack", 0)),
    ]

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
                            "재고 현황 (2026/04/01)",
                            size=19,  # ☑️ 수정: 기존 18 -> 19
                            weight=ft.FontWeight.W_700,
                            color=cm.TEXT_PRIMARY,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            icon_size=24,  # ☑️ 수정: 기존 22 -> 24
                            icon_color=cm.TEXT_PRIMARY,
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
                                        *[_legend_item(clr, lbl, f"{val}%") for clr, lbl, val in categories]
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