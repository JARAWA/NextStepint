# app/utils.py
import pandas as pd
import numpy as np
import math
import logging
import plotly.express as px
import requests
from io import StringIO
from pathlib import Path
from typing import Dict, List, Union, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_data(force_reload: bool = False) -> pd.DataFrame:
    """
    Load and preprocess the JOSAA data from local or remote source.
    
    Args:
        force_reload (bool, optional): Force reloading of data. Defaults to False.
    
    Returns:
        pd.DataFrame: Preprocessed JOSAA counseling data
    """
    try:
        # Attempt to load from local file
        data_path = Path(__file__).parent.parent / 'data' / 'josaa2024_cutoff.csv'
        
        if data_path.exists():
            logger.info(f"Loading data from local file: {data_path}")
            df = pd.read_csv(data_path)
        else:
            # Fallback to GitHub raw file
            logger.info("Local file not found, attempting to load from GitHub")
            url = "https://raw.githubusercontent.com/YOUR_USERNAME/NextStep/main/josaa-service/data/josaa2024_cutoff.csv"
            response = requests.get(url)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
        
        # Data preprocessing and validation
        df = preprocess_dataframe(df)
        
        logger.info(f"Successfully loaded {len(df)} records")
        return df
    
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}", exc_info=True)
        return pd.DataFrame()

