# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
import datetime
import domains
# -------------------------------------------------------------------------------------------------------
class StatusController:
    def __init__(self, page: ft.Page, popup):
        # -----------------------------------------------------------------------------------------------
        # Default Value
        # -----------------------------------------------------------------------------------------------
        self.page = page
        self.popup = popup
        self.storage = page.session.store
        self.popup.event_popup.actions[0] = ft.Row()
        self.popup.event_popup.actions[1].content = "닫기" # type: ignore
        self.popup.event_popup.modal = False
        if self.storage.get("customer_food_id"): self.storage.remove("customer_food_id")
        # -----------------------------------------------------------------------------------------------
        # Popup Bottom Sheet
        # -----------------------------------------------------------------------------------------------
        self.grid_bottom_sheet = self.popup.bottom_sheet_popup
        self.bottom_sheet_contents = self.popup.bottom_sheet_controls
        self.bottom_sheet_contents.clear()
        # -----------------------------------------------------------------------------------------------
        # Guide Bottom Sheet
        # -----------------------------------------------------------------------------------------------
        self.guide_bottom_sheet_content = []
        self.guide_page = dogdog.bottom_sheet(content=self.guide_bottom_sheet_content)
        # -----------------------------------------------------------------------------------------------
        # Date Picker
        # -----------------------------------------------------------------------------------------------
        self.date_picker = ft.DatePicker(
            first_date=datetime.datetime.now() - datetime.timedelta(days=7),
            last_date=datetime.datetime.now())
        if self.date_picker not in page.overlay:
            page.overlay.append(self.date_picker)
        self.data_button = dogdog.flat_icon_text_button(
            ft.Icons.CALENDAR_MONTH, datetime.datetime.now().strftime("%Y.%m.%d")
        )
        self.data_button.on_click = lambda e, picker=self.date_picker: self.open_event(e, picker)
        # -----------------------------------------------------------------------------------------------
        # Time Picker
        # -----------------------------------------------------------------------------------------------
        self.time_picker = ft.TimePicker(
            entry_mode=ft.TimePickerEntryMode.DIAL_ONLY)
        self.time_button = dogdog.flat_icon_text_button(
            ft.Icons.ACCESS_TIME, 
            datetime.datetime.now().strftime("%p %H:%M").replace("AM", "오전").replace("PM", "오후"))
        self.time_button.on_click = lambda e, picker=self.time_picker: self.open_event(e, picker)
    # ---------------------------------------------------------------------------------------------------
    # Picker Open Event
    # ---------------------------------------------------------------------------------------------------
    def open_event(self, e, picker):
        if picker not in self.page.overlay: self.page.overlay.append(picker)
        try: picker.open = True
        except Exception as err: print(err)
    # ---------------------------------------------------------------------------------------------------
    # Input Field Change Event
    # ---------------------------------------------------------------------------------------------------
    def change_event(self, e, change, case=None):
        value = e.control.value
        if change == "customer_food_id":
            if case.visible == False: case.visible = True # type: ignore
            try: self.storage.set("customer_food_id", int(value))
            except ValueError: pass
        elif "weight" in change:
            if "_float_weight" in change:
                try: self.storage.set(change, float(value))
                except ValueError: pass
            else:
                try: self.storage.set(change, int(value))
                except ValueError: pass
        elif "memo" in change:
            try: self.storage.set(change, value)
            except ValueError: pass
        elif "date" in change:
            if value and case:
                now = datetime.timedelta(hours=9)
                self.storage.set(key=change, value=(value + now).strftime("%Y-%m-%d"))
                case.content.controls[1].value = (value + now).strftime("%Y.%m.%d")
        elif "time" in change:
            if value and case:
                self.storage.set(key=change, value=value.strftime("%H:%M"))
                case.content.controls[1].value = (
                    value.strftime("%p %H:%M").replace("AM", "오전").replace("PM", "오후"))
        self.grid_bottom_sheet.update()
    # ---------------------------------------------------------------------------------------------------
    # Button Push Event
    # ---------------------------------------------------------------------------------------------------
    def button_event(self, e, call, content):
        error_popup = self.popup.event_popup
        def error_popup_open(title, text):
            error_popup.title = dogdog.basic_text(title, size=16, weight="bold")
            error_popup.content = dogdog.basic_text(text)
            if error_popup not in self.page.overlay:
                self.page.overlay.append(error_popup)
            else:
                self.page.overlay.clear()
                self.page.overlay.append(error_popup)
            error_popup.open = True
        callcase = {
            "feeding":{"밥주기":"사료, 급여량을 선택 / 작성해주세요."},
            "watering": {"물주기":"물 섭취량을 적어주세요."},
            "daily_walks": {"활동기록":"산책시간을 적어주세요."}, 
            "hygiene_bowel": {"위생/배변":"배변 스코어를 선택해주세요."},
            "health_log": {"건강기록":"건강상태를 작성해주세요."},
            "status_log": {"상태기록":"기타상태를 작성해주세요."},
        }
        for for_call_title, for_call_message in callcase.get(call).items(): # type: ignore
            call_title = for_call_title
            call_message = for_call_message
        event_text = {}
        if content == "edit": pass
            # self.show_error(content)
        elif content == "delete": pass
            # self.show_error(content)
        elif content == "save":
            if call == "feeding":
                if self.storage.get("customer_food_id"):
                    event_text.update({"customer_food_id":self.storage.get("customer_food_id")})
                else:
                    error_popup_open(call_title, call_message)
                    return
            if self.storage.get(f"{call}_weight"):
                event_text.update({f"{call}_weight":self.storage.get(f"{call}_weight")})
            elif self.storage.get(f"{call}_float_weight"):
                event_text.update({f"{call}_float_weight":self.storage.get(f"{call}_float_weight")})
                event_text.update({f"{call}_bcs_weight":self.storage.get(f"{call}_bcs_weight")})
            elif call == "status_log": pass
            else:
                error_popup_open(call_title, call_message)
                return
            if self.storage.get(f"{call}_memo"):
                event_text.update({f"{call}_memo":self.storage.get(f"{call}_memo")})
            else:
                if call == "status_log":
                    error_popup_open(call_title, call_message)
                    return
            event_text.update({f"{call}_date":self.storage.get(f"{call}_date")})
            event_text.update({f"{call}_time":self.storage.get(f"{call}_time")})
            error_popup_open(call_title, call_message)
        elif content == "feeding_add": self.page.go("/feeding_add")
        elif content == "cancel": pass
        self.grid_bottom_sheet.open = False
        self.page.update()
    # ---------------------------------------------------------------------------------------------------
    # Bottom Sheet Append Def
    # ---------------------------------------------------------------------------------------------------
    def bottom_sheet_title(self, text, link=None):
        if link: 
            self.bottom_sheet_contents.append(ft.Row(spacing=5, controls=[
                dogdog.basic_text(value=text, size=25, weight="bold"),
                ft.Container(scale=0.8,
                    width=25, height=25, ink=True, on_click=link, border_radius=25, bgcolor=ft.Colors.GREY_300,
                    content=ft.Icon(icon=ft.Icons.QUESTION_MARK, color=ft.Colors.WHITE, size=20))
            ]))
        else: self.bottom_sheet_contents.append(dogdog.basic_text(value=text, size=25, weight="bold"))
        self.bottom_sheet_contents.append(ft.Divider())
    # ---------------------------------------------------------------------------------------------------
    # Guide Bottom Sheet Event
    # ---------------------------------------------------------------------------------------------------
    def guide_bottom_sheet(self, e, route):
        def guide_close(e):
            self.guide_page.open = False
        if self.guide_page not in self.page.overlay:
            self.page.overlay.append(self.guide_page)
        self.guide_bottom_sheet_content.clear()
        self.guide_bottom_sheet_content.append(
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[dogdog.basic_text(
                f'{"배변 스코어란?" if route == "bowel" else "BCS 란?"}', size=25, weight="bold"),
                dogdog.flat_button("닫기", on_click=lambda e:guide_close(e), scale=0.8)]))
        self.guide_bottom_sheet_content.append(ft.Divider())
        self.guide_bottom_sheet_content.append(
            ft.Column(expand=True, scroll=ft.ScrollMode.HIDDEN, 
                controls=[domains.guide.what_guide(page=self.page, content=route)]))
        self.guide_page.open = True
