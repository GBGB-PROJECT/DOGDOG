import flet as ft
import components as dogdog

def product(p_id, image_src, image_size, title, price):
    return ft.Container(
        padding=0,
        on_click=lambda _:print(p_id, title),
        ink=True,
        content=ft.Column(spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[
            ft.Container(width=image_size, height=image_size, image=ft.DecorationImage(src=image_src)),
            dogdog.basic_text(value=title, size=12, color=ft.Colors.GREY_800),
            dogdog.basic_text(value=price, size=12, color=ft.Colors.GREY_800)
    ]))

def products(data_dict, image_size):
    items = list(data_dict.items())
    products = []
    for i in range(0, len(items), 3):
        chunk = items[i:i+3]
        row_controls = []
        for p_id, p_d in chunk:
            row_controls.append(
                product(p_id, p_d["image_src"], image_size, p_d["product_name"], f"{p_d['sales_price']}원")
            )
        products.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                controls=row_controls
            )
        )

    return products