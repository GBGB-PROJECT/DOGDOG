import flet as ft


# ============================================================
# ✅ ERP 공통 컬러
# ============================================================



# ============================================================
# ✅ ERP 3줄 정보 카드
# - title (작은 설명)
# - main (핵심 값)
# - sub (보조 정보)
# ============================================================
def erp_info_box(title, main, sub):
    return ft.Container(
        width=220,  # 🔥 추가 (핵심)
        height=100,
        bgcolor=BOX_BG,
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),

        content=ft.Column(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                # 🔹 1줄 (작은 제목)
                ft.Text(
                    value=title,
                    size=12,
                    color=TEXT_MUTED,
                    weight=ft.FontWeight.W_500,
                ),

                # 🔹 2줄 (핵심 값)
                ft.Text(
                    value=main,
                    size=20,
                    color=TEXT_PRIMARY,
                    weight=ft.FontWeight.W_700,
                ),

                # 🔹 3줄 (보조 설명)
                ft.Text(
                    value=sub,
                    size=12,
                    color=TEXT_SECONDARY,
                    weight=ft.FontWeight.W_500,
                ),
            ],
        ),
    )