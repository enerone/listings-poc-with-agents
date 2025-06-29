from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api import listings, products
from app.models.database import engine, Base
from app.core.config import settings
from app.core.logger import configure_logging
from app.core.middleware import ErrorHandlingMiddleware, LoggingMiddleware

# Configure logging
configure_logging()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# Add middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="app/templates")

app.include_router(listings.router, prefix="/api/listings", tags=["listings"])
app.include_router(products.router, prefix="/api/products", tags=["products"])

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/listings")
async def listings_page(request: Request):
    return templates.TemplateResponse("listings.html", {"request": request})

@app.get("/create")
async def create_page(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})

@app.get("/test_js_syntax.html")
async def test_js_syntax():
    from fastapi.responses import FileResponse
    return FileResponse("test_js_syntax.html")

@app.get("/test_frontend_simple.html")
async def test_frontend_simple():
    from fastapi.responses import FileResponse
    return FileResponse("test_frontend_simple.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)