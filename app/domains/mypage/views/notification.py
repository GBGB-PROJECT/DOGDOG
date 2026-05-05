import flet as ft
import components as dogdog
import datetime
import asyncio

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
        expand=False,
        border=ft.InputBorder.NONE,
        border_color=ft.Colors.TRANSPARENT
    )
    time_drop.width = 100
    time_drop.text_align = ft.TextAlign.CENTER
    time_drop.margin = ft.margin.only(right=-20)
    return time_drop

class Noti:
    def __init__(self, page: ft.Page, popup, settings=None, is_subscribed=False):
        # -----------------------------------------------------------------------------------------------
        # Default Value
        # -----------------------------------------------------------------------------------------------
        self.page = page
        self.popup = popup
        self.storage = page.session.store
        self.is_subscribed = is_subscribed
        self.notification_settings = {
            item.get("category"): item
            for item in (settings or [])
        }

        self.storage.set("notification_settings", self.notification_settings)

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
        self.noti_container = dogdog.content_container(content_list=[
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
        ])
        # -----------------------------------------------------------------------------------------------
        # Notification Popup
        # -----------------------------------------------------------------------------------------------
        self.notification_popup = self.popup.notification_popup
        self.notification_controls = self.popup.notification_controls
    
    def get_db_noti_value(self, category: str, days: int, default=False):
        setting = self.notification_settings.get(category) or {}

        if days == 3:
            return bool(setting.get("noti_before_3days", default))

        if days == 7:
            return bool(setting.get("noti_before_7days", default))

        return default
    # ---------------------------------------------------------------------------------------------------
    # Picker Open Event
    # ---------------------------------------------------------------------------------------------------
    def open_event(self, e, picker):
        def time_button_update(e, picker, button_type):
            select_time = e.control.value.strftime(format='%p %H:%M').replace('PM','오후').replace('AM','오전')
            picker.content.controls[1].value = select_time
            self.storage.set(f'{button_type}_time', select_time)
            self.Notification(button_type)
        
        button_type = e.control.data.get('button')
        self.time_picker.on_change = (
            lambda e:time_button_update(e, picker, button_type))
        
        if self.time_picker not in self.page.overlay: self.page.overlay.append(self.time_picker)
        try: self.time_picker.open = True
        except Exception as err: print(err)
    # ---------------------------------------------------------------------------------------------------
    # Notification Switch Event
    # ---------------------------------------------------------------------------------------------------
    async def switch_event(self, e):
        from domains.mypage.controller.subs_notification_api import NotificationController

        switch_type = e.control.data.get("noti")
        checked = e.control.value

        self.storage.set(f"noti_{switch_type}", checked)

        category_map = {
            "subs3": ("subs_delivery", "noti_option1"),
            "subs7": ("subs_delivery", "noti_option2"),
            "left_food_count": ("left_feeding_day", "both"),
        }

        if switch_type not in category_map:
            self.Notification(switch_type)
            return

        category, option = category_map[switch_type]

        current_settings = self.storage.get("notification_settings") or {}
        current = current_settings.get(category, {
            "noti_before_3days": False,
            "noti_before_7days": False,
        })

        option1 = current.get("noti_before_3days", False)
        option2 = current.get("noti_before_7days", False)

        if option == "noti_option1":
            option1 = checked
        elif option == "noti_option2":
            option2 = checked
        elif option == "both":
            option1 = checked
            option2 = checked

        result = await NotificationController(self.page).update_setting(
            category=category,
            noti_option1=option1,
            noti_option2=option2,
        )

        if result:
            current_settings[category] = result
            self.storage.set("notification_settings", current_settings)

        self.Notification(switch_type)
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
        self.Notification(content)
    # ---------------------------------------------------------------------------------------------------
    # Notification Test Timer
    # ---------------------------------------------------------------------------------------------------
    def Notification(self, switch_type):
        # -----------------------------------------------------------------------------------------------
        # Notification Popup Content
        # -----------------------------------------------------------------------------------------------
        self.notification_controls.clear()
        self.noti_time = "지금"
        popup_top = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
            ft.Container(padding=0, margin=0, content=ft.Row(spacing=5, controls=[
                ft.Image("icon.png", width=24), dogdog.basic_text("똑똑", color=ft.Colors.GREY_400, weight="bold")
            ])), 
            dogdog.basic_text(self.noti_time, color=ft.Colors.GREY_400, weight="bold")
        ])
        self.notification_controls.append(popup_top)
        if self.notification_popup not in self.page.overlay:
            self.page.overlay.append(self.notification_popup)
        else:
            self.page.overlay.clear()
            self.page.overlay.append(self.notification_popup)
        # -----------------------------------------------------------------------------------------------
        # Notification Setting
        # -----------------------------------------------------------------------------------------------
        noti_setting = self.storage.get(f'noti_{switch_type}')
        if noti_setting:
            # print(switch_type, noti_setting)
            noti_type = None
            select_time = None
            if switch_type == 'food':
                noti_type = self.food_time.content.controls[1].value.replace('오후','PM').replace('오전','AM') # type: ignore
                select_time = int(self.food_time_drop.value) # type: ignore
                self.noti_title = "밥주기"
                self.noti_message = f"🦴 {'pet_name'}, 밥 줄 시간입니다."
            elif switch_type == 'water':
                noti_type = self.water_time.content.controls[1].value.replace('오후','PM').replace('오전','AM') # type: ignore
                select_time = int(self.water_time_drop.value) # type: ignore
                self.noti_title = "물주기"
                self.noti_message = f"💧 {'pet_name'}, 물 줄 시간입니다."
            elif switch_type == 'drug':
                noti_type = self.drug_time.content.controls[1].value.replace('오후','PM').replace('오전','AM') # type: ignore
                select_time = int(self.drug_time_drop.value) # type: ignore
                self.noti_title = "약주기"
                self.noti_message = f"💊 {'pet_name'}, 약 줄 시간입니다."
            elif switch_type == 'subs3':
                self.noti_title = "똑똑배송"
                self.noti_message = "📦 3일 뒤 “가장 맛있는 시간 30일, 닭고기 2.5kg”이 배송됩니다."
            elif switch_type == 'subs7':
                self.noti_title = "똑똑배송"
                self.noti_message = "📦 7일 뒤 “가장 맛있는 시간 30일, 닭고기 2.5kg”이 배송됩니다."
            elif switch_type == 'left_food_count':
                self.noti_title = "소진일 알림"
                self.noti_message = "🍚 급여중인 사료가 7일치 남았습니다. 지금 바로 사료를 구매하세요."
            if noti_type and select_time:
                noti_setting_time = datetime.datetime.strptime(noti_type, "%p %H:%M")
                vs_time = []
                for count in range(int(24/select_time)):
                    times = noti_setting_time + datetime.timedelta(hours=count*select_time)
                    vs_time.append(times.strftime("%d %H:%M"))
                print(f' 🛎️ Setting {switch_type} Guide Time (First Alarm ⏲️[{vs_time[1].split()[1]}])\n{"===="*30}')
            
            popup_title = dogdog.basic_text(self.noti_title, size=16, weight="bold")
            popup_message = dogdog.basic_text(self.noti_message)
            
            self.notification_controls.append(popup_title)
            self.notification_controls.append(popup_message)
            self.notification_popup.open = True
            for task in asyncio.all_tasks():
                if "noti_popup_delay" in str(task.get_coro()):
                    task.cancel()
            asyncio.create_task(self.noti_popup_delay())
    # ---------------------------------------------------------------------------------------------------
    # Notification Popup Delay Task
    # ---------------------------------------------------------------------------------------------------
    async def noti_popup_delay(self):
        try:
            self.notification_popup.content.offset = ft.Offset(0,-1)
            self.notification_popup.update()
            await asyncio.sleep(0.5)
            self.notification_popup.content.offset = ft.Offset(0,0)
            self.notification_popup.update()
            await asyncio.sleep(5)
            self.notification_popup.content.offset = ft.Offset(0,-1)
            self.notification_popup.update()
            self.notification_popup.open = False
            self.page.update()
        except: pass

