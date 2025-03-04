"""
JOSAA College Preference Generator Service
----------------------------------------
This package provides functionality for generating college preference lists
based on JEE ranks and other criteria for JOSAA counselling.
"""

import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler(  # Log to file
            filename=Path(__file__).parent.parent / 'logs' / 'josaa_service.log',
            mode='a'
        )
    ]
)

# Create logger for this package
logger = logging.getLogger(__name__)

# Version info
__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main components
try:
    from .main import app
    from .models import PredictionInput, PredictionOutput
    from .services import predict_preferences
    from .utils import (
        load_data,
        get_unique_branches,
        calculate_admission_probability,
        get_admission_chances,
        create_probability_plot
    )

    logger.info(f"JOSAA Service initialized successfully (version {__version__})")
except Exception as e:
    logger.error(f"Error initializing JOSAA Service: {str(e)}", exc_info=True)
    raise

# Define what should be imported with "from app import *"
__all__ = [
    'app',
    'PredictionInput',
    'PredictionOutput',
    'predict_preferences',
    'load_data',
    'get_unique_branches',
    'calculate_admission_probability',
    'get_admission_chances',
    'create_probability_plot'
]

# Create necessary directories
try:
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
except Exception as e:
    logger.warning(f"Could not create log directory: {str(e)}")

# Package metadata
metadata = {
    'name': 'josaa_service',
    'version': __version__,
    'description': 'JOSAA College Preference Generator Service',
    'author': __author__,
    'email': __email__,
    'status': 'active',
    'dependencies': [
        'fastapi',
        'uvicorn',
        'pandas',
        'numpy',
        'plotly',
        'python-multipart',
        'pydantic',
        'requests',
        'jinja2'
    ]
}

def get_version():
    """Return the current version of the package."""
    return __version__

def get_metadata():
    """Return package metadata."""
    return metadata

def check_dependencies():
    """Check if all required dependencies are installed."""
    import pkg_resources
    
    missing = []
    for dep in metadata['dependencies']:
        try:
            pkg_resources.require(dep)
        except pkg_resources.DistributionNotFound:
            missing.append(dep)
    
    if missing:
        logger.warning(f"Missing dependencies: {', '.join(missing)}")
        return False
    return True

# Run dependency check on import
if not check_dependencies():
    logger.warning("Some dependencies are missing. Please install all required packages.")

# Initialize data loading
try:
    initial_data = load_data()
    if initial_data.empty:
        logger.warning("Initial data loading failed or returned empty dataset")
    else:
        logger.info(f"Successfully loaded initial dataset with {len(initial_data)} records")
except Exception as e:
    logger.error(f"Error during initial data loading: {str(e)}", exc_info=True)
