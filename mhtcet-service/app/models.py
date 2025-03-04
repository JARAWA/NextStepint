from pydantic import BaseModel
from typing import List, Optional

class SearchResult(BaseModel):
    college_code: str
    college_name: str
    branch_code: str
    branch_name: str
    category_code: str
    category: str
    quota_type: str
    allocation_type: str
    rank: float
    percentile: float

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_matches: int
    rank_min: float
    rank_max: float
    unique_colleges: int

class SearchFilters(BaseModel):
    rank: int
    category: str = "All"
    quota: str = "All"
    branch: str = "All"
    rank_range: int = 1000
