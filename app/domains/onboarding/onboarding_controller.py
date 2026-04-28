import re
import flet as ft
import datetime
from dateutil.relativedelta import relativedelta
from api_client import ApiClient


class OnboardingController:
    """
    [Controller] OnboardingController
    역할: 온보딩 과정의 비즈니스 로직(데이터 검증, API 통신, 상태 관리)을 전담합니다.
    - View(UI)는 화면 구성에만 집중하고, 모든 클릭 이벤트와 데이터 처리는 이 컨트롤러에서 수행합니다.
    """

    # 온보딩 단계에서 누적될 데이터 저장소 (클래스 변수로 유지하여 단계 간 공유)
    data = {}

    def __init__(
        self,
        page: ft.Page,
        show_error_callback,
        change_page_callback,
        focus_field=None,
        popup=None,
    ):
        self.page = page
        self.show_error = show_error_callback
        self.change_page_callback = change_page_callback
        self.storage = page.session.store
        self.focus_field = focus_field
        self.popup = popup

        # 이메일 검증용 정규식
        self.regex_email = re.compile(
            pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._]+[@][a-zA-Z][A-Za-z.]+[.]\w{2,}"
        )

        # 비밀번호 검증용 정규식 (최소 8자, 영문, 숫자, 특수문자 포함)
        # ^(?=.*[A-Za-z]) : 최소 하나의 영문자 포함
        # (?=.*\d) : 최소 하나의 숫자 포함
        # (?=.*[@$!%*#?&]) : 최소 하나의 특수문자 포함
        # [A-Za-z\d@$!%*#?&]{8,} : 위 조건을 만족하는 8자 이상의 문자열
        self.regex_password = re.compile(
            pattern=r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        )

    async def check_email_duplicate(self, e):
        """이메일 중복 확인 로직"""
        email = self.storage.get("user_email")
        if not email:
            self.show_error(text="이메일을 입력해 주세요.")
            e.control.update()
            return

        if not re.fullmatch(pattern=self.regex_email, string=email):
            self.show_error(text="유효한 이메일 형식이 아닙니다.")
            e.control.disabled = False
            e.control.update()
            return

        e.control.disabled = True  # 중복 클릭 방지
        e.control.update()

        try:
            api_client = ApiClient(self.page)
            res = await api_client.get(f"/auth/check-email?email={email}")

            if res.status_code == 200:
                is_duplicate = res.json().get("is_duplicate", False)
                if is_duplicate:
                    self.show_error(text="이미 사용 중인 이메일입니다.")
                    self.storage.set("is_email_verified", False)
                else:
                    self.show_error(text="사용 가능한 이메일입니다.")
                    self.storage.set("is_email_verified", True)
                    self.storage.set("verified_email", email)
            else:
                self.show_error(text="이메일 중복 확인에 실패했습니다.")
        except Exception as ex:
            self.show_error(text=f"API 통신 오류: {str(ex)}")
        finally:
            e.control.disabled = False
            e.control.update()
            self.page.update()

    async def process_user_sign_up(self, e):
        """회원가입 기본 정보(이메일, 닉네임, 비밀번호) 검증 및 저장"""
        current_email = self.storage.get("user_email")
        is_verified = self.storage.get("is_email_verified")
        verified_email = self.storage.get("verified_email")
        password = self.storage.get("user_password")
        nickname = self.storage.get("user_name")

        # 1. 필수 입력 및 이메일 인증 확인
        if not current_email or not nickname or not password:
            self.show_error(text="이메일, 닉네임, 비밀번호를 모두 입력해주세요.")
            return

        if not is_verified or current_email != verified_email:
            self.show_error(text="이메일 중복 확인을 진행해 주세요.")
            return

        # 2. 🔥 닉네임 유효성 검사 (신규 기능)
        # 조건: 2~10자, 한글/영문/숫자만 허용, 공백 불가
        regex_nickname = re.compile(r"^[가-힣a-zA-Z0-9]{2,10}$")
        if not re.fullmatch(regex_nickname, nickname):
            self.show_error(
                text="닉네임은 2~10자의 한글, 영문, 숫자만 사용 가능합니다."
            )
            return

        # 3. 🔥 비밀번호 유효성 검사 (신규 기능)
        if not re.fullmatch(self.regex_password, password):
            self.show_error(
                text="비밀번호는 8자 이상, 영문/숫자/특수문자를 포함해야 합니다."
            )
            return

        # 4. 데이터 누적 및 다음 단계 이동
        e.control.disabled = True
        self.page.update()

        try:
            OnboardingController.data.update(
                {
                    "email": current_email,
                    "user_nickname": nickname,
                    "password": password,
                    "phone": None,
                    "oauth_type": None,
                }
            )

            self.show_error(text="기본 정보 저장 완료")
            if self.focus_field:
                await self.focus_field.focus()

            self.page.update()
            self.change_page_callback("/pet_info")
        except Exception as ex:
            e.control.disabled = False
            self.show_error(text=f"데이터 처리 오류: {str(ex)}")
            self.page.update()

    async def process_pet_info(self, e):
        """반려견 기본 정보 검증 및 저장"""
        if not (
            self.storage.get("breed_text")
            and self.storage.get("pet_name")
            and self.storage.get("pet_weight")
        ):
            self.show_error(
                text="이름, 품종, 생년월일, 성별, 무게를 모두 입력해주세요."
            )
            return

        # 생일 계산 로직
        if self.storage.get("pet_birth_day"):
            birth = str(self.storage.get("pet_birth_day"))
        elif self.storage.get("pet_age_year") and self.storage.get("pet_age_month"):
            age_month = int(self.storage.get("pet_age_month").split()[0])
            age_year = int(self.storage.get("pet_age_year").split()[0])
            birth = str(
                datetime.date.today() - relativedelta(months=age_month, years=age_year)
            )
        else:
            self.show_error("생년월일을 선택해주세요.")
            return

        # 무게 검증
        try:
            pet_weight_str = str(self.storage.get("pet_weight"))
            weight_val = float(pet_weight_str)
            if weight_val <= 0 or weight_val >= 120:
                self.show_error(text="정상적인 무게를 입력해주세요.")
                return
        except ValueError:
            self.show_error(text="올바른 숫자 형식으로 무게를 입력해주세요.")
            return

        # 성별 매핑
        gender_map = {
            "수컷": (1, False),
            "암컷": (2, False),
            "수컷 (중성화)": (1, True),
            "암컷 (중성화)": (2, True),
        }
        gender_info = gender_map.get(self.storage.get("pet_gender"))
        if not gender_info:
            self.show_error(text="성별을 선택해주세요.")
            return

        OnboardingController.data.update(
            {
                "pet_nickname": self.storage.get("pet_name"),
                "image_path": self.storage.get("image_path"),
                "breed_id": self.storage.get("breed_id"),
                "birth": birth,
                "sex": gender_info[0],
                "is_neutered": gender_info[1],
                "weight": self.storage.get("pet_weight"),
            }
        )

        if self.focus_field:
            await self.focus_field.focus()
        self.page.update()
        self.change_page_callback("/pet_obesity")

    def process_pet_obesity(self, e):
        """반려견 체형 정보 저장"""
        if self.storage.get("body_score"):
            OnboardingController.data.update({"bcs": self.storage.get("body_score")})
            self.change_page_callback("/pet_activity")
        else:
            self.show_error(text="체형을 선택해주세요.")

    async def process_pet_activity(self, e):
        """산책 및 급여 횟수 정보 저장"""
        meals = [
            self.storage.get("breakfast"),
            self.storage.get("lunch"),
            self.storage.get("dinner"),
        ]
        if self.storage.get("radio_time") and any(meals):
            feeding_count = sum(1 for m in meals if m)
            OnboardingController.data.update(
                {
                    "feeding_count": feeding_count,
                    "daily_walks": int(self.storage.get("radio_time")),
                }
            )
            if self.focus_field:
                await self.focus_field.focus()
            self.page.update()
            self.change_page_callback("/pet_health")
        else:
            self.show_error(text="급여 시간(최소 1개)과 산책 시간을 선택해주세요.")

    async def process_pet_health(self, e):
        """건강(알러지, 질환) 정보 저장"""
        OnboardingController.data.update(
            {
                "allergy": self.storage.get("allergy"),
                "disease": self.storage.get("disease"),
            }
        )
        if self.focus_field:
            await self.focus_field.focus()
        self.page.update()
        self.change_page_callback("/pet_food")

    async def process_onboarding_finalize(self, e):
        """최종 데이터 검증 및 서버 전송 (회원가입+반려견+사료 통합)"""
        p_id = self.storage.get("product_id")
        f_weight = self.storage.get("food_weight")

        if not p_id or not f_weight:
            self.show_error(text="사료 무게와 급여량을 모두 입력/선택해 주세요.")
            return

        OnboardingController.data.update(
            {"product_id": int(p_id), "food_weight": int(float(f_weight))}
        )

        if self.popup:
            await self.popup.show_api_insert_open(e)

        try:
            d = OnboardingController.data
            payload = {
                "user": {
                    "email": str(d.get("email")),
                    "password": str(d.get("password")),
                    "nickname": str(d.get("user_nickname")),
                    "phone": None,
                    "oauth_type": None,
                },
                "pet": {
                    "nickname": str(d.get("pet_nickname")),
                    "birth_day": str(d.get("birth")),
                    "breed_id": int(d.get("breed_id")),
                    "sex": int(d.get("sex")),
                    "is_neutered": bool(d.get("is_neutered")),
                    "weight": float(d.get("weight")),
                    "bcs": int(d.get("bcs")),
                    "daily_walks": int(d.get("daily_walks")),
                    "feeding_count": int(d.get("feeding_count")),
                },
                "food": {
                    "product_id": int(d.get("product_id")),
                    "total_weight": int(d.get("food_weight")),
                },
            }

            api_client = ApiClient(self.page)
            res = await api_client.post("/onboarding", data=payload)

            if res.status_code in [200, 201]:
                res_body = res.json()
                auth_data = res_body.get("auth", {})
                new_pet_id = res_body.get("pet_id")
                customer_id = res_body.get("customer_id")

                if self.popup:
                    await self.popup.show_api_insert_close(e)
                    import asyncio

                    await asyncio.sleep(0.1)  # UI 갱신을 위한 짧은 대기

                # 인증 후처리 (AuthController 위임)
                from domains.auth.auth_controller import AuthController

                auth_ctrl = AuthController(self.page)
                success = await auth_ctrl.complete_relay(
                    auth_data, new_pet_id, customer_id=customer_id
                )

                if success:
                    # self.show_error(text="DOGDOG에 오신 것을 환영합니다!") # 스낵바 대신 성공 화면으로 이동
                    self.change_page_callback("/sign_up_success")
                else:
                    self.show_error(text="세션 동기화 중 오류가 발생했습니다.")
            else:
                if self.popup:
                    await self.popup.show_api_insert_close(e)
                print(f"[API Error] 온보딩 실패: {res.text}")
                msg = res.json().get("detail", "온보딩 실패")
                self.show_error(text=str(msg))

        except Exception as ex:
            if self.popup:
                await self.popup.show_api_insert_close(e)
            print(f"[Onboarding Exception] 상세 내용: {str(ex)}")
            self.show_error(text=f"서버 통신 중 오류 발생: {str(ex)}")
