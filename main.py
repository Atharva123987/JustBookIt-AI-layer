import uvicorn
from fastapi import FastAPI
from router import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Movie Booking AI Agent")
origins = [
    "http://localhost:5173",  # React frontend (Vite dev server)
    "http://127.0.0.1:5173",  # sometimes vite uses this
    "http://0.0.0.0",  # sometimes vite uses this
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routes
app.include_router(router, prefix="/ai")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
