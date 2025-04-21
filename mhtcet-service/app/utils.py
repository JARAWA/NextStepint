import pandas as pd
import logging
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, file_path: str):
        """Initialize the DataManager with the CSV file path."""
        logger.info(f"Initializing DataManager with file path: {file_path}")
        self.file_path = file_path
        self.original_df = self.load_data()
        self.df = self.original_df.copy() if not self.original_df.empty else pd.DataFrame()
        self.initialize_dropdowns()

    def load_data(self) -> pd.DataFrame:
        """Load and validate the CSV data."""
        try:
            if not Path(self.file_path).exists():
                logger.error(f"File not found: {self.file_path}")
                return pd.DataFrame()

            df = pd.read_csv(self.file_path, encoding='cp1252')
            
            required_columns = [
                'college_code', 'college_name', 'branch_code', 'branch_name',
                'category_code', 'category', 'quota_type', 'allocation_type',
                'rank', 'percentile'
            ]

            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Missing columns: {missing_columns}")
                return pd.DataFrame()

            # Data cleaning and validation
            df = df.dropna(subset=['rank', 'college_name', 'branch_name'])
            df['rank'] = pd.to_numeric(df['rank'], errors='coerce')
            df = df.dropna(subset=['rank'])

            logger.info(f"Successfully loaded {len(df)} records")
            return df

        except Exception as e:
            logger.error(f"Error loading data: {str(e)}", exc_info=True)
            return pd.DataFrame()

    def initialize_dropdowns(self):
        """Initialize dropdown options."""
        if self.df.empty:
            self.categories = ["All"]
            self.quotas = ["All"]
            self.branches = ["All"]
            return

        self.categories = self.prepare_dropdown('category')
        self.quotas = self.prepare_dropdown('quota_type')
        self.branches = self.prepare_dropdown('branch_name')

    def prepare_dropdown(self, column: str) -> list:
        """Prepare dropdown options for a given column."""
        if self.df.empty:
            return ["All"]
        
        options = ["All"] + sorted([
            str(x) for x in self.df[column].unique() 
            if pd.notna(x) and str(x).lower() != 'not specified'
        ])
        logger.debug(f"Prepared {len(options)} options for {column}")
        return options

    def search_colleges(
        self, 
        rank: int, 
        category: str = "All", 
        quota: str = "All", 
        branch: str = "All",
        rank_range: int = 1000
    ) -> dict:
        """Search colleges based on given criteria."""
        try:
            if self.df.empty:
                logger.warning("Search attempted on empty DataFrame")
                return self.empty_search_result()

            logger.info(f"Searching with parameters: rank={rank}, category={category}, "
                       f"quota={quota}, branch={branch}")

            # Create base mask for rank range
            mask = (self.df['rank'] >= rank - 1000) & (self.df['rank'] <= rank + 3000)

            # Apply additional filters
            if category != "All":
                mask &= self.df['category'] == category
            if quota != "All":
                mask &= self.df['quota_type'] == quota
            if branch != "All":
                mask &= self.df['branch_name'] == branch

            # Apply mask and sort results
            results = self.df[mask].sort_values('rank')
            
            logger.info(f"Found {len(results)} matching results")

            return {
                'results': results.to_dict('records'),
                'total_matches': len(results),
                'rank_min': results['rank'].min() if not results.empty else 0,
                'rank_max': results['rank'].max() if not results.empty else 0,
                'unique_colleges': results['college_name'].nunique() if not results.empty else 0
            }

        except Exception as e:
            logger.error(f"Search error: {str(e)}", exc_info=True)
            return self.empty_search_result()

    def empty_search_result(self) -> dict:
        """Return empty search result structure."""
        return {
            'results': [],
            'total_matches': 0,
            'rank_min': 0,
            'rank_max': 0,
            'unique_colleges': 0
        }
