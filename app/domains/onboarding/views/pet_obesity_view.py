# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog

# -------------------------------------------------------------------------------------------------------
def pet_obesity_view(page: ft.Page, controller):
    """
    [View] pet_obesity_view
    - 순수 Dumb Component: UI만 렌더링하고 상태 변경은 모두 controller에 위임합니다.
    """
    storage = page.session.store
    
    body_score_descriptions = {
        1: "✅ 1단계:\n갈비뼈, 요추, 골반 뼈와 모든 뼈의 윤곽이 뚜렷하게 드러납니다. "
                    "체지방이 전혀 보이지 않으며 근육 손실이 보입니다.",
        2: "✅ 2단계:\n갈비뼈, 요추, 골반 뼈가 쉽게 보입니다. "
                    "지방이 만져지지 않으며 뼈의 윤곽이 드러나고 근육량이 약간 감소한 상태입니다.",
        3: "✅ 3단계:\n갈비뼈가 쉽게 만져지며 체지방이 적습니다. "
                    "요추 끝이 보이고 골반 뼈 윤곽이 나타나기 시작하며, 위에서 보았을 때 허리와 복부가 홀쭉합니다.",
        4: "✅ 4단계:\n적당한 지방이 덮인 갈비뼈가 쉽게 만져집니다. "
                    "허리가 쉽게 구분되며 옆에서 보았을 때 배가 들어가있습니다.",
        5: "✅ 5단계:\n과도한 지방 없이 갈비뼈가 잘 만져집니다. "
                    "위에서 보았을 때 갈비뼈 뒤로 허리가 잘록하게 보이며, 옆에서 보았을 때 배가 들어가있습니다.",
        6: "✅ 6단계:\n갈비뼈가 약간의 지방에 덮여 있어 만져지긴 하지만, 허리 구분이 모호해지기 시작합니다. "
                    "단, 복부는 아직 들어가 있어 구분은 가능합니다.",
        7: "✅ 7단계:\n두꺼운 지방층 때문에 갈비뼈를 만지기 힘듭니다. "
                    "요추와 꼬리 시작 부분에 눈에 띄는 지방 축적이 보이며, 허리 구분이 매우 힘듭니다.",
        8: "✅ 8단계:\n많은 지방이 덮여 있어 갈비뼈가 전혀 만져지지 않습니다. "
                    "요추와 꼬리 부분에 살이 접힐 정도로 지방이 많고 허리와 배의 구분이 안 되며 복부가 팽창되어 보입니다.",
        9: "✅ 9단계:\n목, 척추, 꼬리 부분에 매우 많은 양의 지방이 축적되어 살이 접힙니다. "
                    "허리 구분이 불가능하고 사지(다리)에도 지방이 축적되며 복부 팽창이 심한 상태입니다.",
    }

    initial_score = storage.get("body_score") or 6

    body_score_text = dogdog.basic_text(
        value=f"현재 선택: {initial_score}단계", size=14, weight="bold", color=ft.Colors.BLUE_700
    )
    body_score_description_text = dogdog.basic_text(
        value=body_score_descriptions[initial_score], size=14, weight="bold"
    )

    def slider_changed(e):
        selected_value = int(e.control.value)
        body_score_text.value = f"현재 선택: {selected_value}단계"
        body_score_description_text.value = body_score_descriptions[selected_value]
        controller.update_field("body_score", selected_value)
        page.update()

    body_score_slider = ft.Slider(
        min=1,
        max=9,
        divisions=8,
        value=initial_score,
        label="{value}",
        active_color=ft.Colors.BLUE_400,
        inactive_color=ft.Colors.BLUE_100,
        on_change_end=slider_changed
    )

    # 기본값 설정
    if not storage.get("body_score"):
        controller.update_field("body_score", 6)

    content_column = [
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[ft.Column(
                width=320, 
                controls=[
                    dogdog.basic_text(value="체형은 몇단계인가요?", weight="bold"),
                    ft.Image(
                        src="obesity.png", fit=ft.BoxFit.CONTAIN, 
                        color_blend_mode=ft.BlendMode.MULTIPLY, color="#FFFFFF"
                    ),
                    body_score_text,
                    body_score_slider,
                    ft.Container(
                        content=body_score_description_text
                    )
                ]
            )]
        )
    ]
    return content_column