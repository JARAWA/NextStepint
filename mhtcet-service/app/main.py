from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import io
import logging
from pathlib import Path
from .models import SearchFilters, SearchResponse
from .services import MHTCETService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MHTCET College Finder",
    description="College search tool for MHTCET counselling",
    version="1.0.0"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup static files and templates
static_path = Path(__file__).parent.parent / "static"
templates_path = Path(__file__).parent.parent / "templates"

app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory=templates_path)

# Initialize service
mhtcet_service = MHTCETService()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page route."""
    try:
        options = mhtcet_service.get_dropdown_options()
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                **options
            }
        )
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Application is not properly initialized"}
        )

@app.post("/search")
async def search_colleges(
    request: Request,
    rank: int = Form(...),
    category: str = Form(default="All"),
    quota: str = Form(default="All"),
    branch: str = Form(default="All")
):
    """Search colleges endpoint."""
    try:
        search_results = mhtcet_service.search_colleges(
            rank=rank,
            category=category,
            quota=quota,
            branch=branch,
            rank_range=1000
        )
        
        options = mhtcet_service.get_dropdown_options()
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                **options,
                "rank": rank,
                "category": category,
                "quota": quota,
                "branch": branch,
                **search_results
            }
        )
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)}
        )

@app.post("/export")
async def export_results(
    rank: int = Form(...),
    category: str = Form(default="All"),
    quota: str = Form(default="All"),
    branch: str = Form(default="All")
):
    """Export search results to CSV."""
    try:
        search_results = mhtcet_service.search_colleges(
            rank=rank,
            category=category,
            quota=quota,
            branch=branch,
            rank_range=1000
        )
        
        if not search_results['results']:
            raise HTTPException(status_code=404, detail="No results to export")

        df = mhtcet_service.export_results(search_results['results'])
        
        output = io.StringIO()
        df.to_csv(output, index=False)
        
        response = StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=college_results.csv"
            }
        )
        return response

    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "data_loaded": bool(mhtcet_service.data_manager.df is not None),
        "data_size": len(mhtcet_service.data_manager.df)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
