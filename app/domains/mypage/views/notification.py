import flet as ft
import components as dogdog
import datetime

def notification_dummy(page: ft.Page):
    storage = page.session.store
    category = dogdog.basic_text("똑똑배송", color=ft.Colors.GREY_500, weight="bold")
    category.expand = 1
    dummy_ment = dogdog.basic_text("🚚 10일 뒤 “가장 맛있는 시간 30일, 닭고기 2.5kg”이 배송됩니다.")
    dummy_ment.max_lines = 1
    dummy_ment.overflow = ft.TextOverflow.ELLIPSIS
    dummy_ment.expand = 5
    content_column = [
        dogdog.content_container(
            on_click=lambda _,i=i:print(f"notification_select {i}"),
            content_list=[
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                    category,
                    dummy_ment
                ]),
                ft.Row(alignment=ft.MainAxisAlignment.END, controls=[
                    dogdog.basic_text(f"25.{i if i >= 10 else f'0{i}'}.20")
                ])
            ]
        ) for i in range(12 , 8, -1)
    ]

    notification_set = dogdog.flat_icon_text_button(ft.Icons.NOTIFICATIONS_ACTIVE, "알림 설정")
    notification_set.content.controls[0].color = ft.Colors.YELLOW_ACCENT_700 # type: ignore
    notification_set.content.controls[0].size = 20 # type: ignore
    notification_set.on_click = lambda _:page.go("/notification_setting")

    content_column.insert(
        0, ft.Row(alignment=ft.MainAxisAlignment.END, controls=[notification_set]) # type: ignore
    )

    content_column.append(
        ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
            ft.TextButton(
                content=dogdog.basic_text("더보기", size=14,color=ft.Colors.GREY_500), 
                on_click=lambda _:print("notification_dummy +"))
        ]) # type: ignore
    )

    return ft.Container(
        padding=ft.Padding.only(top=10, bottom=10),
        bgcolor="#ffffff",
        content=ft.Column(
            controls=content_column # type: ignore
        )
    )

def noti_time_drop(content, event):
    time_drop_list = [dogdog.dropdown_menu_option(key=i, text=f"{i}시간") for i in [4, 8, 12]]
    time_drop = dogdog.dropdown_menu(
        label=None,
        event=lambda e:event(e, content),
        options=time_drop_list,
        # expand=False,
        # border=ft.InputBorder.NONE,
        # border_color=ft.Colors.TRANSPARENT
    )
    time_drop.width = 120
    return time_drop

