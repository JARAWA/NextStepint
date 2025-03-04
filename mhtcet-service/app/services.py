from .utils import DataManager
from pathlib import Path
import pandas as pd

class MHTCETService:
    def __init__(self):
        data_file = Path(__file__).parent.parent / 'data' / 'Structured_MHTCET_Cutoffs_with_validation.csv'
        self.data_manager = DataManager(str(data_file))

    def get_dropdown_options(self):
        """Get all dropdown options."""
        return {
            'categories': self.data_manager.categories,
            'quotas': self.data_manager.quotas,
            'branches': self.data_manager.branches
        }

    def search_colleges(self, rank: int, category: str, quota: str, branch: str, rank_range: int):
        """Search colleges based on criteria."""
        return self.data_manager.search_colleges(
            rank=rank,
            category=category,
            quota=quota,
            branch=branch,
            rank_range=rank_range
        )

    def export_results(self, results: list) -> pd.DataFrame:
        """Convert results to DataFrame for export."""
        return pd.DataFrame(results)
