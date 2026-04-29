# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
# -------------------------------------------------------------------------------------------------------
def image_guide_row(image_src, text):
    return ft.Row(
        alignment=ft.MainAxisAlignment.CENTER, 
        controls=[
            ft.Image(src=image_src, width=100),
            ft.Container(
                alignment=ft.Alignment(-1,0), expand=True, height=80, 
                content=dogdog.basic_text(text, size=18, weight="bold")
            )
        ]
    )
# -------------------------------------------------------------------------------------------------------
def what_guide(page: ft.Page, content):
    if content == "bowel":
        content_column = [
            image_guide_row("bowel/01_poop.png", "1. 매우 딱딱하고 마름"),
            ft.Divider(),
            image_guide_row("bowel/02_poop.png", "2. 견고하나 딱딱하지 않고 잘 휘어짐"),
            ft.Divider(),
            image_guide_row("bowel/03_poop.png", "3. 표면이 촉촉하고 집어들 때 형태를 유지하나 바닥에 잔여물이 남음"),
            ft.Divider(),
            image_guide_row("bowel/04_poop.png", "4. 질척거림, 집어들 때 형태를 잃고 바닥에 잔여물이 남음"),
            ft.Divider(),
            image_guide_row("bowel/05_poop.png", "5. 매우 질척거리나 형태를 유지, 집어들 때 형태를 잃고 바닥에 잔여물이 남음"),
            ft.Divider(),
            image_guide_row("bowel/06_poop.png", "6. 물기가 몹시 많으나 질감은 있음"),
            ft.Divider(),
            image_guide_row("bowel/07_poop.png", "7. 완전한 액체 상태"),
        ]
    elif content == "bcs":
        content_column = [
            dogdog.basic_text(
                spans=[
                    ft.TextSpan("강아지BCS(Body Condition Score, 신체충실지수)", style=dogdog.TextStyle(size=16)),
                    ft.TextSpan("는 수의사들이 강아지의 표준 체형과 비만도를 판단하기 위해 사용하는 신체 조건 점수입니다.")
                ], size=14
            ), ft.Row(),
            dogdog.basic_text(
                spans=[
                    ft.TextSpan("[마름] 1~3단계\n", style=dogdog.TextStyle(size=16)),
                    ft.TextSpan("▪️ 1단계: 갈비뼈, 요추, 골반 뼈와 모든 뼈의 윤곽이 뚜렷하게 드러납니다. 체지방이 전혀 보이지 않으며 근육 손실이 보입니다.\n"),
                    ft.TextSpan("▪️ 2단계: 갈비뼈, 요추, 골반 뼈가 쉽게 보입니다. 지방이 만져지지 않으며 뼈의 윤곽이 드러나고 근육량이 약간 감소한 상태입니다.\n"),
                    ft.TextSpan("▪️ 3단계: 갈비뼈가 쉽게 만져지며 체지방이 적습니다. 요추 끝이 보이고 골반 뼈 윤곽이 나타나기 시작하며, 위에서 보았을 때 허리와 복부가 홀쭉합니다."),
                ], size=14
            ), ft.Row(),
            dogdog.basic_text(
                spans=[
                    ft.TextSpan("[정상] 4~5단계\n", style=dogdog.TextStyle(size=16)),
                    ft.TextSpan("▪️ 4단계: 적당한 지방이 덮인 갈비뼈가 쉽게 만져집니다. 허리가 쉽게 구분되며 옆에서 보았을 때 배가 들어가있습니다.\n"),
                    ft.TextSpan("▪️ 5단계: 과도한 지방 없이 갈비뼈가 잘 만져집니다. 위에서 보았을 때 갈비뼈 뒤로 허리가 잘록하게 보이며, 옆에서 보았을 때 배가 들어가있습니다."),
                ], size=14
            ), ft.Row(),
            dogdog.basic_text(
                spans=[
                    ft.TextSpan("[과체중 및 비만] 6~9단계\n", style=dogdog.TextStyle(size=16)),
                    ft.TextSpan("▪️ 6단계: 갈비뼈가 약간의 지방에 덮여 있어 만져지긴 하지만, 허리 구분이 모호해지기 시작합니다. 단, 복부는 아직 들어가 있어 구분은 가능합니다.\n"),
                    ft.TextSpan("▪️ 7단계: 두꺼운 지방층 때문에 갈비뼈를 만지기 힘듭니다. 요추와 꼬리 시작 부분에 눈에 띄는 지방 축적이 보이며, 허리 구분이 매우 힘듭니다.\n"),
                    ft.TextSpan("▪️ 8단계: 많은 지방이 덮여 있어 갈비뼈가 전혀 만져지지 않습니다. 요추와 꼬리 부분에 살이 접힐 정도로 지방이 많고 허리와 배의 구분이 안 되며 복부가 팽창되어 보입니다.\n"),
                    ft.TextSpan("▪️ 9단계: 목, 척추, 꼬리 부분에 매우 많은 양의 지방이 축적되어 살이 접힙니다. 허리 구분이 불가능하고 사지(다리)에도 지방이 축적되며 복부 팽창이 심한 상태입니다."),
                ], size=14
            ), ft.Row(),
        ]
    # ---------------------------------------------------------------------------------------------------
    return ft.Container(
        padding=ft.Padding.only(left=20, right=20),
        bgcolor="#ffffff",
        content=ft.Column(
            controls=content_column # type: ignore
        )
    )