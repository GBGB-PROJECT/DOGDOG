# =========================================================
# 🔥 생산입고 Service
# - view/API에서 repository 함수를 바로 가져다 쓸 수 있게 export
# =========================================================

from .inbound_repository import count_inbounds, fetch_inbounds


__all__ = [
    "count_inbounds",
    "fetch_inbounds",
]
