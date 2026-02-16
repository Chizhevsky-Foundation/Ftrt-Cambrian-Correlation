// frontend/src/components/CorrelationChart.js
import React, { useEffect, useRef } from 'react';
import { Card } from 'react-bootstrap';
import * as d3 from 'd3';

const CorrelationChart = ({ correlations, cosmicEvents, evolutionaryEvents }) => {
  const chartRef = useRef(null);
  
  useEffect(() => {
    if (!correlations || !chartRef.current) return;
    
    // Limpiar el gráfico anterior
    d3.select(chartRef.current).selectAll('*').remove();
    
    // Dimensiones
    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const width = chartRef.current.clientWidth - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;
    
    // Crear SVG
    const svg = d3.select(chartRef.current)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Escalas
    const xScale = d3.scaleLinear()
      .domain(d3.extent(correlations.correlation_results, d => d.time_lag_days))
      .range([0, width]);
    
    const yScale = d3.scaleLinear()
      .domain([-1, 1])
      .range([height, 0]);
    
    // Línea de correlación
    const line = d3.line()
      .x(d => xScale(d.time_lag_days))
      .y(d => yScale(d.correlation_coefficient))
      .curve(d3.curveMonotoneX);
    
    // Ejes
    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale).ticks(10))
      .append('text')
      .attr('x', width / 2)
      .attr('y', 35)
      .attr('fill', 'black')
      .style('text-anchor', 'middle')
      .text('Time Lag (days)');
    
    svg.append('g')
      .call(d3.axisLeft(yScale))
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', -35)
      .attr('x', -height / 2)
      .attr('fill', 'black')
      .style('text-anchor', 'middle')
      .text('Correlation Coefficient');
    
    // Línea horizontal en y=0
    svg.append('line')
      .attr('x1', 0)
      .attr('y1', yScale(0))
      .attr('x2', width)
      .attr('y2', yScale(0))
      .attr('stroke', '#ccc')
      .attr('stroke-dasharray', '5,5');
    
    // Área de significancia (p < 0.05)
    const significantData = correlations.correlation_results.filter(d => d.significant);
    
    if (significantData.length > 0) {
      const area = d3.area()
        .x(d => xScale(d.time_lag_days))
        .y0(d => yScale(Math.min(0, d.correlation_coefficient)))
        .y1(d => yScale(Math.max(0, d.correlation_coefficient)));
      
      svg.append('path')
        .datum(significantData)
        .attr('fill', 'rgba(75, 192, 192, 0.3)')
        .attr('d', area);
    }
    
    // Línea de correlación
    svg.append('path')
      .datum(correlations.correlation_results)
      .attr('fill', 'none')
      .attr('stroke', 'steelblue')
      .attr('stroke-width', 2)
      .attr('d', line);
    
    // Puntos de datos
    svg.selectAll('.dot')
      .data(correlations.correlation_results)
      .enter().append('circle')
      .attr('class', 'dot')
      .attr('cx', d => xScale(d.time_lag_days))
      .attr('cy', d => yScale(d.correlation_coefficient))
      .attr('r', d => d.significant ? 5 : 3)
      .attr('fill', d => d.significant ? 'red' : 'steelblue')
      .on('mouseover', function(event, d) {
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
          <strong>Time Lag:</strong> ${d.time_lag_days} days<br>
          <strong>Correlation:</strong> ${d.correlation_coefficient.toFixed(4)}<br>
          <strong>P-value:</strong> ${d.p_value.toFixed(6)}<br>
          <strong>Significant:</strong> ${d.significant ? 'Yes' : 'No'}
        `)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', function() {
        d3.selectAll('.tooltip').remove();
      });
    
  }, [correlations]);
  
  return (
    <Card>
      <Card.Header as="h5">Cosmic-Evolutionary Correlation Analysis</Card.Header>
      <Card.Body>
        <div ref={chartRef} style={{ width: '100%' }}></div>
        <p className="text-muted mt-3">
          This chart shows the correlation between cosmic events and evolutionary patterns 
          at different time lags. Red dots indicate statistically significant correlations (p &lt; 0.05).
        </p>
      </Card.Body>
    </Card>
  );
};

export default CorrelationChart;
