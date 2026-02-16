# API module initialization
from flask import Blueprint

# Create API blueprint
api_bp = Blueprint('api', __name__)

# Import all API modules to register their routes
from . import cosmic_events, evolutionary_events, correlations