def notification_setting(page: ft.Page, popup, settings=None, is_subscribed=False):

    noti = Noti(page=page, popup=popup, settings=settings, is_subscribed=is_subscribed)

    subs_interval = dogdog.content_container(
        content_list=[
            dogdog.basic_text("구독 알림 설정", size=16, color=ft.Colors.GREY_800, weight="bold"),
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                dogdog.basic_text(spans=[
                    ft.TextSpan("3일 전\n", style=dogdog.TextStyle(color=ft.Colors.GREY_700)),
                    ft.TextSpan("구독 배송 3일 전 안내"),
                ], color=ft.Colors.GREY_600, size=12),
                ft.Switch(
                    value=noti.get_db_noti_value("subs_delivery", 3) if noti.is_subscribed else False,
                    disabled=not noti.is_subscribed,
                    active_track_color="#FBDD30" if noti.is_subscribed else "#EEEEEE",
                    inactive_track_color="#E5E5E5",
                    thumb_color=None if noti.is_subscribed else "#D0D0D0",
                    data={'noti':'subs3'},
                    on_change=noti.switch_event,
                )
            ]),
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                dogdog.basic_text(spans=[
                    ft.TextSpan("7일 전\n", style=dogdog.TextStyle(color=ft.Colors.GREY_700)),
                    ft.TextSpan("구독 배송 7일 전 안내"),
                ], color=ft.Colors.GREY_600, size=12),
                ft.Switch(
                    value=noti.get_db_noti_value("subs_delivery", 7) if noti.is_subscribed else False,
                    disabled=not noti.is_subscribed,
                    active_track_color="#FBDD30" if noti.is_subscribed else "#EEEEEE",
                    inactive_track_color="#E5E5E5",
                    thumb_color=None if noti.is_subscribed else "#D0D0D0",
                    data={'noti':'subs7'},
                    on_change=noti.switch_event,
                )
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
                ft.Switch(
                    value=noti.get_db_noti_value("left_feeding_day", 3),
                    active_track_color="#FBDD30",
                    data={'noti':'left_food_count'},
                    on_change=noti.switch_event,
                )
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