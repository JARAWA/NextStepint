from pydantic import BaseModel
from typing import List, Optional

class PredictionInput(BaseModel):
    jee_rank: int
    category: str
    college_type: str
    preferred_branch: str
    round_no: str
    min_probability: float = 0

class College(BaseModel):
    Preference: int
    Institute: str
    College_Type: str
    Location: str
    Branch: str
    Opening_Rank: float
    Closing_Rank: float
    Admission_Probability: float
    Admission_Chances: str

class PredictionOutput(BaseModel):
    preferences: List[College]
    plot_data: Optional[dict] = None
