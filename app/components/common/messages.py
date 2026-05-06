# app/components/common/messages.py

# 성공 메시지 정의
SUCCESS_MESSAGES = {
    "HISTORY_DELETE_COMPLETE": "기록이 성공적으로 삭제되었습니다.",
    "STATUS_UPDATE_COMPLETE": "정보가 성공적으로 업데이트되었습니다.",
    "LOGIN_SUCCESS": "로그인에 성공했습니다.",
}

# 에러 및 경고 메시지 정의
ERROR_MESSAGES = {
    "HISTORY_DELETE_FAILED": "기록 삭제 중 오류가 발생했습니다.",
    "STATUS_UPDATE_FAILED": "정보 업데이트 중 오류가 발생했습니다.",
    "INVALID_INPUT": "입력 값이 올바르지 않습니다. 다시 확인해 주세요.",
    "NETWORK_ERROR": "서버와 통신할 수 없습니다. 네트워크 상태를 확인해 주세요.",
    "UNKNOWN_ERROR": "알 수 없는 오류가 발생했습니다.",
}
