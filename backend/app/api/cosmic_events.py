from flask import jsonify, request
from app.api import api_bp
from app.core.cosmic_evolution_correlator import CosmicEvolutionCorrelator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Initialize the correlator
correlator = CosmicEvolutionCorrelator()

@api_bp.route('/cosmic-events', methods=['GET'])
def get_cosmic_events():
    """
    Endpoint to retrieve cosmic events
    Query parameters:
    - start_date: Start date in ISO format (YYYY-MM-DD)
    - end_date: End date in ISO format (YYYY-MM-DD)
    - event_type: Type of event (ftrt, geomagnetic, all)
    """
    try:
        # Get query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        event_type = request.args.get('event_type', 'all')
        
        # Set default dates if not provided
        if not start_date_str:
            start_date = datetime(2000, 1, 1)
        else:
            start_date = datetime.fromisoformat(start_date_str)
            
        if not end_date_str:
            end_date = datetime.now()
        else:
            end_date = datetime.fromisoformat(end_date_str)
        
        # Get cosmic events based on type
        if event_type == 'ftrt':
            events = correlator.ftrt_calculator.find_peaks(start_date, end_date)
        elif event_type == 'geomagnetic':
            events = correlator.paleomag_database.get_field_weaknesses(start_date, end_date)
        else:
            # Get all events
            ftrt_peaks = correlator.ftrt_calculator.find_peaks(start_date, end_date)
            geomag_minima = correlator.paleomag_database.get_field_weaknesses(start_date, end_date)
            events = ftrt_peaks + geomag_minima
        
        # Format events for JSON response
        formatted_events = []
        for event in events:
            formatted_events.append({
                'timestamp': event.timestamp.isoformat(),
                'type': event.event_type,
                'magnitude': event.magnitude,
                'duration_days': event.duration.days,
                'description': event.description
            })
        
        return jsonify({
            'success': True,
            'data': formatted_events,
            'count': len(formatted_events),
            'message': f"Retrieved {len(formatted_events)} cosmic events"
        })
    
    except Exception as e:
        logger.error(f"Error retrieving cosmic events: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': "Failed to retrieve cosmic events"
        }), 500

@api_bp.route('/cosmic-events/ftrt', methods=['GET'])
def get_ftrt_peaks():
    """
    Endpoint specifically for FTRT peaks
    """
    try:
        # Get query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        threshold = float(request.args.get('threshold', 1.5))
        
        # Set default dates if not provided
        if not start_date_str:
            start_date = datetime(2000, 1, 1)
        else:
            start_date = datetime.fromisoformat(start_date_str)
            
        if not end_date_str:
            end_date = datetime.now()
        else:
            end_date = datetime.fromisoformat(end_date_str)
        
        # Get FTRT peaks
        events = correlator.ftrt_calculator.find_peaks(start_date, end_date, threshold)
        
        # Format events for JSON response
        formatted_events = []
        for event in events:
            formatted_events.append({
                'timestamp': event.timestamp.isoformat(),
                'magnitude': event.magnitude,
                'duration_days': event.duration.days,
                'description': event.description
            })
        
        return jsonify({
            'success': True,
            'data': formatted_events,
            'count': len(formatted_events),
            'message': f"Retrieved {len(formatted_events)} FTRT peaks"
        })
    
    except Exception as e:
        logger.error(f"Error retrieving FTRT peaks: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': "Failed to retrieve FTRT peaks"
        }), 500

@api_bp.route('/cosmic-events/geomagnetic', methods=['GET'])
def get_geomagnetic_events():
    """
    Endpoint specifically for geomagnetic events
    """
    try:
        # Get query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        threshold = float(request.args.get('threshold', 10.0))
        
        # Set default dates if not provided
        if not start_date_str:
            start_date = datetime(2000, 1, 1)
        else:
            start_date = datetime.fromisoformat(start_date_str)
            
        if not end_date_str:
            end_date = datetime.now()
        else:
            end_date = datetime.fromisoformat(end_date_str)
        
        # Get geomagnetic events
        events = correlator.paleomag_database.get_field_weaknesses(start_date, end_date, threshold)
        
        # Format events for JSON response
        formatted_events = []
        for event in events:
            formatted_events.append({
                'timestamp': event.timestamp.isoformat(),
                'magnitude': event.magnitude,
                'duration_days': event.duration.days,
                'description': event.description
            })
        
        return jsonify({
            'success': True,
            'data': formatted_events,
            'count': len(formatted_events),
            'message': f"Retrieved {len(formatted_events)} geomagnetic events"
        })
    
    except Exception as e:
        logger.error(f"Error retrieving geomagnetic events: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': "Failed to retrieve geomagnetic events"
        }), 500
