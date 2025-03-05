from fastapi import FastAPI, Request, Form, HTTPException, Depends, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging
from datetime import datetime
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
    allow_origins=["*"],  # Update this with your frontend URL in production
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
async def get_current_user(access_token: str = Cookie(None)) -> Optional[User]:
    if not access_token:
        return None
    payload = verify_token(access_token)
    if not payload:
        return None
    email = payload.get("sub")
    if not email:
        return None
    return await authenticate_user(email, None)

@app.post("/auth/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...)
):
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
        
        max_age = 30 * 24 * 60 * 60 if remember else 1800
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
    response = templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "message": "Logout successful"
        }
    )
    response.delete_cookie("access_token")
    return response

# Update existing endpoints to use authentication
@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user)
):
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
    if not current_user:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": "Please login to generate preferences"
            }
        )
    
    # Rest of the prediction logic remains the same
    # [Previous prediction code]
