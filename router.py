from fastapi import APIRouter, Query,Request, Header,HTTPException
from agent import process_query
from typing import Optional
router = APIRouter()
import json
@router.get("/health")
def health_check():
    return {"status": "healthy"}

@router.post("/query")
async def ai_query(
    request: Request,
    q: str = Query(..., description="User's natural language query"),
    authorization: Optional[str] = Header(None),
    device_id: Optional[str] = Header(None, alias="X-Device-Id"),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization token missing")
    if not device_id:
        raise HTTPException(status_code=400, detail="X-Device-Id header missing")

    token = "test"

    # 👇 safely get body (optional)
    raw_body = await request.body()
    body = json.loads(raw_body) if raw_body else {}

    return await process_query(q, token, body,device_id)
