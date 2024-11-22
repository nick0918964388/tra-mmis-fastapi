import httpx
import ssl
from fastapi import HTTPException

async def make_api_request(url: str, headers: dict):
    # 創建自定義的 SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # 使用自定義的 SSL context 創建 client
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = {
                "status_code": e.response.status_code,
                "error_message": str(e),
                "response_text": e.response.text
            }
            raise HTTPException(status_code=e.response.status_code, detail=error_detail)
        except httpx.RequestError as e:
            error_detail = {
                "error_type": "RequestError",
                "error_message": str(e)
            }
            raise HTTPException(status_code=500, detail=error_detail)
        except Exception as e:
            error_detail = {
                "error_type": "UnexpectedError",
                "error_message": str(e)
            }
            raise HTTPException(status_code=500, detail=error_detail)
