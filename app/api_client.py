import httpx
import flet as ft
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000/api/v1"

class ApiClient:
    def __init__(self, page: ft.Page):
        self.page = page
        
    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        # [수정 1] Flet 0.81.0 최신 문법 (.store 추가)
        token = self.page.session.store.get("access_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
        
    # [수정 2] httpx Response 타입으로 변경 및 비동기(async) 처리
    async def _handle_response(self, response: httpx.Response) -> httpx.Response:
        if response.status_code == 401:
            # [수정 3] Flet 0.81.0 최신 문법 (.store 추가)
            if self.page.session.store.contains_key("access_token"):
                self.page.session.store.remove("access_token")
            if self.page.session.store.contains_key("refresh_token"):
                self.page.session.store.remove("refresh_token")
            self.page.go("/sign_up") 
        return response

    # [수정 4] requests -> httpx.AsyncClient 로 전면 교체
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        url = f"{BASE_URL}{endpoint}"
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(url, headers=self._get_headers(), params=params)
        return await self._handle_response(response)

    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> httpx.Response:
        url = f"{BASE_URL}{endpoint}"
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.post(url, headers=self._get_headers(), json=data)
        return await self._handle_response(response)

    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> httpx.Response:
        url = f"{BASE_URL}{endpoint}"
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.put(url, headers=self._get_headers(), json=data)
        return await self._handle_response(response)
        
    async def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> httpx.Response:
        url = f"{BASE_URL}{endpoint}"
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.patch(url, headers=self._get_headers(), json=data)
        return await self._handle_response(response)

    async def delete(self, endpoint: str) -> httpx.Response:
        url = f"{BASE_URL}{endpoint}"
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.delete(url, headers=self._get_headers())
        return await self._handle_response(response)