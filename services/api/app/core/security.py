"""
JWT verification and rate-limiting helpers.
"""
from fastapi import HTTPException, Request, status


async def verify_token(request: Request) -> str:
    """
    Simple bearer-token check.
    Replace with a full JWT library (python-jose) in production.
    """
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    return auth.removeprefix("Bearer ").strip()