class Noti:
    def __init__(self, page: ft.Page):
        # -----------------------------------------------------------------------------------------------
        # Default Value
        # -----------------------------------------------------------------------------------------------
        self.page = page
        self.storage = page.session.store
        base_time = 8
        interval_time = 4
        self.default_time = (
            datetime.time(base_time).strftime(format="%p %H:%M").replace('PM','오후').replace('AM','오전'))
        # -----------------------------------------------------------------------------------------------
        # Time Picker
        # -----------------------------------------------------------------------------------------------
        self.time_picker = ft.TimePicker(
            entry_mode=ft.TimePickerEntryMode.DIAL_ONLY)
        # -----------------------------------------------------------------------------------------------
        self.food_time = dogdog.flat_icon_text_button(
            ft.Icons.ACCESS_TIME, 
            self.default_time if not self.storage.get('food_time') 
                else str(self.storage.get('food_time')))
        self.food_time.on_click = lambda e, picker=self.food_time: self.open_event(e, picker)
        self.food_time.data = {'button':'food'}
        # -----------------------------------------------------------------------------------------------
        self.water_time = dogdog.flat_icon_text_button(
            ft.Icons.ACCESS_TIME, 
            self.default_time if not self.storage.get('water_time') 
                else str(self.storage.get('water_time')))
        self.water_time.on_click = lambda e, picker=self.water_time: self.open_event(e, picker)
        self.water_time.data = {'button':'water'}
        # -----------------------------------------------------------------------------------------------
        self.drug_time = dogdog.flat_icon_text_button(
            ft.Icons.ACCESS_TIME, 
            self.default_time if not self.storage.get('drug_time') 
                else str(self.storage.get('drug_time')))
        self.drug_time.data = {'button':'drug'}
        self.drug_time.on_click = lambda e, picker=self.drug_time: self.open_event(e, picker)
        # -----------------------------------------------------------------------------------------------
        # Interval
        # -----------------------------------------------------------------------------------------------
        self.food_interval = (
            interval_time if not self.storage.get('food_interval') 
                else self.storage.get('food_interval'))
        self.water_interval = (
            interval_time if not self.storage.get('water_interval') 
                else self.storage.get('water_interval'))
        self.drug_interval = (
            interval_time if not self.storage.get('drug_interval') 
                else self.storage.get('drug_interval'))
        # -----------------------------------------------------------------------------------------------
        # Interval Dropdown
        # -----------------------------------------------------------------------------------------------
        self.food_time_drop = noti_time_drop('food', self.drop_event)
        self.water_time_drop = noti_time_drop('water', self.drop_event)
        self.drug_time_drop = noti_time_drop('drug', self.drop_event)
        # -----------------------------------------------------------------------------------------------
        # Interval Dropdown Value
        # -----------------------------------------------------------------------------------------------
        self.food_time_drop.value = (
            self.food_time_drop.value if not self.storage.get('food_interval') 
                else self.storage.get('food_interval'))
        self.water_time_drop.value = (
            self.water_time_drop.value if not self.storage.get('water_interval') 
                else self.storage.get('water_interval'))
        self.drug_time_drop.value = (
            self.drug_time_drop.value if not self.storage.get('drug_interval') 
                else self.storage.get('drug_interval'))
        # -----------------------------------------------------------------------------------------------
        # Notification Container
        # -----------------------------------------------------------------------------------------------
        self.noti_container = dogdog.content_container(
            content_list=[
                ft.Row(controls=[dogdog.basic_text(color=ft.Colors.GREY_600, size=12, spans=[
                    ft.TextSpan("알림 간격\n", style=dogdog.TextStyle(size=16, color=ft.Colors.GREY_800)),
                    ft.TextSpan("첫 알람 시작 시간에서 일정 시간이 지나면 알림을 보내드려요.")
                ])]),
                ft.Column(spacing=0, controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                        dogdog.basic_text("밥주기", weight="bold", color=ft.Colors.GREY_700),
                        self.food_time,
                        self.food_time_drop,
                        ft.Switch(
                            value=False if not self.storage.get('noti_food') else True,
                            active_track_color="#FBDD30", 
                            data={'noti':'food'}, on_change=self.switch_event)
                    ]),
                    dogdog.basic_text(
                        f"{self.food_interval}시간 알림 간격", size=12, color=ft.Colors.GREY_600)
                ]),
                ft.Column(spacing=0, controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                        dogdog.basic_text("물주기", weight="bold", color=ft.Colors.GREY_700),
                        self.water_time,
                        self.water_time_drop,
                        ft.Switch(
                            value=False if not self.storage.get('noti_water') else True,
                            active_track_color="#FBDD30", 
                            data={'noti':'water'}, on_change=self.switch_event)
                    ]),
                    dogdog.basic_text(
                        f"{self.water_interval}시간 알림 간격", size=12, color=ft.Colors.GREY_600)
                ]),
                ft.Column(spacing=0, controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                        dogdog.basic_text("약주기", weight="bold", color=ft.Colors.GREY_700),
                        self.drug_time,
                        self.drug_time_drop,
                        ft.Switch(
                            value=False if not self.storage.get('noti_drug') else True,
                            active_track_color="#FBDD30", 
                            data={'noti':'drug'}, on_change=self.switch_event)
                    ]),
                    dogdog.basic_text(
                        f"{self.drug_interval}시간 알림 간격", size=12, color=ft.Colors.GREY_600)
                ]),
            ]
        )
    # ---------------------------------------------------------------------------------------------------
    # Picker Open Event
    # ---------------------------------------------------------------------------------------------------
    def open_event(self, e, picker):
        def time_button_update(e, picker, button_type):
            select_time = e.control.value.strftime(format='%p %H:%M').replace('PM','오후').replace('AM','오전')
            picker.content.controls[1].value = select_time
            self.storage.set(f'{button_type}_time', select_time)
            self.test_timer(button_type)
        
        button_type = e.control.data.get('button')
        self.time_picker.on_change = (
            lambda e:time_button_update(e, picker, button_type))
        
        if self.time_picker not in self.page.overlay: self.page.overlay.append(self.time_picker)
        try: self.time_picker.open = True
        except Exception as err: print(err)
    # ---------------------------------------------------------------------------------------------------
    # Notification Switch Event
    # ---------------------------------------------------------------------------------------------------
    def switch_event(self, e):
        switch_type = e.control.data.get('noti')
        self.storage.set(f'noti_{switch_type}', e.data)
        self.test_timer(switch_type)
    # ---------------------------------------------------------------------------------------------------
    # Interval Dropdown Event
    # ---------------------------------------------------------------------------------------------------
    def drop_event(self, e, content):
        interval_guide = self.noti_container.content.controls # type: ignore
        if content == 'food': 
            self.food_interval = e.data
            interval_guide[1].controls[1].value = f"{self.food_interval}시간 알림 간격"
            self.storage.set('food_interval', self.food_interval)
        elif content == 'water': 
            self.water_interval = e.data
            interval_guide[2].controls[1].value = f"{self.water_interval}시간 알림 간격"
            self.storage.set('water_interval', self.water_interval)
        elif content == 'drug': 
            self.drug_interval = e.data
            interval_guide[3].controls[1].value = f"{self.drug_interval}시간 알림 간격"
            self.storage.set('drug_interval', self.drug_interval)
        self.test_timer(content)
    # ---------------------------------------------------------------------------------------------------
    # Notification Test Timer
    # ---------------------------------------------------------------------------------------------------
    def test_timer(self, switch_type):
        noti_setting = self.storage.get(f'noti_{switch_type}')
        if noti_setting:
            # print(switch_type, noti_setting)
            if switch_type == 'food':
                noti_type = self.food_time.content.controls[1].value.replace('오후','PM').replace('오전','AM') # type: ignore
                select_time = int(self.food_time_drop.value) # type: ignore
            elif switch_type == 'water':
                noti_type = self.water_time.content.controls[1].value.replace('오후','PM').replace('오전','AM') # type: ignore
                select_time = int(self.water_time_drop.value) # type: ignore
            elif switch_type == 'drug':
                noti_type = self.drug_time.content.controls[1].value.replace('오후','PM').replace('오전','AM') # type: ignore
                select_time = int(self.drug_time_drop.value) # type: ignore
            noti_setting_time = datetime.datetime.strptime(noti_type, "%p %H:%M")
            vs_time = []
            for count in range(int(24/select_time)):
                times = noti_setting_time + datetime.timedelta(hours=count*select_time)
                vs_time.append(times.strftime("%d %H:%M"))
            print(f' 🛎️ Setting {switch_type} Guide Time (First Alarm ⏲️[{vs_time[1].split()[1]}])')
            print(' 설정 시간의 다음 알림 시간 및 이후 알림 시간을 계산하고 화면을 업데이트 하는 부분까지 완료')
            print(f' 인앱 알림 팝업 제작 및 subs_interval 기능구현 필요\n{"===="*30}')

