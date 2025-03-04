from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
import logging
from datetime import datetime
from .utils import get_unique_branches
from .services import predict_preferences

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="JOSAA Preference Generator",
    description="Generate college preference lists for JOSAA counselling",
    version="1.0.0"
)

# Setup static files and templates
static_path = Path(__file__).parent.parent / "static"
templates_path = Path(__file__).parent.parent / "templates"

app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory=templates_path)

@app.on_event("startup")
async def startup_event():
    """Perform startup checks."""
    try:
        # Check template directory
        if not templates_path.exists():
            logger.error("Templates directory not found")
            raise Exception("Templates missing")
            
        # Check static directory
        if not static_path.exists():
            logger.error("Static directory not found")
            raise Exception("Static files missing")
            
        logger.info("All startup checks passed successfully")
    except Exception as e:
        logger.error(f"Startup checks failed: {str(e)}")
        raise

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page route."""
    try:
        categories = ["OPEN", "OBC-NCL", "SC", "ST", "EWS"]
        college_types = ["ALL", "IIT", "NIT", "IIIT", "GFTI"]
        rounds = ["1", "2", "3", "4", "5", "6"]
        branches = get_unique_branches()
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "categories": categories,
                "college_types": college_types,
                "rounds": rounds,
                "branches": branches
            }
        )
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Application is not properly initialized"}
        )

@app.post("/predict")
async def predict(
    request: Request,
    jee_rank: int = Form(...),
    category: str = Form(...),
    college_type: str = Form(...),
    preferred_branch: str = Form(...),
    round_no: str = Form(...),
    min_probability: float = Form(30.0)
):
    """Generate predictions based on form input."""
    try:
        logger.info(f"Generating predictions for rank: {jee_rank}, category: {category}")
        predictions, plot_data = predict_preferences(
            jee_rank=jee_rank,
            category=category,
            college_type=college_type,
            preferred_branch=preferred_branch,
            round_no=round_no,
            min_probability=min_probability
        )
        
        categories = ["OPEN", "OBC-NCL", "SC", "ST", "EWS"]
        college_types = ["ALL", "IIT", "NIT", "IIIT", "GFTI"]
        rounds = ["1", "2", "3", "4", "5", "6"]
        branches = get_unique_branches()

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "predictions": predictions,
                "plot_data": plot_data,
                "categories": categories,
                "college_types": college_types,
                "rounds": rounds,
                "branches": branches,
                "jee_rank": jee_rank,
                "category": category,
                "college_type": college_type,
                "preferred_branch": preferred_branch,
                "round_no": round_no,
                "min_probability": min_probability
            }
        )
    except Exception as e:
        logger.error(f"Error in predict route: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)}
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.head("/")
async def head():
    """Handle HEAD requests."""
    return HTMLResponse(content="")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
