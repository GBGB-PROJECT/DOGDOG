
def set_view_prefilter(holder, **values):
    # 🔥 대시보드 카드 → 조회 화면 필터 전달 공통 저장
    holder["value"] = values


def consume_view_prefilter(holder):
    # 🔥 필터는 한 번 소비 후 제거
    value = holder.get("value")
    holder["value"] = None
    return value or {}
