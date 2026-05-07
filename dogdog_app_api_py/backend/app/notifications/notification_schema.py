from pydantic import BaseModel
from typing import List

# 알림 설정 테이블 구조
class NotificationSettingResponse(BaseModel):
    category: str
    category_name: str
    noti_option1: bool
    noti_option2: bool

# 알림 설정 응답 구조
# 조회
class NotificationSettingsReadResponse(BaseModel):
    success: bool
    message: str
    data: List[NotificationSettingResponse]

# 알림 설정 요청 구조
# 수정
class NotificationSettingUpdateRequest(BaseModel):
    category: str
    noti_option1: bool
    noti_option2: bool