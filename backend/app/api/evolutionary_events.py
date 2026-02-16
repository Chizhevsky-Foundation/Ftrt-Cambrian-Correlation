from flask import jsonify, request
from app.api import api_bp
from app.core.cosmic_evolution_correlator import CosmicEvolutionCorrelator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Initialize the correlator
correlator = CosmicEvolutionCorrelator()

@api_bp.route('/evolutionary-events', methods=['GET'])
def get_evolutionary_events():
    """
    Endpoint to retrieve evolutionary events
    Query parameters:
    - start_date: Start date in ISO format (YYYY-MM-DD)
    - end_date: End date in ISO format (YYYY-MM-DD)
    - event_type: Type of event (speciation, extinction, all)
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
        
        # Get evolutionary events
        events = correlator.fossil_parser.identify_radiations(start_date, end_date)
        
        # Filter by event type if specified
        if event_type != 'all':
            events = [event for event in events if event.event_type == event_type]
        
        # Format events for JSON response
        formatted_events = []
        for event in events:
            formatted_events.append({
                'timestamp': event.timestamp.isoformat(),
                'type': event.event_type,
                'magnitude': event.magnitude,
                'affected_taxa': event.affected_taxa,
                'description': event.description
            })
        
        return jsonify({
            'success': True,
            'data': formatted_events,
            'count': len(formatted_events),
            'message': f"Retrieved {len(formatted_events)} evolutionary events"
        })
    
    except Exception as e:
        logger.error(f"Error retrieving evolutionary events: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': "Failed to retrieve evolutionary events"
        }), 500

@api_bp.route('/evolutionary-events/speciation', methods=['GET'])
def get_speciation_events():
    """
    Endpoint specifically for speciation events
    """
    try:
        # Get query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # Set default dates if not provided
        if not start_date_str:
            start_date = datetime(2000, 1, 1)
        else:
            start_date = datetime.fromisoformat(start_date_str)
            
        if not end_date_str:
            end_date = datetime.now()
        else:
            end_date = datetime.fromisoformat(end_date_str)
        
        # Get evolutionary events
        events = correlator.fossil_parser.identify_radiations(start_date, end_date)
        
        # Filter for speciation events only
        speciation_events = [event for event in events if event.event_type == 'speciation']
        
        # Format events for JSON response
        formatted_events = []
        for event in speciation_events:
            formatted_events.append({
                'timestamp': event.timestamp.isoformat(),
                'magnitude': event.magnitude,
                'affected_taxa': event.affected_taxa,
                'description': event.description
            })
        
        return jsonify({
            'success': True,
            'data': formatted_events,
            'count': len(formatted_events),
            'message': f"Retrieved {len(formatted_events)} speciation events"
        })
    
    except Exception as e:
        logger.error(f"Error retrieving speciation events: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': "Failed to retrieve speciation events"
        }), 500

@api_bp.route('/evolutionary-events/extinction', methods=['GET'])
def get_extinction_events():
    """
    Endpoint specifically for extinction events
    """
    try:
        # Get query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # Set default dates if not provided
        if not start_date_str:
            start_date = datetime(2000, 1, 1)
        else:
            start_date = datetime.fromisoformat(start_date_str)
            
        if not end_date_str:
            end_date = datetime.now()
        else:
            end_date = datetime.fromisoformat(end_date_str)
        
        # Get evolutionary events
        events = correlator.fossil_parser.identify_radiations(start_date, end_date)
        
        # Filter for extinction events only
        extinction_events = [event for event in events if event.event_type == 'extinction']
        
        # Format events for JSON response
        formatted_events = []
        for event in extinction_events:
            formatted_events.append({
                'timestamp': event.timestamp.isoformat(),
                'magnitude': event.magnitude,
                'affected_taxa': event.affected_taxa,
                'description': event.description
            })
        
        return jsonify({
            'success': True,
            'data': formatted_events,
            'count': len(formatted_events),
            'message': f"Retrieved {len(formatted_events)} extinction events"
        })
    
    except Exception as e:
        logger.error(f"Error retrieving extinction events: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': "Failed to retrieve extinction events"
        }), 500
