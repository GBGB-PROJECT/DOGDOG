import flet as ft
import components as dogdog


def notification_dummy(page: ft.Page):
    storage = page.session.store
    category = dogdog.basic_text("똑똑배송", color=ft.Colors.GREY_500, weight="bold")
    category.expand = 1
    dummy_ment = dogdog.basic_text(
        "🚚 10일 뒤 “가장 맛있는 시간 30일, 닭고기 2.5kg”이 배송됩니다."
    )
    dummy_ment.max_lines = 1
    dummy_ment.overflow = ft.TextOverflow.ELLIPSIS
    dummy_ment.expand = 5
    content_column = [
        dogdog.content_container(
            on_click=lambda _, i=i: print(f"notification_select {i}"),
            content_list=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[category, dummy_ment],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    controls=[dogdog.basic_text(f"25.{i:02d}.20")],
                ),
            ],
        )
        for i in range(12, 8, -1)
    ]

    notification_set = dogdog.flat_icon_text_button(
        ft.Icons.NOTIFICATIONS_ACTIVE, "알림 설정"
    )
    notification_set.content.controls[0].color = ft.Colors.YELLOW_ACCENT_700  # type: ignore
    notification_set.content.controls[0].size = 20  # type: ignore
    notification_set.on_click = lambda _: page.go("/notification_setting")

    content_column.insert(
        0,
        ft.Row(alignment=ft.MainAxisAlignment.END, controls=[notification_set]),  # type: ignore
    )

    content_column.append(
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.TextButton(
                    content=dogdog.basic_text(
                        "더보기", size=14, color=ft.Colors.GREY_500
                    ),
                    on_click=lambda _: print("notification_dummy +"),
                )
            ],
        )  # type: ignore
    )

    return ft.Container(
        padding=ft.Padding.only(top=10, bottom=10),
        bgcolor="#ffffff",
        content=ft.Column(
            controls=content_column  # type: ignore
        ),
    )


def notification_setting(page: ft.Page):
    storage = page.session.store

    time_drop_list = [
        dogdog.dropdown_menu_option(key=i, text=f"{i}시간") for i in [4, 8, 12]
    ]

    time_drop = dogdog.dropdown_menu(label=None, event=None, options=time_drop_list)
    time_drop.value = time_drop_list[0].key
    time_drop.border = None
    time_drop.border_color = ft.Colors.TRANSPARENT
    time_drop.expand = False
    time_drop.width = 120

    noti_interval = dogdog.content_container(
        content_list=[
            ft.Row(
                controls=[
                    dogdog.basic_text(
                        spans=[
                            ft.TextSpan(
                                "알림 간격\n",
                                style=dogdog.TextStyle(
                                    size=16, color=ft.Colors.GREY_800
                                ),
                            ),
                            ft.TextSpan(
                                "첫 알람 시작 시간에서 일정 시간이 지나면 알림을 보내드려요."
                            ),
                        ],
                        color=ft.Colors.GREY_600,
                        size=12,
                    )
                ]
            ),
            ft.Column(
                spacing=0,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            dogdog.basic_text(
                                "밥주기", weight="bold", color=ft.Colors.GREY_700
                            ),
                            dogdog.basic_text("오전 08:00"),
                            time_drop,
                            ft.Switch(active_track_color="#FBDD30"),
                        ],
                    ),
                    dogdog.basic_text(
                        "12시간 알림 간격", size=12, color=ft.Colors.GREY_600
                    ),
                ],
            ),
            ft.Column(
                spacing=0,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            dogdog.basic_text(
                                "물주기", weight="bold", color=ft.Colors.GREY_700
                            ),
                            dogdog.basic_text("오전 08:00"),
                            time_drop,
                            ft.Switch(active_track_color="#FBDD30"),
                        ],
                    ),
                    dogdog.basic_text(
                        "4시간 알림 간격", size=12, color=ft.Colors.GREY_600
                    ),
                ],
            ),
            ft.Column(
                spacing=0,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            dogdog.basic_text(
                                "약주기", weight="bold", color=ft.Colors.GREY_700
                            ),
                            dogdog.basic_text("오전 08:00"),
                            time_drop,
                            ft.Switch(active_track_color="#FBDD30"),
                        ],
                    ),
                    dogdog.basic_text(
                        "12시간 알림 간격", size=12, color=ft.Colors.GREY_600
                    ),
                ],
            ),
        ]
    )

    subs_interval = dogdog.content_container(
        content_list=[
            dogdog.basic_text(
                "구독 알림 설정", size=16, color=ft.Colors.GREY_800, weight="bold"
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    dogdog.basic_text(
                        spans=[
                            ft.TextSpan(
                                "3일 전\n",
                                style=dogdog.TextStyle(color=ft.Colors.GREY_700),
                            ),
                            ft.TextSpan("구독 배송 3일 전 안내"),
                        ],
                        color=ft.Colors.GREY_600,
                        size=12,
                    ),
                    ft.Switch(active_track_color="#FBDD30"),
                ],
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    dogdog.basic_text(
                        spans=[
                            ft.TextSpan(
                                "7일 전\n",
                                style=dogdog.TextStyle(color=ft.Colors.GREY_700),
                            ),
                            ft.TextSpan("구독 배송 7일 전 안내"),
                        ],
                        color=ft.Colors.GREY_600,
                        size=12,
                    ),
                    ft.Switch(active_track_color="#FBDD30"),
                ],
            ),
        ]
    )

    feeding_food_interval_text = dogdog.basic_text(
        spans=[
            ft.TextSpan(
                "사료 소진일 알림 설정\n",
                style=dogdog.TextStyle(size=16, color=ft.Colors.GREY_800),
            ),
            ft.TextSpan("상품이 소진되기 3일, 7일 전 미리 알림을 받을 수 있어요."),
        ],
        color=ft.Colors.GREY_600,
        size=12,
    )
    feeding_food_interval_text.overflow = ft.TextOverflow.ELLIPSIS
    feeding_food_interval_text.expand = True

    feeding_food_interval = dogdog.content_container(
        content_list=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    feeding_food_interval_text,
                    ft.Switch(active_track_color="#FBDD30"),
                ],
            )
        ]
    )

    content_column = [noti_interval, subs_interval, feeding_food_interval]

    return ft.Container(
        padding=ft.Padding.only(top=10, bottom=10),
        bgcolor="#ffffff",
        content=ft.Column(
            controls=content_column  # type: ignore
        ),
    )
