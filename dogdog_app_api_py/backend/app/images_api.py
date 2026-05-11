from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Query
from fastapi.responses import Response, JSONResponse

router = APIRouter(prefix="/api/v1/images", tags=["Images"])

ALLOWED_IMAGE_HOSTS = {
    "image.enuri.info",
    "photo3.enuri.info",
    "thumbnail.coupangcdn.com",
    "llis-pipeline.lotteon.com",
    "harimpetfood.cafe24.com"
}

@router.get("/proxy")
async def proxy_image(url: str = Query(...)):
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Invalid image URL"},
        )

    if parsed.netloc not in ALLOWED_IMAGE_HOSTS:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Image host is not allowed"},
        )

    try:
        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.enuri.com/",
            },
        ) as client:
            image_response = await client.get(url)

        if image_response.status_code != 200:
            return JSONResponse(
                status_code=image_response.status_code,
                content={
                    "success": False,
                    "message": "Failed to fetch image",
                },
            )

        content_type = image_response.headers.get("content-type", "image/jpeg")

        return Response(
            content=image_response.content,
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=86400",
            },
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(e),
            },
        )
