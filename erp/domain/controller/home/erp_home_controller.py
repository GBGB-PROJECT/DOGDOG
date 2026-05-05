import time

import httpx


BASE_URL = "http://127.0.0.1:8000"
_CLIENT = httpx.Client(base_url=BASE_URL, timeout=5.0)
_GET_CACHE = {}
_GET_CACHE_TTL_SECONDS = 10.0


def _cache_key(path: str, params: dict | None = None):
    return path, tuple(sorted((params or {}).items()))


def _get_data(path: str, params: dict | None = None):
    key = _cache_key(path, params)
    now = time.monotonic()
    cached = _GET_CACHE.get(key)
    if cached and now - cached["time"] <= _GET_CACHE_TTL_SECONDS:
        return cached["data"]

    response = _CLIENT.get(path, params=params)
    response.raise_for_status()
    data = response.json().get("data")
    _GET_CACHE[key] = {"time": now, "data": data}
    return data


class HomeViewMain:
    @staticmethod
    def sale_dashboard():
        try:
            return _get_data("/erp/home/sale_dashboard")
        except httpx.ConnectError as exc:
            raise Exception("서버 연결 실패") from exc
        except httpx.TimeoutException as exc:
            raise Exception("응답 시간 초과") from exc
        except Exception as exc:
            raise Exception(f"기타 오류 발생: {exc}") from exc

    @staticmethod
    def inventory_dashboard():
        try:
            return _get_data("/erp/home/inventory_dashboard")
        except httpx.ConnectError as exc:
            raise Exception("서버 연결 실패") from exc
        except httpx.TimeoutException as exc:
            raise Exception("응답 시간 초과") from exc
        except Exception as exc:
            raise Exception(f"기타 오류 발생: {exc}") from exc

    @staticmethod
    def sale_chart(period: str = "1개월"):
        try:
            return _get_data(
                "/erp/home/chart_dashboard_sale",
                params={"period": period},
            )
        except httpx.ConnectError as exc:
            raise Exception("서버 연결 실패") from exc
        except httpx.TimeoutException as exc:
            raise Exception("응답 시간 초과") from exc
        except Exception as exc:
            raise Exception(f"기타 오류 발생: {exc}") from exc

    @staticmethod
    def prduct_defect_chart(period: str = "1개월"):
        try:
            return _get_data("/erp/home/chart_dashboard_production")
        except httpx.ConnectError as exc:
            raise Exception("서버 연결 실패") from exc
        except httpx.TimeoutException as exc:
            raise Exception("응답 시간 초과") from exc
        except Exception as exc:
            raise Exception(f"기타 오류 발생: {exc}") from exc
