from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging
import os
from datetime import datetime

# Import utility functions
from .utils import (
    load_data, 
    get_unique_branches, 
    predict_preferences
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="JOSAA Preference Predictor",
    description="Predict college preferences for JOSAA counseling",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider restricting in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path configurations
BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Configure templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.on_event("startup")
async def startup_event():
    """
    Perform startup checks and initializations
    """
    try:
        # Validate directories
        if not STATIC_DIR.exists():
            logger.warning(f"Static directory not found: {STATIC_DIR}")
        
        if not TEMPLATES_DIR.exists():
            logger.warning(f"Templates directory not found: {TEMPLATES_DIR}")
        
        # Optional: Preload or warm-up data
        load_data()
        
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}", exc_info=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Render the home page with dropdown options
    """
    try:
        # Prepare dropdown options
        context = {
            "request": request,
            "categories": ["OPEN", "OBC-NCL", "SC", "ST", "EWS"],
            "college_types": ["ALL", "IIT", "NIT", "IIIT", "GFTI"],
            "rounds": ["1", "2", "3", "4", "5", "6"],
            "branches": get_unique_branches()
        }
        return templates.TemplateResponse("index.html", context)
    
    except Exception as e:
        logger.error(f"Home page rendering error: {str(e)}", exc_info=True)
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)

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
    """
    Generate college predictions based on input parameters
    """
    try:
        # Validate input parameters
        if jee_rank <= 0:
            raise ValueError("JEE Rank must be a positive number")
        
        # Call prediction service
        prediction_results = predict_preferences(
            jee_rank=jee_rank,
            category=category,
            college_type=college_type,
            preferred_branch=preferred_branch,
            round_no=round_no,
            min_probability=min_probability
        )
        
        # Prepare context for template rendering
        context = {
            "request": request,
            "predictions": prediction_results.get('predictions', []),
            "plot_data": prediction_results.get('plot_data', {}),
            "categories": ["OPEN", "OBC-NCL", "SC", "ST", "EWS"],
            "college_types": ["ALL", "IIT", "NIT", "IIIT", "GFTI"],
            "rounds": ["1", "2", "3", "4", "5", "6"],
            "branches": get_unique_branches(),
            
            # Preserve form inputs for sticky form
            "jee_rank": jee_rank,
            "category": category,
            "college_type": college_type,
            "preferred_branch": preferred_branch,
            "round_no": round_no,
            "min_probability": min_probability
        }
        
        return templates.TemplateResponse("index.html", context)
    
    except ValueError as ve:
        logger.warning(f"Validation error: {str(ve)}")
        return JSONResponse(
            content={"error": str(ve)}, 
            status_code=400
        )
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"error": "An unexpected error occurred during prediction"}, 
            status_code=500
        )

@app.get("/health")
async def health_check():
    """
    Provide a simple health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "data_loaded": bool(load_data().shape[0])
    }

@app.get("/branches")
async def get_branches():
    """
    Endpoint to retrieve unique branches
    """
    try:
        branches = get_unique_branches()
        return {"branches": branches}
    except Exception as e:
        logger.error(f"Error retrieving branches: {str(e)}")
        return {"branches": []}

# Application entry point
if __name__ == "__main__":
    import uvicorn
    
    # Use environment variable or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=True
    )
