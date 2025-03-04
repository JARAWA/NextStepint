from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI(title="JOSAA Preference Generator")

# Setup static files and templates
static_path = Path(__file__).parent.parent / "static"
templates_path = Path(__file__).parent.parent / "templates"

app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory=templates_path)

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
        predictions = predict_preferences(
            jee_rank=jee_rank,
            category=category,
            college_type=college_type,
            preferred_branch=preferred_branch,
            round_no=round_no,
            min_probability=min_probability
        )
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "predictions": predictions,
                "jee_rank": jee_rank,
                "category": category,
                "college_type": college_type,
                "preferred_branch": preferred_branch,
                "round_no": round_no,
                "min_probability": min_probability
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)}
        )
