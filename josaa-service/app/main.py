from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import PredictionInput, PredictionOutput
from .services import JOSAAService
from .utils import get_unique_branches

app = FastAPI(
    title="JOSAA Preference Generator",
    description="Generate college preference lists for JOSAA counselling",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize service
josaa_service = JOSAAService()

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "JOSAA Preference Generator API"}

@app.get("/branches")
async def get_branches():
    """Get list of available branches."""
    return {"branches": get_unique_branches()}

@app.post("/predict", response_model=PredictionOutput)
async def predict_preferences(input_data: PredictionInput):
    """Generate college preference list."""
    try:
        preferences, plot_data = josaa_service.predict_preferences(
            jee_rank=input_data.jee_rank,
            category=input_data.category,
            college_type=input_data.college_type,
            preferred_branch=input_data.preferred_branch,
            round_no=input_data.round_no,
            min_probability=input_data.min_probability
        )
        
        if not preferences:
            raise HTTPException(
                status_code=404,
                detail="No colleges found matching your criteria"
            )
            
        return PredictionOutput(
            preferences=preferences,
            plot_data=plot_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
