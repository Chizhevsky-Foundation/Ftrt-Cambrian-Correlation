# backend/app/api/correlations.py
from flask import Blueprint, jsonify, request
from datetime import datetime
from app.core.cosmic_evolution_correlator import CosmicEvolutionCorrelator
import logging

logger = logging.getLogger(__name__)

correlations_bp = Blueprint('correlations', __name__)
correlator = CosmicEvolutionCorrelator()

@correlations_bp.route('/api/correlations', methods=['GET'])
def get_correlations():
    """
    Endpoint para obtener correlaciones entre eventos cósmicos y evolutivos
    """
    try:
        # Obtener parámetros de la solicitud
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # Valores predeterminados si no se proporcionan
        if not start_date_str:
            start_date = datetime(2000, 1, 1)
        else:
            start_date = datetime.fromisoformat(start_date_str)
            
        if not end_date_str:
            end_date = datetime.now()
        else:
            end_date = datetime.fromisoformat(end_date_str)
        
        # Realizar análisis de correlación
        results = correlator.correlate_events(start_date, end_date)
        
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

@correlations_bp.route('/api/cosmic-events', methods=['GET'])
def get_cosmic_events():
    """
    Endpoint para obtener eventos cósmicos
    """
    try:
        # Obtener parámetros de la solicitud
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        event_type = request.args.get('type')
        
        # Valores predeterminados si no se proporcionan
        if not start_date_str:
            start_date = datetime(2000, 1, 1)
        else:
            start_date = datetime.fromisoformat(start_date_str)
            
        if not end_date_str:
            end_date = datetime.now()
        else:
            end_date = datetime.fromisoformat(end_date_str)
        
        # Obtener eventos cósmicos
        if event_type == 'ftrt':
            events = correlator.ftrt_calculator.find_peaks(start_date, end_date)
        elif event_type == 'geomagnetic':
            events = correlator.paleomag_database.get_field_weaknesses(start_date, end_date)
        else:
            # Obtener todos los eventos
            ftrt_peaks = correlator.ftrt_calculator.find_peaks(start_date, end_date)
            geomag_minima = correlator.paleomag_database.get_field_weaknesses(start_date, end_date)
            events = ftrt_peaks + geomag_minima
        
        # Formatear resultados
        formatted_events = [
            {
                'timestamp': event.timestamp.isoformat(),
                'type': event.event_type,
                'magnitude': event.magnitude,
                'duration_days': event.duration.days,
                'description': event.description
            }
            for event in events
        ]
        
        return jsonify({
            'success': True,
            'data': formatted_events,
            'message': f"Retrieved {len(formatted_events)} cosmic events"
        })
    
    except Exception as e:
        logger.error(f"Error retrieving cosmic events: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': "Failed to retrieve cosmic events"
        }), 500

@correlations_bp.route('/api/evolutionary-events', methods=['GET'])
def get_evolutionary_events():
    """
    Endpoint para obtener eventos evolutivos
    """
    try:
        # Obtener parámetros de la solicitud
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        event_type = request.args.get('type')
        
        # Valores predeterminados si no se proporcionan
        if not start_date_str:
            start_date = datetime(2000, 1, 1)
        else:
            start_date = datetime.fromisoformat(start_date_str)
            
        if not end_date_str:
            end_date = datetime.now()
        else:
            end_date = datetime.fromisoformat(end_date_str)
        
        # Obtener eventos evolutivos
        events = correlator.fossil_parser.identify_radiations(start_date, end_date)
        
        # Filtrar por tipo si se especifica
        if event_type:
            events = [event for event in events if event.event_type == event_type]
        
        # Formatear resultados
        formatted_events = [
            {
                'timestamp': event.timestamp.isoformat(),
                'type': event.event_type,
                'magnitude': event.magnitude,
                'affected_taxa': event.affected_taxa,
                'description': event.description
            }
            for event in events
        ]
        
        return jsonify({
            'success': True,
            'data': formatted_events,
            'message': f"Retrieved {len(formatted_events)} evolutionary events"
        })
    
    except Exception as e:
        logger.error(f"Error retrieving evolutionary events: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': "Failed to retrieve evolutionary events"
        }), 500
