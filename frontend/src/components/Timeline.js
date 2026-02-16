// frontend/src/components/Timeline.js
import React, { useEffect, useRef } from 'react';
import { Card } from 'react-bootstrap';
import * as d3 from 'd3';

const Timeline = ({ cosmicEvents, evolutionaryEvents }) => {
  const timelineRef = useRef(null);
  
  useEffect(() => {
    if (!cosmicEvents || !evolutionaryEvents || !timelineRef.current) return;
    
    // Limpiar la línea de tiempo anterior
    d3.select(timelineRef.current).selectAll('*').remove();
    
    // Preparar datos
    const allEvents = [
      ...cosmicEvents.map(e => ({...e, category: 'cosmic'})),
      ...evolutionaryEvents.map(e => ({...e, category: 'evolutionary'}))
    ];
    
    // Ordenar por fecha
    allEvents.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    
    // Dimensiones
    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const width = timelineRef.current.clientWidth - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;
    
    // Crear SVG
    const svg = d3.select(timelineRef.current)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Escala de tiempo
    const xScale = d3.scaleTime()
      .domain(d3.extent(allEvents, d => new Date(d.timestamp)))
      .range([0, width]);
    
    // Eje X
    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale).ticks(10))
      .append('text')
      .attr('x', width / 2)
      .attr('y', 35)
      .attr('fill', 'black')
      .style('text-anchor', 'middle')
      .text('Time');
    
    // Línea de tiempo principal
    svg.append('line')
      .attr('x1', 0)
      .attr('y1', height / 2)
      .attr('x2', width)
      .attr('y2', height / 2)
      .attr('stroke', '#ccc')
      .attr('stroke-width', 2);
    
    // Añadir eventos
    const cosmicEventsGroup = svg.append('g').attr('class', 'cosmic-events');
    const evolutionaryEventsGroup = svg.append('g').attr('class', 'evolutionary-events');
    
    // Eventos cósmicos (arriba de la línea)
    cosmicEventsGroup.selectAll('.cosmic-event')
      .data(cosmicEvents)
      .enter().append('circle')
      .attr('class', 'cosmic-event')
      .attr('cx', d => xScale(new Date(d.timestamp)))
      .attr('cy', height / 2)
      .attr('r', 8)
      .attr('fill', '#FF6B6B')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .on('mouseover', function(event, d) {
        d3.select(this).attr('r', 10);
        
        const tooltip = d3.select('body').append('div')
          .attr('class', 'tooltip')
          .style('opacity', 0)
          .style('position', 'absolute')
          .style('background-color', 'white')
          .style('border', '1px solid #ddd')
          .style('border-radius', '5px')
          .style('padding', '10px')
          .style('pointer-events', 'none');
        
        tooltip.transition()
          .duration(200)
          .style('opacity', .9);
        
        tooltip.html(`
          <strong>Date:</strong> ${new Date(d.timestamp).toLocaleDateString()}<br>
          <strong>Type:</strong> ${d.type}<br>
          <strong>Magnitude:</strong> ${d.magnitude.toFixed(2)}<br>
          <strong>Description:</strong> ${d.description}
        `)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', function() {
        d3.select(this).attr('r', 8);
        d3.selectAll('.tooltip').remove();
      })
      .on('click', function(event, d) {
        // Animación para mostrar detalles
        const y = height / 2 - 30;
        
        d3.select(this)
          .transition()
          .duration(300)
          .attr('cy', y);
        
        // Añadir etiqueta
        svg.append('text')
          .attr('class', 'event-label')
          .attr('x', xScale(new Date(d.timestamp)))
          .attr('y', y - 10)
          .attr('text-anchor', 'middle')
          .attr('fill', '#FF6B6B')
          .text(d.type);
        
        // Volver a la posición original después de un tiempo
        setTimeout(() => {
          d3.select(this)
            .transition()
            .duration(300)
            .attr('cy', height / 2);
          
          svg.selectAll('.event-label').remove();
        }, 2000);
      });
    
    // Eventos evolutivos (abajo de la línea)
    evolutionaryEventsGroup.selectAll('.evolutionary-event')
      .data(evolutionaryEvents)
      .enter().append('circle')
      .attr('class', 'evolutionary-event')
      .attr('cx', d => xScale(new Date(d.timestamp)))
      .attr('cy', height / 2)
      .attr('r', 8)
      .attr('fill', '#4ECDC4')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .on('mouseover', function(event, d) {
        d3.select(this).attr('r', 10);
        
        const tooltip = d3.select('body').append('div')
          .attr('class', 'tooltip')
          .style('opacity', 0)
          .style('position', 'absolute')
          .style('background-color', 'white')
          .style('border', '1px solid #ddd')
          .style('border-radius', '5px')
          .style('padding', '10px')
          .style('pointer-events', 'none');
        
        tooltip.transition()
          .duration(200)
          .style('opacity', .9);
        
        tooltip.html(`
          <strong>Date:</strong> ${new Date(d.timestamp).toLocaleDateString()}<br>
          <strong>Type:</strong> ${d.type}<br>
          <strong>Magnitude:</strong> ${d.magnitude.toFixed(2)}<br>
          <strong>Affected Taxa:</strong> ${d.affected_taxa.join(', ')}<br>
          <strong>Description:</strong> ${d.description}
        `)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', function() {
        d3.select(this).attr('r', 8);
        d3.selectAll('.tooltip').remove();
      })
      .on('click', function(event, d) {
        // Animación para mostrar detalles
        const y = height / 2 + 30;
        
        d3.select(this)
          .transition()
          .duration(300)
          .attr('cy', y);
        
        // Añadir etiqueta
        svg.append('text')
          .attr('class', 'event-label')
          .attr('x', xScale(new Date(d.timestamp)))
          .attr('y', y + 20)
          .attr('text-anchor', 'middle')
          .attr('fill', '#4ECDC4')
          .text(d.type);
        
        // Volver a la posición original después de un tiempo
        setTimeout(() => {
          d3.select(this)
            .transition()
            .duration(300)
            .attr('cy', height / 2);
          
          svg.selectAll('.event-label').remove();
        }, 2000);
      });
    
    // Leyenda
    const legend = svg.append('g')
      .attr('transform', `translate(${width - 150}, 20)`);
    
    legend.append('circle')
      .attr('cx', 0)
      .attr('cy', 0)
      .attr('r', 6)
      .attr('fill', '#FF6B6B');
    
    legend.append('text')
      .attr('x', 15)
      .attr('y', 5)
      .text('Cosmic Events');
    
    legend.append('circle')
      .attr('cx', 0)
      .attr('cy', 20)
      .attr('r', 6)
      .attr('fill', '#4ECDC4');
    
    legend.append('text')
      .attr('x', 15)
      .attr('y', 25)
      .text('Evolutionary Events');
    
  }, [cosmicEvents, evolutionaryEvents]);
  
  return (
    <Card>
      <Card.Header as="h5">Cosmic-Evolutionary Timeline</Card.Header>
      <Card.Body>
        <div ref={timelineRef} style={{ width: '100%' }}></div>
        <p className="text-muted mt-3">
          This timeline displays cosmic events (red) and evolutionary events (teal) over time. 
          Click on events to see more details.
        </p>
      </Card.Body>
    </Card>
  );
};

export default Timeline;