# -------------------------------------------------------------------------------------------------------
def bottom_sheet(e, page: ft.Page, popup, call):
    # ---------------------------------------------------------------------------------------------------
    # Default Value
    # ---------------------------------------------------------------------------------------------------
    storage = page.session.store
    s_control = StatusController(page=page, popup=popup)
    customer_detail = storage.get("customer_detail")
    is_customer_detail = True
    # ---------------------------------------------------------------------------------------------------
    def setting_content(call):
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                dogdog.flat_button(
                    "취소", on_click=lambda e, menu=call, content="cancel": s_control.button_event(e, call,content)),
                dogdog.flat_button(
                    "저장", bgcolor="#FEF3B9", # type: ignore
                    on_click=lambda e, menu=call, content="save": s_control.button_event(e, call, content)),
            ] # type: ignore
        )
    # ---------------------------------------------------------------------------------------------------
    def data_time_select(call):
        s_control.date_picker.on_change=lambda e, change=f"{call}_date", case=s_control.data_button: s_control.change_event(e, change, case)
        storage.set(f"{call}_date", datetime.datetime.now().strftime("%Y-%m-%d"))
        s_control.time_picker.on_change=lambda e, change=f"{call}_time", case=s_control.time_button: s_control.change_event(e, change, case)
        storage.set(f"{call}_time", datetime.datetime.now().strftime("%H:%M"))
        return ft.Row(spacing=30, alignment=ft.MainAxisAlignment.CENTER, controls=[s_control.data_button, s_control.time_button])
    # ---------------------------------------------------------------------------------------------------
    if call == "feeding":
        s_control.bottom_sheet_title("밥주기")
        if customer_detail:
            feeding_guide = ft.Column(
                visible=False,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                controls=[
                    ft.Row(margin=ft.margin.only(bottom=10), controls=[
                        dogdog.basic_text(
                            value=f"오늘 {storage.get('customer_pet_name')}에게 딱 알맞는 1회 급여량은 ...",
                            size=16, weight="bold", color=ft.Colors.GREY_600)]),
                    ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                        ft.Image(src="speech_bubble.png", height=100, color="#FEF3B9"),
                        dogdog.basic_text("40g", weight="bold", size=40),
                    ], spacing=-90),
                    ft.Image(src="dogbowl.png", height=100, margin=ft.margin.only(top=20))
            ])
            food = [dogdog.dropdown_menu_option(
                key=customer_food_id, text=f"{detail.get('brand')} {detail.get('product_name')}"
                    ) for customer_food_id , detail in customer_detail.items()]
            feeding_food_list = ft.Row(margin=ft.margin.only(bottom=18),
                controls=[
                    dogdog.dropdown_menu(label="사료를 선택해주세요.", options=food, 
                        event=lambda e, change="customer_food_id", 
                        case=feeding_guide: s_control.change_event(e, change, case)
            )])
            
            feeding_weight = dogdog.input_textfield(
                hint_text="급여량을 적어주세요.", input_type="int", suffix="g", 
                on_change=lambda e, change=f"{call}_weight": s_control.change_event(e, change))
            if storage.get(f"{call}_weight"): storage.remove(f"{call}_weight")
            
            feeding_memo = dogdog.input_textfield(
                hint_text="메모 (선택)", text_filter=None, max_length=None, # type: ignore
                on_change=lambda e, change=f"{call}_memo": s_control.change_event(e, change))
            if storage.get(f"{call}_memo"): storage.remove(f"{call}_memo")
            # -------------------------------------------------------------------------------------------
            s_control.bottom_sheet_contents.append(feeding_guide)
            s_control.bottom_sheet_contents.append(feeding_food_list)
            s_control.bottom_sheet_contents.append(feeding_weight)
            s_control.bottom_sheet_contents.append(feeding_memo)
        # -----------------------------------------------------------------------------------------------
        else:
            is_customer_detail = False
            not_customer_detail = ft.Row(
                height=100,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    dogdog.basic_text(
                        value="등록된 제품이 없습니다.", size=16, weight="bold", color=ft.Colors.GREY_600),
            ])
            setting_content = [
                dogdog.flat_button(
                    "등록하러가기", bgcolor="#FEF3B9", # type: ignore 
                    on_click=lambda e, menu=call, content="feeding_add": 
                    s_control.button_event(e, call, content)),
                dogdog.flat_button(
                    "나중에 등록할께요",
                    on_click=lambda e, menu=call, content="cancel": 
                    s_control.button_event(e, call, content)),
            ] # type: ignore
            setting = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[ft.Column(
                    spacing=20,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=setting_content)] # type: ignore
            )
            # -------------------------------------------------------------------------------------------
            s_control.bottom_sheet_contents.append(not_customer_detail)
            s_control.bottom_sheet_contents.append(setting)
    # ---------------------------------------------------------------------------------------------------
    elif call == "watering":
        s_control.bottom_sheet_title("물주기")
        watering = dogdog.input_textfield(
            hint_text="물 섭취량을 적어주세요.", input_type="int", suffix="ml", 
            on_change=lambda e, change=f"{call}_weight": s_control.change_event(e, change))
        if storage.get(f"{call}_weight"): storage.remove(f"{call}_weight")
        
        watering_memo = dogdog.input_textfield(
            hint_text="메모 (선택)", text_filter=None, max_length=None, # type: ignore
            on_change=lambda e, change=f"{call}_memo": s_control.change_event(e, change))
        if storage.get(f"{call}_memo"): storage.remove(f"{call}_memo")
        # -----------------------------------------------------------------------------------------------
        s_control.bottom_sheet_contents.append(watering)
        s_control.bottom_sheet_contents.append(watering_memo)
    # ---------------------------------------------------------------------------------------------------
    elif call == "daily_walks":
        s_control.bottom_sheet_title("활동기록")
        daily_walks = dogdog.input_textfield(
            hint_text="산책시간을 적어주세요.", input_type="int", suffix="분", 
            on_change=lambda e, change=f"{call}_weight": s_control.change_event(e, change))
        if storage.get(f"{call}_weight"): storage.remove(f"{call}_weight")
        
        daily_walks_memo = dogdog.input_textfield(
            hint_text="메모 (선택)", text_filter=None, max_length=None, # type: ignore
            on_change=lambda e, change=f"{call}_memo": s_control.change_event(e, change))
        if storage.get(f"{call}_memo"): storage.remove(f"{call}_memo")
        # -----------------------------------------------------------------------------------------------
        s_control.bottom_sheet_contents.append(daily_walks)
        s_control.bottom_sheet_contents.append(daily_walks_memo)
    # ---------------------------------------------------------------------------------------------------
    elif call == "hygiene_bowel":
        s_control.bottom_sheet_title("위생/배변", lambda e=e, route="bowel":s_control.guide_bottom_sheet(e, route))
        hygiene_bowel_score = dogdog.dropdown_menu(
            label="배변 스코어를 선택해주세요.", options=[], 
            event=lambda e, change=f"{call}_weight": s_control.change_event(e, change)
        )
        hygiene_bowel_score.options = [dogdog.dropdown_menu_option(text=f"{row}") for row in range(1,8)]
        if storage.get(f"{call}_weight"): storage.remove(f"{call}_weight")
        hygiene_bowel_memo = dogdog.input_textfield(
            hint_text="메모 (선택)", text_filter=None, max_length=None, # type: ignore
            on_change=lambda e, change=f"{call}_memo": s_control.change_event(e, change))
        if storage.get(f"{call}_memo"): storage.remove(f"{call}_memo")
        # -----------------------------------------------------------------------------------------------
        s_control.bottom_sheet_contents.append(hygiene_bowel_score)
        s_control.bottom_sheet_contents.append(hygiene_bowel_memo)
    # ---------------------------------------------------------------------------------------------------
    elif call == "health_log":
        s_control.bottom_sheet_title("건강기록", lambda e=e, route="bcs":s_control.guide_bottom_sheet(e, route))
        health_log = dogdog.input_textfield(
            hint_text="몸무게를 적어주세요.", input_type="float", suffix="Kg", 
            on_change=lambda e, change=f"{call}_float_weight": s_control.change_event(e, change))
        if storage.get(f"{call}_float_weight"): storage.remove(f"{call}_float_weight")
        health_bcs = dogdog.dropdown_menu(
            label="BCS를 선택해주세요.", options=[], 
            event=lambda e, change=f"{call}_bcs_weight": s_control.change_event(e, change)
        )
        health_bcs.options = [dogdog.dropdown_menu_option(text=f"{row}") for row in range(9, 0, -1)]
        if storage.get(f"{call}_bcs_weight"): storage.remove(f"{call}_bcs_weight")
        # -----------------------------------------------------------------------------------------------
        s_control.bottom_sheet_contents.append(health_log)
        s_control.bottom_sheet_contents.append(health_bcs)
    # ---------------------------------------------------------------------------------------------------
    elif call == "status_log":
        s_control.bottom_sheet_title("상태기록")
        status_log = dogdog.input_textfield(
            hint_text="기타상태를 작성해주세요.", text_filter=None, max_length=None, # type: ignore
            on_change=lambda e, change=f"{call}_memo": s_control.change_event(e, change))
        if storage.get(f"{call}_memo"): storage.remove(f"{call}_memo")
        # -----------------------------------------------------------------------------------------------
        s_control.bottom_sheet_contents.append(status_log)
    # ---------------------------------------------------------------------------------------------------
    if is_customer_detail == True:
        s_control.bottom_sheet_contents.append(data_time_select(call))
        s_control.bottom_sheet_contents.append(setting_content(call))
    # ---------------------------------------------------------------------------------------------------
    s_control.data_button.content.controls[1].value = ( # type: ignore
        datetime.datetime.now().strftime("%Y.%m.%d"))
    s_control.time_button.content.controls[1].value = ( # type: ignore
        datetime.datetime.now().strftime("%p %H:%M").replace("AM", "오전").replace("PM", "오후"))
    # ---------------------------------------------------------------------------------------------------
    if s_control.grid_bottom_sheet not in page.overlay:
        page.overlay.append(s_control.grid_bottom_sheet)
    else:
        page.overlay.clear()
        page.overlay.append(s_control.grid_bottom_sheet)
    # ---------------------------------------------------------------------------------------------------
    s_control.grid_bottom_sheet.open = True
    page.update()
