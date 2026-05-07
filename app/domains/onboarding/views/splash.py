import flet as ft
import time
import threading


BG_COLOR = "#FEF3B9"


def splash_view(page: ft.Page):
    # [버그 해결] page 전역 속성(padding, bgcolor 등)을 직접 수정하지 않습니다.
    # 대신 최종 반환하는 ft.View에 해당 속성들을 부여합니다.

    dog_image = ft.Container(
        content=ft.Image(
            src="dogclay.png",
            width=230,
            fit=ft.BoxFit.CONTAIN,
        ),
        animate_offset=ft.Animation(260, ft.AnimationCurve.EASE_OUT_BACK),
        animate_scale=ft.Animation(260, ft.AnimationCurve.EASE_OUT_BACK),
        offset=ft.Offset(0, 0),
        scale=ft.Scale(1.0),
    )

    def animated_letter(src, width, left, top):
        return ft.Container(
            left=left,
            top=top,
            content=ft.Image(
                src=src,
                width=width,
                fit=ft.BoxFit.CONTAIN,
            ),
            animate_offset=ft.Animation(260, ft.AnimationCurve.EASE_OUT_BACK),
            animate_scale=ft.Animation(260, ft.AnimationCurve.EASE_OUT_BACK),
            offset=ft.Offset(0, 0),
            scale=ft.Scale(1.0),
        )

    def build_left_word():
        d = animated_letter("d1.png", width=92, left=-6, top=8)
        o = animated_letter("o1.png", width=42, left=48, top=34)
        g = animated_letter("g1.png", width=52, left=78, top=16)

        word = ft.Container(
            width=134,
            height=104,
            content=ft.Stack(
                clip_behavior=ft.ClipBehavior.NONE,
                controls=[d, o, g],
            ),
        )
        return word, [d, o, g]

    def build_right_word():
        d = animated_letter("d2.png", width=62, left=0, top=10)
        o = animated_letter("o2.png", width=44, left=46, top=28)
        g = animated_letter("g2.png", width=50, left=78, top=18)

        word = ft.Container(
            width=126,
            height=104,
            content=ft.Stack(
                clip_behavior=ft.ClipBehavior.NONE,
                controls=[d, o, g],
            ),
        )
        return word, [d, o, g]

    left_word, left_letters = build_left_word()
    right_word, right_letters = build_right_word()
    letters = left_letters + right_letters

    title_logo = ft.Row(
        spacing=2,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[left_word, right_word],
    )

    title_wrap = ft.Container(
        margin=ft.margin.only(top=-2),
        content=title_logo,
    )

    splash_content = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
        controls=[
            dog_image,
            title_wrap,
        ],
    )

    # splash_view 컨테이너
    content_container = ft.Container(
        expand=True,
        bgcolor=BG_COLOR,
        alignment=ft.Alignment(0, 0),
        content=splash_content,
    )

    async def splash_bounce():
        await asyncio.sleep(0.5) # 초기 대기 (뷰가 완전히 마운트될 시간을 확보)
        
        # 뷰 리스트가 비어있을 때 update()를 방지하기 위한 안전 체크
        if not page.views:
            return

        group = [dog_image] + letters

        for item in group:
            item.offset = ft.Offset(0, 0.10)
            item.scale = ft.Scale(0.94)
        page.update()
        await asyncio.sleep(0.08)

        for item in group:
            item.offset = ft.Offset(0, -0.16)
            item.scale = ft.Scale(1.08)
        page.update()
        await asyncio.sleep(0.16)

        for item in group:
            item.offset = ft.Offset(0, 0.04)
            item.scale = ft.Scale(0.98)
        page.update()
        await asyncio.sleep(0.10)

        for item in group:
            item.offset = ft.Offset(0, -0.03)
            item.scale = ft.Scale(1.01)
        page.update()
        await asyncio.sleep(0.08)

        for item in group:
            item.offset = ft.Offset(0, 0)
            item.scale = ft.Scale(1.0)
        page.update()

        await asyncio.sleep(1.2)
        # 스플래시 종료 후 온보딩 완료 여부에 따라 이동
        is_complete = page.session.store.get("is_onboarding_complete")
        if is_complete:
            page.go("/home")
        else:
            page.go("/login")

    # [가장 중요] 애니메이션 태스크 예약 (View가 리턴된 후 실행됨)
    import asyncio
    page.run_task(splash_bounce)

    return ft.View(
        route="/splash",
        bgcolor=BG_COLOR,
        padding=0,
        spacing=0, # View 레벨에서 spacing 설정
        controls=[content_container]
    )