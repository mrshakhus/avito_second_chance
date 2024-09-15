from fastapi import FastAPI
from src.ping.router import router as ping_router
from src.tenders.router import router as tenders_router
from src.bids.router import router as bids_router

app = FastAPI(
    title="Тендеры",
    root_path="/api"
)

app.include_router(ping_router)
app.include_router(tenders_router)
app.include_router(bids_router)