import pandas as pd
import numpy as np
import math
from typing import Dict, List
import plotly.express as px
import requests
from io import StringIO
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_data() -> pd.DataFrame:
    """Load and preprocess the JOSAA data."""
    try:
        # Load data from local file first
        data_path = Path(__file__).parent.parent / 'data' / 'josaa2024_cutoff.csv'
        if data_path.exists():
            logger.info(f"Loading data from local file: {data_path}")
            df = pd.read_csv(data_path)
        else:
            logger.info("Local file not found, attempting to load from GitHub")
            # Replace with your actual GitHub repository URL
            url = "https://raw.githubusercontent.com/YOUR_USERNAME/NextStep/main/josaa-service/data/josaa2024_cutoff.csv"
            response = requests.get(url)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
        
        # Data preprocessing
        df["Opening Rank"] = pd.to_numeric(df["Opening Rank"], errors="coerce").fillna(9999999)
        df["Closing Rank"] = pd.to_numeric(df["Closing Rank"], errors="coerce").fillna(9999999)
        df["Round"] = df["Round"].astype(str)
        
        logger.info(f"Successfully loaded {len(df)} records")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}", exc_info=True)
        return pd.DataFrame()

def get_unique_branches() -> List[str]:
    """Get list of unique branches from the dataset."""
    try:
        df = load_data()
        if df is not None and not df.empty:
            unique_branches = sorted(df["Academic Program Name"].dropna().unique().tolist())
            logger.info(f"Found {len(unique_branches)} unique branches")
            return ["All"] + unique_branches
        logger.warning("No branches found in dataset")
        return ["All"]
    except Exception as e:
        logger.error(f"Error getting unique branches: {str(e)}", exc_info=True)
        return ["All"]

def calculate_admission_probability(rank: int, opening_rank: float, closing_rank: float) -> float:
    """Calculate admission probability using hybrid approach."""
    try:
        # Input validation
        if not all(isinstance(x, (int, float)) for x in [rank, opening_rank, closing_rank]):
            raise ValueError("All inputs must be numeric")
        
        # Logistic function calculation
        M = (opening_rank + closing_rank) / 2
        S = max((closing_rank - opening_rank) / 10, 1)  # Ensure S is never zero
        logistic_prob = 1 / (1 + math.exp((rank - M) / S)) * 100

        # Piece-wise calculation
        if rank < opening_rank:
            improvement = (opening_rank - rank) / opening_rank
            if improvement >= 0.5:
                piece_wise_prob = 99.0
            else:
                piece_wise_prob = 96 + (improvement * 6)
        elif rank == opening_rank:
            piece_wise_prob = 95.0
        elif rank < closing_rank:
            range_width = closing_rank - opening_rank
            position = (rank - opening_rank) / range_width
            if position <= 0.2:
                piece_wise_prob = 94 - (position * 70)
            elif position <= 0.5:
                piece_wise_prob = 80 - ((position - 0.2) / 0.3 * 20)
            elif position <= 0.8:
                piece_wise_prob = 60 - ((position - 0.5) / 0.3 * 20)
            else:
                piece_wise_prob = 40 - ((position - 0.8) / 0.2 * 20)
        elif rank == closing_rank:
            piece_wise_prob = 15.0
        elif rank <= closing_rank + 10:
            piece_wise_prob = 5.0
        else:
            piece_wise_prob = 0.0

        # Combine probabilities
        if rank < opening_rank:
            improvement = (opening_rank - rank) / opening_rank
            final_prob = max(logistic_prob, 95) if improvement > 0.5 else (logistic_prob * 0.4 + piece_wise_prob * 0.6)
        elif rank <= closing_rank:
            final_prob = (logistic_prob * 0.7 + piece_wise_prob * 0.3)
        else:
            final_prob = 0.0 if rank > closing_rank + 100 else min(logistic_prob, 5)

        return round(max(min(final_prob, 100), 0), 2)  # Ensure probability is between 0 and 100
    except Exception as e:
        logger.error(f"Error in probability calculation: {str(e)}", exc_info=True)
        return 0.0

def get_admission_chances(probability: float) -> str:
    """Convert probability to text interpretation."""
    try:
        if not isinstance(probability, (int, float)):
            raise ValueError("Probability must be numeric")
        
        if probability >= 95:
            return "Very High Chance"
        elif probability >= 80:
            return "High Chance"
        elif probability >= 60:
            return "Moderate Chance"
        elif probability >= 40:
            return "Low Chance"
        elif probability > 0:
            return "Very Low Chance"
        return "No Chance"
    except Exception as e:
        logger.error(f"Error in getting admission chances: {str(e)}", exc_info=True)
        return "Error"

def create_probability_plot(df: pd.DataFrame) -> dict:
    """Create probability distribution visualization."""
    try:
        if df is None or df.empty:
            raise ValueError("DataFrame is empty or None")
            
        fig = px.histogram(
            df,
            x='Admission Probability (%)',
            title='Distribution of Admission Probabilities',
            nbins=20,
            color_discrete_sequence=['#3366cc']
        )
        fig.update_layout(
            xaxis_title="Admission Probability (%)",
            yaxis_title="Number of Colleges",
            showlegend=False,
            title_x=0.5
        )
        return fig.to_dict()
    except Exception as e:
        logger.error(f"Error in creating probability plot: {str(e)}", exc_info=True)
        return None