# -------------------------------------------------------------------------------------------------------
def status_update_menu(page :ft.Page, popup):
    # ---------------------------------------------------------------------------------------------------
    # Default Value
    # ---------------------------------------------------------------------------------------------------
    content_list_top = [
        ("밥주기", "dogbowl.png", lambda e, call="feeding":bottom_sheet(e, page, popup, call)),
        ("물주기", "waterdrop.png", lambda e, call="watering":bottom_sheet(e, page, popup, call)),
        ("활동기록", "dogwalking.png", lambda e, call="daily_walks":bottom_sheet(e, page, popup, call)),
    ]
    content_list_bottom = [
        ("배변", "poop.png", lambda e, call="hygiene_bowel":bottom_sheet(e, page, popup, call)),
        ("건강기록", "injection.png", lambda e, call="health_log":bottom_sheet(e, page, popup, call)),
        ("상태기록", "note.png", lambda e, call="status_log":bottom_sheet(e, page, popup, call)),
    ]
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        ft.Row(controls=[
            dogdog.icon_flat_button(
                text=text, icon=icon, on_click=on_click) for text, icon, on_click in content_list_top]),
        ft.Row(controls=[
            dogdog.icon_flat_button(
                text=text, icon=icon, on_click=on_click) for text, icon, on_click in content_list_bottom]),
    ]
    return ft.Container(
        padding=ft.Padding.only(left=20, right=20),
        bgcolor="#ffffff",
        content=ft.Column(controls=content_column) # type: ignore
    )