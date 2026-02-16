import React, { useEffect, useRef, useState, useMemo } from 'react';
import * as d3 from 'd3';
import { Card, Row, Col, Form, Badge } from 'react-bootstrap';
import './CosmicOrrery.css';

const CosmicOrrery = ({ cosmicEvents, evolutionaryEvents, correlations }) => {
    const svgRef = useRef(null);
    const [selectedEvent, setSelectedEvent] = useState(null);
    const [hoveredEvent, setHoveredEvent] = useState(null);
    const [currentTime, setCurrentTime] = useState(0); // 0 to 100
    const [isPlaying, setIsPlaying] = useState(false);

    // Memoize the data processing to avoid recalculating on every render
    const processedData = useMemo(() => {
        if (!cosmicEvents || !evolutionaryEvents) return { cosmic: [], evolutionary: [] };

        // Process cosmic events
        const processedCosmic = cosmicEvents.map(event => ({
            ...event,
            date: new Date(event.timestamp),
            radius: 150, // Inner orbit radius
            size: Math.sqrt(event.magnitude) * 4, // Size based on magnitude
            color: event.type.includes('ftrt') ? '#FF6B6B' : '#FFA726', // Red for FTRT, Orange for Geomagnetic
        }));

        // Process evolutionary events
        const processedEvolutionary = evolutionaryEvents.map(event => ({
            ...event,
            date: new Date(event.timestamp),
            radius: 250, // Outer orbit radius
            size: Math.sqrt(event.magnitude) * 3,
            color: event.type === 'speciation' ? '#4ECDC4' : '#9575CD', // Teal for Speciation, Purple for Extinction
        }));

        return { cosmic: processedCosmic, evolutionary: processedEvolutionary };
    }, [cosmicEvents, evolutionaryEvents]);

    // D3 visualization effect
    useEffect(() => {
        if (!svgRef.current || processedData.cosmic.length === 0) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll('*').remove(); // Clear previous render

        const width = svgRef.current.clientWidth;
        const height = 600;
        const centerX = width / 2;
        const centerY = height / 2;

        const g = svg.append('g')
            .attr('transform', `translate(${centerX}, ${centerY})`);

        // Add zoom and pan
        const zoom = d3.zoom()
            .scaleExtent([0.5, 3])
            .on('zoom', (event) => {
                g.attr('transform', `translate(${centerX}, ${centerY}) scale(${event.transform.k})`);
            });
        svg.call(zoom);

        // --- Draw Static Elements ---
        
        // The Sun (Cambrian Explosion)
        g.append('circle')
            .attr('r', 30)
            .attr('fill', 'url(#sunGradient)')
            .attr('stroke', '#FFD54F')
            .attr('stroke-width', 3);
        g.append('text')
            .text('CÁMBRICO')
            .attr('text-anchor', 'middle')
            .attr('dy', '0.35em')
            .attr('fill', '#3E2723')
            .style('font-weight', 'bold');

        // Define gradients
        const defs = svg.append('defs');
        const sunGradient = defs.append('radialGradient').attr('id', 'sunGradient');
        sunGradient.append('stop').attr('offset', '0%').attr('stop-color', '#FFF59D');
        sunGradient.append('stop').attr('offset', '100%').attr('stop-color', '#FFB300');

        // --- Draw Dynamic Elements (using a general update pattern) ---
        
        const timeExtent = d3.extent([...processedData.cosmic, ...processedData.evolutionary], d => d.date);
        const timeScale = d3.scaleTime().domain(timeExtent).range([0, 2 * Math.PI]);

        function updatePositions(progress) {
            // Update Cosmic Events (Planets)
            const cosmicPlanets = g.selectAll('.cosmic-planet')
                .data(processedData.cosmic, d => d.timestamp);

            cosmicPlanets.enter()
                .append('g')
                .attr('class', 'cosmic-planet')
                .append('circle')
                .merge(cosmicPlanets.select('circle'))
                .transition()
                .duration(50)
                .attr('r', d => d.size)
                .attr('fill', d => d.color)
                .attr('stroke', '#fff')
                .attr('stroke-width', 2)
                .attr('cx', d => Math.cos(timeScale(d.date) + progress) * d.radius)
                .attr('cy', d => Math.sin(timeScale(d.date) + progress) * d.radius)
                .attr('opacity', d => selectedEvent && selectedEvent.timestamp !== d.timestamp ? 0.3 : 0.9);

            // Update Evolutionary Events (Moons)
            const evolutionaryMoons = g.selectAll('.evolutionary-moon')
                .data(processedData.evolutionary, d => d.timestamp);

            evolutionaryMoons.enter()
                .append('g')
                .attr('class', 'evolutionary-moon')
                .append('circle')
                .merge(evolutionaryMoons.select('circle'))
                .transition()
                .duration(50)
                .attr('r', d => d.size)
                .attr('fill', d => d.color)
                .attr('stroke', '#fff')
                .attr('stroke-width', 1.5)
                .attr('cx', d => Math.cos(timeScale(d.date) + progress * 1.5) * d.radius) // Different speed
                .attr('cy', d => Math.sin(timeScale(d.date) + progress * 1.5) * d.radius)
                .attr('opacity', d => selectedEvent && selectedEvent.timestamp !== d.timestamp ? 0.3 : 0.9);
        }

        // Initial draw
        updatePositions(currentTime / 100 * Math.PI * 2);

        // --- Add Interactivity ---
        const allEvents = g.selectAll('.cosmic-planet, .evolutionary-moon');

        function handleMouseEnter(event, d) {
            setHoveredEvent(d);
            d3.select(this).select('circle').attr('r', d => d.size * 1.5);
        }

        function handleMouseLeave(event, d) {
            setHoveredEvent(null);
            d3.select(this).select('circle').transition().attr('r', d => d.size);
        }
        
        function handleClick(event, d) {
            setSelectedEvent(d === selectedEvent ? null : d);
        }

        // Re-bind events after data join
        g.selectAll('.cosmic-planet')
            .on('mouseenter', handleMouseEnter)
            .on('mouseleave', handleMouseLeave)
            .on('click', handleClick);
        
        g.selectAll('.evolutionary-moon')
            .on('mouseenter', handleMouseEnter)
            .on('mouseleave', handleMouseLeave)
            .on('click', handleClick);
        
        // Animation loop
        let animationFrame;
        if (isPlaying) {
            const animate = () => {
                setCurrentTime(prev => {
                    const next = (prev + 0.2) % 100;
                    updatePositions(next / 100 * Math.PI * 2);
                    return next;
                });
                animationFrame = requestAnimationFrame(animate);
            };
            animate();
        }
        
        return () => {
            if (animationFrame) {
                cancelAnimationFrame(animationFrame);
            }
        };

    }, [processedData, currentTime, isPlaying, selectedEvent]); // Re-run if data or time changes

    // --- Draw correlation lines when an event is selected ---
    useEffect(() => {
        const svg = d3.select(svgRef.current);
        const g = svg.select('g');
        
        // Remove old lines
        g.selectAll('.correlation-line').remove();

        if (!selectedEvent || !correlations) return;

        // This is a simplified logic. In a real scenario, you'd find the best matches from the correlation data.
        const relatedEvents = selectedEvent.type.includes('ftrt') || selectedEvent.type.includes('geomagnetic')
            ? processedData.evolutionary
            : processedData.cosmic;

        const lines = g.selectAll('.correlation-line')
            .data(relatedEvents.slice(0, 5)); // Draw lines to the first 5 related events

        lines.enter()
            .append('line')
            .attr('class', 'correlation-line')
            .merge(lines)
            .attr('x1', 0)
            .attr('y1', 0)
            .attr('x2', d => Math.cos(d.date / 100000000 * Math.PI * 2) * d.radius) // Simplified position calc
            .attr('y2', d => Math.sin(d.date / 100000000 * Math.PI * 2) * d.radius)
            .attr('stroke', '#FFF')
            .attr('stroke-width', 1)
            .attr('stroke-dasharray', '5,5')
            .attr('opacity', 0.5);

    }, [selectedEvent, processedData, correlations]);


    return (
        <Card className="orrery-card">
            <Card.Header as="h5">Orrery Cósmico-Evolutivo</Card.Header>
            <Card.Body>
                <svg ref={svgRef} width="100%" height="600"></svg>
                
                <Row className="mt-4">
                    <Col md={8}>
                        <Form.Group>
                            <Form.Label>Viajar en el Tiempo Cámbrico</Form.Label>
                            <Form.Range 
                                min="0" 
                                max="100" 
                                value={currentTime} 
                                onChange={(e) => setCurrentTime(Number(e.target.value))}
                            />
                        </Form.Group>
                    </Col>
                    <Col md={4} className="text-end">
                        <button className={`btn ${isPlaying ? 'btn-danger' : 'btn-success'}`} onClick={() => setIsPlaying(!isPlaying)}>
                            {isPlaying ? 'Pausar' : 'Reproducir'} Animación
                        </button>
                    </Col>
                </Row>
                
                {hoveredEvent && (
                    <div className="orrery-tooltip">
                        <strong>{hoveredEvent.type.replace('_', ' ').toUpperCase()}</strong>
                        <br />
                        <small>{new Date(hoveredEvent.timestamp).toLocaleDateString()}</small>
                        <br />
                        Magnitud: {hoveredEvent.magnitude.toFixed(2)}
                    </div>
                )}

                {selectedEvent && (
                    <Row className="mt-3">
                        <Col>
                            <h5>Evento Seleccionado</h5>
                            <p>
                                <Badge bg={selectedEvent.type.includes('ftrt') ? 'danger' : 'info'}>
                                    {selectedEvent.type.replace('_', ' ').toUpperCase()}
                                </Badge>
                                <br />
                                <strong>Fecha:</strong> {new Date(selectedEvent.timestamp).toLocaleDateString()}
                                <br />
                                <strong>Magnitud:</strong> {selectedEvent.magnitude.toFixed(2)}
                                <br />
                                <strong>Descripción:</strong> {selectedEvent.description}
                            </p>
                        </Col>
                    </Row>
                )}
            </Card.Body>
        </Card>
    );
};

export default CosmicOrrery;
