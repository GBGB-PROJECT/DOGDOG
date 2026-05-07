# =========================================================
# 🔥 불량현황 Service
# - view/API에서 repository 함수를 바로 가져다 쓸 수 있게 export
# =========================================================

from .defective_repository import count_defectives, fetch_defectives


__all__ = [
    "count_defectives",
    "fetch_defectives",
]