def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess and clean the DataFrame.
    
    Args:
        df (pd.DataFrame): Input DataFrame
    
    Returns:
        pd.DataFrame: Preprocessed DataFrame
    """
    try:
        # Convert rank columns to numeric
        rank_columns = ['Opening Rank', 'Closing Rank']
        for col in rank_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(9999999)
        
        # Ensure Round is string
        df['Round'] = df['Round'].astype(str)
        
        # Additional data cleaning
        df['Institute'] = df['Institute'].fillna('Unknown')
        df['Academic Program Name'] = df['Academic Program Name'].fillna('Unknown')
        df['Category'] = df['Category'].fillna('Unknown')
        
        # Validate required columns
        required_columns = [
            'Institute', 'College Type', 'Location', 
            'Academic Program Name', 'Quota', 'Category', 
            'Gender', 'Opening Rank', 'Closing Rank', 'Round'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.warning(f"Missing columns: {missing_columns}")
        
        return df
    
    except Exception as e:
        logger.error(f"DataFrame preprocessing error: {str(e)}", exc_info=True)
        return df

def get_unique_branches() -> List[str]:
    """
    Retrieve unique academic program names.
    
    Returns:
        List[str]: List of unique branches
    """
    try:
        df = load_data()
        if not df.empty:
            unique_branches = sorted(df["Academic Program Name"].dropna().unique().tolist())
            logger.info(f"Found {len(unique_branches)} unique branches")
            return ["All"] + unique_branches
        
        logger.warning("No branches found in dataset")
        return ["All"]
    
    except Exception as e:
        logger.error(f"Error getting unique branches: {str(e)}", exc_info=True)
        return ["All"]

def calculate_admission_probability(
    rank: int, 
    opening_rank: float, 
    closing_rank: float
) -> float:
    """
    Calculate admission probability using a sophisticated hybrid approach.
    
    Args:
        rank (int): Candidate's JEE rank
        opening_rank (float): Opening rank for the program
        closing_rank (float): Closing rank for the program
    
    Returns:
        float: Admission probability percentage
    """
    try:
        # Handle edge cases
        if not all(isinstance(x, (int, float)) for x in [rank, opening_rank, closing_rank]):
            logger.warning(f"Invalid input types: {type(rank)}, {type(opening_rank)}, {type(closing_rank)}")
            return 0.0
        
        # Prevent division by zero
        if opening_rank == closing_rank:
            return 50.0 if rank <= opening_rank else 0.0
        
        # Logistic function calculation
        midpoint = (opening_rank + closing_rank) / 2
        scale = max((closing_rank - opening_rank) / 10, 1)
        
        # Logistic probability
        logistic_prob = 1 / (1 + math.exp((rank - midpoint) / scale)) * 100
        
        # Piece-wise probability calculation
        if rank < opening_rank:
            improvement = (opening_rank - rank) / opening_rank
            piece_wise_prob = 99.0 if improvement >= 0.5 else 96 + (improvement * 6)
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
        
        return round(max(min(final_prob, 100), 0), 2)
    
    except Exception as e:
        logger.error(f"Probability calculation error: {str(e)}", exc_info=True)
        return 0.0

def get_admission_chances(probability: float) -> str:
    """
    Convert probability to text interpretation.
    
    Args:
        probability (float): Admission probability percentage
    
    Returns:
        str: Admission chance description
    """
    try:
        if not isinstance(probability, (int, float)):
            raise ValueError("Probability must be a number")
        
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
        logger.error(f"Admission chances error: {str(e)}", exc_info=True)
        return "Error"

def predict_preferences(
    jee_rank: int,
    category: str,
    college_type: str,
    preferred_branch: str,
    round_no: str,
    min_probability: float = 30.0
) -> Dict[str, Union[List[Dict], Dict]]:
    """
    Predict college preferences based on input parameters.
    
    Args:
        jee_rank (int): Candidate's JEE rank
        category (str): Reservation category
        college_type (str): Type of college
        preferred_branch (str): Preferred academic program
        round_no (str): Counseling round number
        min_probability (float, optional): Minimum admission probability. Defaults to 30.0.
    
    Returns:
        Dict containing predictions and plot data
    """
    try:
        # Load data
        df = load_data()
        
        # Create a copy of the DataFrame
        filtered_df = df.copy()
        
        # Filtering logic
        if category != "ALL":
            filtered_df = filtered_df[filtered_df["Category"] == category]
        
        if college_type != "ALL":
            filtered_df = filtered_df[filtered_df["College Type"] == college_type]
        
        if preferred_branch != "All":
            filtered_df = filtered_df[filtered_df["Academic Program Name"] == preferred_branch]
        
        # Round filtering
        filtered_df = filtered_df[filtered_df["Round"] == round_no]
        
        # Calculate admission probabilities
        predictions = []
        for _, row in filtered_df.iterrows():
            prob = calculate_admission_probability(
                jee_rank, 
                row["Opening Rank"], 
                row["Closing Rank"]
            )
            
            if prob >= min_probability:
                prediction = {
                    "institute": row["Institute"],
                    "college_type": row["College Type"],
                    "location": row["Location"],
                    "academic_program": row["Academic Program Name"],
                    "quota": row["Quota"],
                    "category": row["Category"],
                    "gender": row["Gender"],
                    "admission_probability": prob,
                    "admission_chances": get_admission_chances(prob),
                    "opening_rank": row["Opening Rank"],
                    "closing_rank": row["Closing Rank"]
                }
                predictions.append(prediction)
        
        # Sort predictions by admission probability in descending order
        predictions.sort(key=lambda x: x["admission_probability"], reverse=True)
        
        # Create plot data
        plot_data = create_probability_plot(predictions)
        
        return {
            "predictions": predictions,
            "plot_data": plot_data
        }
    
    except Exception as e:
        logger.error(f"Comprehensive prediction error: {str(e)}", exc_info=True)
        return {"predictions": [], "plot_data": {}}

def create_probability_plot(predictions: List[Dict]) -> Dict:
    """
    Create probability distribution visualization.
    
    Args:
        predictions (List[Dict]): List of prediction dictionaries
    
    Returns:
        Dict: Plotly figure configuration
    """
    try:
        if not predictions:
            return {}
        
        # Convert predictions to DataFrame
        plot_df = pd.DataFrame(predictions)
        
        # Create histogram
        fig = px.histogram(
            plot_df, 
            x='admission_probability', 
            title='Distribution of Admission Probabilities',
            labels={'admission_probability': 'Admission Probability (%)'},
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
        logger.error(f"Plot creation error: {str(e)}", exc_info=True)
        return {}

# Optional: Add caching mechanism for expensive computations
def cache_data(func):
    """
    Simple caching decorator to store and reuse expensive computation results.
    """
    cache = {}
    
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    return wrapper
