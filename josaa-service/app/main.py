from fastapi import FastAPI, Request, Form, HTTPException, Depends, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging
from datetime import datetime
import os
from typing import Optional
from .utils import get_unique_branches
from .services import predict_preferences
from .auth import (
    register_user, 
    authenticate_user, 
    create_access_token, 
    verify_token,
    User
)

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nextstep-nexn.onrender.com"],  # Update this with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup static files and templates
static_path = Path(__file__).parent.parent / "static"
templates_path = Path(__file__).parent.parent / "templates"

app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory=templates_path)

# Authentication dependency
''' async def get_current_user(access_token: str = Cookie(None)) -> Optional[User]:
    if not access_token:
        return None
    payload = verify_token(access_token)
    if not payload:
        return None
    email = payload.get("sub")
    if not email:
        return None
    return await authenticate_user(email, None)'''

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

'''@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user)
):'''
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
                "branches": branches,
                "user": current_user
            }
        )
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Application is not properly initialized"}
        )

@app.post("/auth/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...)
):
    """Handle user registration."""
    try:
        success = await register_user(email, password, full_name)
        if not success:
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "error": "Email already registered"
                }
            )
        
        user = await authenticate_user(email, password)
        if not user:
            raise HTTPException(status_code=400, detail="Registration failed")
        
        access_token = create_access_token({"sub": user.email})
        response = templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "message": "Registration successful",
                "user": user
            }
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=1800
        )
        return response
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/auth/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False)
):
    """Handle user login."""
    try:
        user = await authenticate_user(email, password)
        if not user:
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "error": "Invalid email or password"
                }
            )
        
        access_token = create_access_token({"sub": user.email})
        response = templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "message": "Login successful",
                "user": user
            }
        )
        
        max_age = 30 * 24 * 60 * 60 if remember else 1800  # 30 days or 30 minutes
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=max_age
        )
        return response
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/auth/logout")
async def logout(request: Request):
    """Handle user logout."""
    response = templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "message": "Logout successful"
        }
    )
    response.delete_cookie("access_token")
    return response

@app.post("/predict")
async def predict(
    request: Request,
    current_user: User = Depends(get_current_user),
    jee_rank: int = Form(...),
    category: str = Form(...),
    college_type: str = Form(...),
    preferred_branch: str = Form(...),
    round_no: str = Form(...),
    min_probability: float = Form(30.0)
):
    """Generate college predictions."""
    if not current_user:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": "Please login to generate preferences"
            }
        )
    
    try:
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
                "min_probability": min_probability,
                "user": current_user
            }
        )
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
