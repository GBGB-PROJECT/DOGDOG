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

        # 이메일 검증용 정규식 (TLD 길이 제한 포함, 도메인 제한시 일부 예외 상황 있을 수 있어 길이제한으로 한함)
        self.regex_email = re.compile(
            pattern=r"^[a-zA-Z0-9._+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,6}$"
        )

        # 비밀번호 검증용 정규식 (최소 8자, 영문, 숫자, 특수문자 포함)
        # ^(?=.*[A-Za-z]) : 최소 하나의 영문자 포함
        # (?=.*\d) : 최소 하나의 숫자 포함
        # (?=.*[@$!%*#?&]) : 최소 하나의 특수문자 포함
        # [A-Za-z\d@$!%*#?&]{8,} : 위 조건을 만족하는 8자 이상의 문자열
        self.regex_password = re.compile(
            pattern=r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        )

    def update_field(self, key: str, value):
        """
        [공통 상태 관리] Dumb View에서 발생하는 입력 변경 이벤트를 처리하여 세션 스토리지에 저장합니다.
        """
        if value is None or str(value).strip() == "":
            self.storage.remove(key)
        else:
            self.storage.set(key, value)

    def validate_password(self, password: str) -> tuple[bool, str]:
        """
        비밀번호 유효성 검사 (8자 이상, 영문/숫자/특수문자 포함)
        """
        if not password:
            return False, "비밀번호를 입력해주세요."
        if not re.fullmatch(self.regex_password, password):
            return False, "비밀번호는 8자 이상, 영문/숫자/특수문자를 포함해야 합니다."
        return True, ""

    def validate_email(self, email: str) -> tuple[bool, str]:
        """
        이메일 유효성 검사 (TLD 2-6자 제한 적용)
        """
        if not email:
            return False, "이메일을 입력해주세요."
        if not re.fullmatch(self.regex_email, email):
            return False, "올바른 이메일 형식이 아닙니다. (예: dog@dog.com)"
        return True, ""

    async def check_email_duplicate(self, e):
        """이메일 중복 확인 로직"""
        email = self.storage.get("user_email")
        if not email:
            self.show_error(text="이메일을 입력해 주세요.")
            e.control.update()
            return

        is_valid, error_msg = self.validate_email(email)
        if not is_valid:
            self.show_error(text=error_msg)
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
        is_valid, error_msg = self.validate_password(password)
        if not is_valid:
            self.show_error(text=error_msg)
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
        import datetime

        # 1. 스토리지 데이터 추출 및 엄격한 검증
        d = OnboardingController.data
        p_id = self.storage.get("product_id")
        f_weight = self.storage.get("food_weight")

        # 필수 필드 리스트 및 검증 (임시 기본값 사용 금지 원칙 준수)
        required_fields = {
            "email": "이메일 정보가 누락되었습니다.",
            "password": "비밀번호 정보가 누락되었습니다.",
            "user_nickname": "유저 닉네임이 누락되었습니다.",
            "pet_nickname": "반려견 이름을 입력해 주세요.",
            "birth": "반려견 생일을 선택해 주세요.",
            "breed_id": "반려견 품종을 선택해 주세요.",
            "sex": "반려견 성별을 선택해 주세요.",
            "weight": "반려견 몸무게를 입력해 주세요.",
            "bcs": "BCS 지수를 선택해 주세요.",
            "daily_walks": "산책 횟수를 선택해 주세요.",
            "feeding_count": "하루 급여 횟수를 선택해 주세요.",
        }

        for key, msg in required_fields.items():
            if not d.get(key):
                self.show_error(text=msg)
                return

        if not p_id:
            self.show_error(text="사료 상품을 선택해 주세요.")
            return

        if f_weight is None or str(f_weight).strip() == "":
            self.show_error(text="사료 잔여량을 입력해 주세요.")
            return

        # 2. 데이터 타입 변환 및 정규화
        try:
            total_weight = int(float(f_weight))
            product_id = int(p_id)
            if total_weight < 0:
                raise ValueError
        except (ValueError, TypeError):
            self.show_error(text="사료 잔여량은 0 이상의 숫자여야 합니다.")
            return

        OnboardingController.data.update(
            {"product_id": product_id, "total_weight": total_weight}
        )

        if self.popup:
            await self.popup.show_api_insert_open(e)

        try:
            # 3. 최종 Payload 구성 (기본값 제거 및 정적 타입 보장)
            today_str = datetime.date.today().isoformat()

            payload = {
                "user": {
                    "email": str(d["email"]),
                    "password": str(d["password"]),
                    "nickname": str(d["user_nickname"]),
                    "phone": d.get("phone"),
                    "oauth_type": d.get("oauth_type", "local"),
                },
                "pet": {
                    "nickname": str(d["pet_nickname"]),
                    "birth_day": str(d["birth"]),
                    "breed_id": int(d["breed_id"]),
                    "sex": int(d["sex"]),
                    "is_neutered": bool(d.get("is_neutered", False)),
                    "weight": float(d["weight"]),
                    "bcs": int(d["bcs"]),
                    "daily_walks": int(d["daily_walks"]),
                    "feeding_count": int(d["feeding_count"]),
                },
                "food": {
                    "product_id": int(d["product_id"]),
                    "total_weight": int(d["total_weight"]),
                    "feeding_start": today_str,
                },
            }

            # [DEBUG] 전송 데이터 확인
            print(f"[Onboarding DEBUG] Final Payload: {payload}")

            api_client = ApiClient(self.page)
            res = await api_client.post("/onboarding", data=payload)

            if res.status_code in [200, 201]:
                res_body = res.json()
                auth_data = res_body.get("auth", {})
                new_pet_id = res_body.get("pet_id")
                customer_id = res_body.get("customer_id")  # 이거 챙기기!

                if self.popup:
                    await self.popup.show_api_insert_close(e)
                    import asyncio

                    await asyncio.sleep(0.1)

                # 인증 후처리 (원래 잘 작동하던 오리지널 로직으로 복구!)
                from domains.auth.auth_controller import AuthController

                auth_ctrl = AuthController(self.page)

                success = await auth_ctrl.complete_relay(
                    auth_data, new_pet_id, customer_id=customer_id, redirect_to=None
                )

                if success:
                    self.page.go("/sign_up_success")
                else:
                    self.show_error(text="세션 동기화 중 오류가 발생했습니다.")

            else:
                if self.popup:
                    await self.popup.show_api_insert_close(e)
                error_detail = res.json().get("detail", "서버 오류가 발생했습니다.")
                self.show_error(text=f"등록 실패: {error_detail}")

        except Exception as ex:
            if self.popup:
                await self.popup.show_api_insert_close(e)

            # 파이썬 에러의 실제 원인(Traceback)을 터미널에 출력
            import traceback

            print("❌ [Onboarding FATAL ERROR] ==================================")
            traceback.print_exc()
            print("=============================================================")

            # 사용자에게는 간략한 에러 원인만 노출
            self.show_error(text=f"처리 중 오류 발생: {str(ex)}")
