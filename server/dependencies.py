import os
from fastapi import Header, HTTPException


auth_token = os.getenv('AUTH_TOKEN')

async def get_token_header(x_token: str = Header(...)):
    if x_token != auth_token:
        raise HTTPException(status_code=400, detail="X-Token header invalid")
