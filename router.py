from fastapi import APIRouter, Query
from agent import process_query

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "healthy"}

@router.post("/query")
async def ai_query(q: str = Query(..., description="User's natural language query"), ip: dict = {}):
    """
    Example queries:
    - 'Show me movies playing in Mumbai'
    - 'Book 2 seats for Oppenheimer tomorrow evening'
    """
    return await process_query(q,ip)