def notification_setting(page: ft.Page):

    noti = Noti(page=page)

    subs_interval = dogdog.content_container(
        content_list=[
            dogdog.basic_text("구독 알림 설정", size=16, color=ft.Colors.GREY_800, weight="bold"),
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                dogdog.basic_text(spans=[
                    ft.TextSpan("3일 전\n", style=dogdog.TextStyle(color=ft.Colors.GREY_700)),
                    ft.TextSpan("구독 배송 3일 전 안내"),
                ], color=ft.Colors.GREY_600, size=12),
                ft.Switch(active_track_color="#FBDD30")
            ]),
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                dogdog.basic_text(spans=[
                    ft.TextSpan("7일 전\n", style=dogdog.TextStyle(color=ft.Colors.GREY_700)),
                    ft.TextSpan("구독 배송 7일 전 안내"),
                ], color=ft.Colors.GREY_600, size=12),
                ft.Switch(active_track_color="#FBDD30")
            ])
    ])
    
    feeding_food_interval_text = dogdog.basic_text(spans=[
        ft.TextSpan("사료 소진일 알림 설정\n", style=dogdog.TextStyle(size=16, color=ft.Colors.GREY_800)),
        ft.TextSpan("제품이 소진되기 3일, 7일 전 미리 알림을 받을 수 있어요."),
    ], color=ft.Colors.GREY_600, size=12)
    feeding_food_interval_text.overflow = ft.TextOverflow.ELLIPSIS
    feeding_food_interval_text.expand = True
    
    feeding_food_interval = dogdog.content_container(
        content_list=[
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                feeding_food_interval_text,
                ft.Switch(active_track_color="#FBDD30")
            ])
    ])
    
    content_column = [
        noti.noti_container,
        subs_interval,
        feeding_food_interval
    ]

    return ft.Container(
        padding=ft.Padding.only(top=10, bottom=10),
        bgcolor="#ffffff",
        content=ft.Column(
            controls=content_column # type: ignore
        )
    )