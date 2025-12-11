from fastapi import Request, HTTPException, status
from app.settings import settings

def verify_api_key(request: Request):
    api_key = request.headers.get("x-api-key")

    if not api_key or api_key.strip() != settings.fast_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Unauthorized: Invalid or missing API Key"
        )