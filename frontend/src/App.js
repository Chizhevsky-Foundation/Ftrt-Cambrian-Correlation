// frontend/src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import Dashboard from './components/Dashboard';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  return (
    <Router>
      <Container fluid className="p-0">
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </Container>
    </Router>
  );
}

export default App;
