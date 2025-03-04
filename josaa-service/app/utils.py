import pandas as pd
import numpy as np
import math
from typing import Dict, List
import plotly.express as px
import requests
from io import StringIO

def load_data() -> pd.DataFrame:
    """Load and preprocess the JOSAA data."""
    try:
        url = "https://raw.githubusercontent.com/JARAWA/NextStepint/refs/heads/main/josaa-service/data/josaa2024_cutoff.csv"
        response = requests.get(url)
        response.raise_for_status()
        
        df = pd.read_csv(StringIO(response.text))
        df["Opening Rank"] = pd.to_numeric(df["Opening Rank"], errors="coerce").fillna(9999999)
        df["Closing Rank"] = pd.to_numeric(df["Closing Rank"], errors="coerce").fillna(9999999)
        df["Round"] = df["Round"].astype(str)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

def get_unique_branches() -> List[str]:
    """Get list of unique branches from the dataset."""
    df = load_data()
    if df is not None and not df.empty:
        unique_branches = sorted(df["Academic Program Name"].dropna().unique().tolist())
        return ["All"] + unique_branches
    return ["All"]

def calculate_admission_probability(rank: int, opening_rank: float, closing_rank: float) -> float:
    """Calculate admission probability using hybrid approach."""
    try:
        # Logistic function calculation
        M = (opening_rank + closing_rank) / 2
        S = (closing_rank - opening_rank) / 10
        if S == 0:
            S = 1
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

        return round(final_prob, 2)
    except Exception as e:
        print(f"Error in probability calculation: {str(e)}")
        return 0.0

def get_admission_chances(probability: float) -> str:
    """Convert probability to text interpretation."""
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

def create_probability_plot(df: pd.DataFrame) -> dict:
    """Create probability distribution visualization."""
    try:
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
        print(f"Error in plotting: {str(e)}")
        return None
