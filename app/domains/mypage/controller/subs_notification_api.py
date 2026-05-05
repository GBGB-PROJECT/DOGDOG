import datetime
import flet as ft
from api_client import ApiClient


class NotificationController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.storage = page.session.store
        self.api = ApiClient(page)

    async def check_on_app_load(self):
        if self.storage.get("notification_load_checked"):
            return

        if not self.storage.get("access_token"):
            return

        self.storage.set("notification_load_checked", True)

        # today = datetime.date.today().isoformat()
        # customer_id = self.storage.get("customer_id") or "me"
        # storage_key = f"notification_sent_date:{customer_id}"

        try:
            # last_sent_date = None
            # if hasattr(self.page, "client_storage"):
            #     last_sent_date = await self.page.client_storage.get_async(storage_key)

            # if last_sent_date == today:
            #     return

            res = await self.api.get("/notifications/check")

            if res.status_code != 200:
                return

            payload = res.json()
            notifications = payload.get("data") or []

            if not notifications:
                return

            self.storage.set("notifications", notifications)

            message = "\n".join([n.get("message", "") for n in notifications])
            snack_bar = ft.SnackBar(
                content=ft.Text(message),
                behavior=ft.SnackBarBehavior.FLOATING,
            )
            self.page.overlay.append(snack_bar)
            snack_bar.open = True

            # if hasattr(self.page, "client_storage"):
            #     await self.page.client_storage.set_async(storage_key, today)

            self.page.update()

        except Exception as e:
            print(f"[NOTIFICATION] on-load check failed: {e}")

    # setting 조회, 수정
    # 조회 ----------------------------------------------------------------------------------
    async def get_settings(self):
        res = await self.api.get("/notifications/settings")
        if res.status_code != 200:
            print(f"[NOTIFICATION] settings get failed: {res.status_code}")
            return []

        return res.json().get("data") or []

    # 수정 ----------------------------------------------------------------------------------
    async def update_setting(self, category: str, noti_option1: bool, noti_option2: bool):
        body = {
            "category": category,
            "noti_option1": noti_option1,
            "noti_option2": noti_option2,
        }

        res = await self.api.patch("/notifications/settings", data=body)

        if res.status_code != 200:
            print(f"[NOTIFICATION] settings update failed: {res.status_code} {res.text}")
            return None

        return res.json().get("data")
