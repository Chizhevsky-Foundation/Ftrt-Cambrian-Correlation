from flask import jsonify, request
from app.api import api_bp
from app.core.cosmic_evolution_correlator import CosmicEvolutionCorrelator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Initialize the correlator
correlator = CosmicEvolutionCorrelator()

@api_bp.route('/correlations', methods=['GET'])
def get_correlations():
    """
    Endpoint to get correlations between cosmic and evolutionary events
    Query parameters:
    - start_date: Start date in ISO format (YYYY-MM-DD)
    - end_date: End date in ISO format (YYYY-MM-DD)
    - max_lag_days: Maximum time lag in days to consider (default: 365)
    """
    try:
        # Get query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        max_lag_days = int(request.args.get('max_lag_days', 365))
        
        # Set default dates if not provided
        if not start_date_str:
            start_date = datetime(2000, 1, 1)
        else:
            start_date = datetime.fromisoformat(start_date_str)
            
        if not end_date_str:
            end_date = datetime.now()
        else:
            end_date = datetime.fromisoformat(end_date_str)
        
        # Perform correlation analysis
        results = correlator.correlate_events(start_date, end_date, max_lag_days)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': f"Correlation analysis completed for period {start_date} to {end_date}"
        })
    
    except Exception as e:
        logger.error(f"Error in correlation analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': "Failed to complete correlation analysis"
        }), 500

@api_bp.route('/correlations/summary', methods=['GET'])
def get_correlation_summary():
    """
    Endpoint to get a summary of correlation results
    """
    try:
        # Get query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        max_lag_days = int(request.args.get('max_lag_days', 365))
        
        # Set default dates if not provided
        if not start_date_str:
            start_date = datetime(2000, 1, 1)
        else:
            start_date = datetime.fromisoformat(start_date_str)
            
        if not end_date_str:
            end_date = datetime.now()
        else:
            end_date = datetime.fromisoformat(end_date_str)
        
        # Perform correlation analysis
        results = correlator.correlate_events(start_date, end_date, max_lag_days)
        
        # Extract summary information
        summary = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'cosmic_events_count': len(results['cosmic_events']),
            'evolutionary_events_count': len(results['evolutionary_events']),
            'best_correlation': results['best_correlation'],
            'significant_correlations': len([r for r in results['correlation_results'] if r['significant']]),
            'cosmic_clusters': len(results['cosmic_clusters']),
            'evolutionary_clusters': len(results['evolutionary_clusters'])
        }
        
        return jsonify({
            'success': True,
            'data': summary,
            'message': "Correlation summary generated successfully"
        })
    
    except Exception as e:
        logger.error(f"Error generating correlation summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': "Failed to generate correlation summary"
        }), 500

@api_bp.route('/correlations/statistical-significance', methods=['GET'])
def get_statistical_significance():
    """
    Endpoint to get statistical significance of correlations
    """
    try:
        # Get query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        max_lag_days = int(request.args.get('max_lag_days', 365))
        significance_threshold = float(request.args.get('significance_threshold', 0.05))
        
        # Set default dates if not provided
        if not start_date_str:
            start_date = datetime(2000, 1, 1)
        else:
            start_date = datetime.fromisoformat(start_date_str)
            
        if not end_date_str:
            end_date = datetime.now()
        else:
            end_date = datetime.fromisoformat(end_date_str)
        
        # Perform correlation analysis
        results = correlator.correlate_events(start_date, end_date, max_lag_days)
        
        # Filter for significant correlations
        significant_correlations = [
            r for r in results['correlation_results'] 
            if r['p_value'] < significance_threshold
        ]
        
        # Sort by absolute correlation coefficient
        significant_correlations.sort(
            key=lambda x: abs(x['correlation_coefficient']), 
            reverse=True
        )
        
        return jsonify({
            'success': True,
            'data': {
                'total_correlations': len(results['correlation_results']),
                'significant_correlations': len(significant_correlations),
                'significance_threshold': significance_threshold,
                'correlations': significant_correlations
            },
            'message': f"Found {len(significant_correlations)} statistically significant correlations"
        })
    
    except Exception as e:
        logger.error(f"Error analyzing statistical significance: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': "Failed to analyze statistical significance"
        }), 500
