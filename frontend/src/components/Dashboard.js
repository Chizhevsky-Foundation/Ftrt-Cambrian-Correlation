// frontend/src/components/Dashboard.js
import CosmicOrrery from './CosmicOrrery';
import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Alert, Spinner, Button } from 'react-bootstrap';
import CorrelationChart from './CorrelationChart';
import Timeline from './Timeline';
import DataExplorer from './DataExplorer';
import { getCorrelations, getCosmicEvents, getEvolutionaryEvents } from '../services/api';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [correlations, setCorrelations] = useState(null);
  const [cosmicEvents, setCosmicEvents] = useState([]);
  const [evolutionaryEvents, setEvolutionaryEvents] = useState([]);
  const [startDate, setStartDate] = useState('2000-01-01');
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);
  const [activeTab, setActiveTab] = useState('correlations');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Obtener correlaciones
        const correlationsData = await getCorrelations(startDate, endDate);
        setCorrelations(correlationsData.data);
        
        // Obtener eventos cósmicos
        const cosmicData = await getCosmicEvents(startDate, endDate);
        setCosmicEvents(cosmicData.data);
        
        // Obtener eventos evolutivos
        const evolutionaryData = await getEvolutionaryEvents(startDate, endDate);
        setEvolutionaryEvents(evolutionaryData.data);
        
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate]);

  const handleRefresh = () => {
    setLoading(true);
    // Forzar recarga de datos
    const fetchData = async () => {
      try {
        // Obtener correlaciones
        const correlationsData = await getCorrelations(startDate, endDate);
        setCorrelations(correlationsData.data);
        
        // Obtener eventos cósmicos
        const cosmicData = await getCosmicEvents(startDate, endDate);
        setCosmicEvents(cosmicData.data);
        
        // Obtener eventos evolutivos
        const evolutionaryData = await getEvolutionaryEvents(startDate, endDate);
        setEvolutionaryEvents(evolutionaryData.data);
        
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchData();
  };

  const renderContent = () => {
    if (loading) {
      return (
        <div className="text-center my-5">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p className="mt-2">Analyzing cosmic-evolutionary correlations...</p>
        </div>
      );
    }

    if (error) {
      return (
        <Alert variant="danger">
          <Alert.Heading>Error</Alert.Heading>
          <p>{error}</p>
        </Alert>
      );
    }

   switch (activeTab) {
     case 'correlations':
       return <CorrelationChart ... />;
     case 'timeline':
       return <Timeline ... />;
     case 'explorer':
       return <DataExplorer ... />;
     case 'orrery': // <-- NUEVA PESTAÑA
       return <CosmicOrrery 
         cosmicEvents={cosmicEvents}
         evolutionaryEvents={evolutionaryEvents}
         correlations={correlations}
       />;
     default:
       return null;
   }
      
      case 'timeline':
        return (
          <Timeline 
            cosmicEvents={cosmicEvents}
            evolutionaryEvents={evolutionaryEvents}
          />
        );
      case 'explorer':
        return (
          <DataExplorer 
            correlations={correlations}
            cosmicEvents={cosmicEvents}
            evolutionaryEvents={evolutionaryEvents}
          />
        );
      default:
        return null;
    }
  };

  return (
    <Container fluid className="p-4">
      <Row className="mb-4">
        <Col>
          <h1 className="text-center">🌌 FTRT-Cambrian Correlation Project</h1>
          <p className="text-center text-muted">Cosmic Architecture Revealed</p>
        </Col>
      </Row>
      
      <Row className="mb-4">
        <Col md={4}>
          <Card>
            <Card.Body>
              <Card.Title>Analysis Parameters</Card.Title>
              <div className="mb-3">
                <label htmlFor="startDate" className="form-label">Start Date</label>
                <input 
                  type="date" 
                  className="form-control" 
                  id="startDate"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>
              <div className="mb-3">
                <label htmlFor="endDate" className="form-label">End Date</label>
                <input 
                  type="date" 
                  className="form-control" 
                  id="endDate"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                />
              </div>
              <Button variant="primary" onClick={handleRefresh}>
                Refresh Analysis
              </Button>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={8}>
          {correlations && correlations.best_correlation && (
            <Card className="h-100">
              <Card.Body>
                <Card.Title>Key Findings</Card.Title>
                <p>
                  <strong>Best Correlation:</strong> {correlations.best_correlation.correlation_coefficient.toFixed(4)}
                  <br />
                  <strong>P-value:</strong> {correlations.best_correlation.p_value.toFixed(6)}
                  <br />
                  <strong>Time Lag:</strong> {correlations.best_correlation.time_lag_days} days
                  <br />
                  <strong>Significant:</strong> {correlations.best_correlation.significant ? 'Yes' : 'No'}
                </p>
                <p className="text-muted">
                  {correlations.best_correlation.significant 
                    ? "The analysis reveals a statistically significant correlation between cosmic events and evolutionary patterns."
                    : "No statistically significant correlation was found in the selected time period."}
                </p>
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>
      
      <Row className="mb-4">
        <Col>
          <div className="btn-group" role="group">
            <button 
              type="button" 
              className={`btn ${activeTab === 'correlations' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setActiveTab('correlations')}
            >
              Correlations
            </button>
            <button 
              type="button" 
              className={`btn ${activeTab === 'timeline' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setActiveTab('timeline')}
            >
            <button 
              type="button" 
              className={`btn ${activeTab === 'orrery' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setActiveTab('orrery')}
            >
              Orrery Cósmico
            </button>
              Timeline
            </button>
            <button 
              type="button" 
              className={`btn ${activeTab === 'explorer' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setActiveTab('explorer')}
            >
              Data Explorer
            </button>
          </div>
        </Col>
      </Row>
      
      <Row>
        <Col>
          {renderContent()}
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;
