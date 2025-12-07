from fastapi import Request, HTTPException, status
from app.utils.env import FAST_API_KEY

def verify_api_key(request: Request):
    api_key = request.headers.get("x-api-key")

    if not api_key or api_key.strip().lower() != FAST_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Unauthorized: Invalid or missing API Key"
        )