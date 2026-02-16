import React, { useState, useMemo } from 'react';
import { Card, Table, Form, Button, Row, Col, Spinner, Alert } from 'react-bootstrap';

const DataExplorer = ({ correlations, cosmicEvents, evolutionaryEvents }) => {
  const [activeDataset, setActiveDataset] = useState('cosmic');
  const [filter, setFilter] = useState('');
  const [sortBy, setSortBy] = useState('timestamp');
  const [sortOrder, setSortOrder] = useState('asc');

  const data = useMemo(() => {
    let dataset = activeDataset === 'cosmic' ? cosmicEvents : evolutionaryEvents;
    
    // Filter data
    if (filter) {
      dataset = dataset.filter(event => 
        event.type.toLowerCase().includes(filter.toLowerCase()) ||
        event.description.toLowerCase().includes(filter.toLowerCase())
      );
    }

    // Sort data
    dataset.sort((a, b) => {
      let valA = a[sortBy];
      let valB = b[sortBy];
      
      if (sortBy === 'timestamp') {
        valA = new Date(valA);
        valB = new Date(valB);
      }

      if (sortOrder === 'asc') {
        return valA > valB ? 1 : -1;
      } else {
        return valA < valB ? 1 : -1;
      }
    });

    return dataset;
  }, [activeDataset, cosmicEvents, evolutionaryEvents, filter, sortBy, sortOrder]);

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  const renderCosmicTable = () => (
    <Table striped bordered hover responsive>
      <thead>
        <tr>
          <th onClick={() => handleSort('timestamp')} style={{ cursor: 'pointer' }}>
            Timestamp {sortBy === 'timestamp' && (sortOrder === 'asc' ? '▲' : '▼')}
          </th>
          <th onClick={() => handleSort('type')} style={{ cursor: 'pointer' }}>
            Type {sortBy === 'type' && (sortOrder === 'asc' ? '▲' : '▼')}
          </th>
          <th onClick={() => handleSort('magnitude')} style={{ cursor: 'pointer' }}>
            Magnitude {sortBy === 'magnitude' && (sortOrder === 'asc' ? '▲' : '▼')}
          </th>
          <th>Description</th>
        </tr>
      </thead>
      <tbody>
        {data.map((event, index) => (
          <tr key={index}>
            <td>{new Date(event.timestamp).toLocaleString()}</td>
            <td>{event.type}</td>
            <td>{event.magnitude.toFixed(2)}</td>
            <td>{event.description}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  );

  const renderEvolutionaryTable = () => (
    <Table striped bordered hover responsive>
      <thead>
        <tr>
          <th onClick={() => handleSort('timestamp')} style={{ cursor: 'pointer' }}>
            Timestamp {sortBy === 'timestamp' && (sortOrder === 'asc' ? '▲' : '▼')}
          </th>
          <th onClick={() => handleSort('type')} style={{ cursor: 'pointer' }}>
            Type {sortBy === 'type' && (sortOrder === 'asc' ? '▲' : '▼')}
          </th>
          <th onClick={() => handleSort('magnitude')} style={{ cursor: 'pointer' }}>
            Magnitude {sortBy === 'magnitude' && (sortOrder === 'asc' ? '▲' : '▼')}
          </th>
          <th>Affected Taxa</th>
          <th>Description</th>
        </tr>
      </thead>
      <tbody>
        {data.map((event, index) => (
          <tr key={index}>
            <td>{new Date(event.timestamp).toLocaleString()}</td>
            <td>{event.type}</td>
            <td>{event.magnitude.toFixed(2)}</td>
            <td>{event.affected_taxa.join(', ')}</td>
            <td>{event.description}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  );

  return (
    <Card>
      <Card.Header as="h5">Data Explorer</Card.Header>
      <Card.Body>
        <Row className="mb-3">
          <Col md={6}>
            <Form.Group>
              <Form.Label>Select Dataset</Form.Label>
              <Form.Control as="select" value={activeDataset} onChange={(e) => setActiveDataset(e.target.value)}>
                <option value="cosmic">Cosmic Events</option>
                <option value="evolutionary">Evolutionary Events</option>
              </Form.Control>
            </Form.Group>
          </Col>
          <Col md={6}>
            <Form.Group>
              <Form.Label>Filter</Form.Label>
              <Form.Control 
                type="text" 
                placeholder="Filter by type or description..." 
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              />
            </Form.Group>
          </Col>
        </Row>
        
        {data.length > 0 ? (
          activeDataset === 'cosmic' ? renderCosmicTable() : renderEvolutionaryTable()
        ) : (
          <Alert variant="info">No data to display. Try adjusting the filters or date range.</Alert>
        )}
      </Card.Body>
    </Card>
  );
};

export default DataExplorer;
