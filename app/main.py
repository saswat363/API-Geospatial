from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.routes.files import router as files_router

app = FastAPI(
    title="Geospatial File Measurement API",
    description="API for processing geospatial files and calculating measurements.",
    version="1.0.0"
)

app.include_router(files_router)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")
