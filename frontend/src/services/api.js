// frontend/src/services/api.js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const getCorrelations = async (startDate, endDate) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/correlations?start_date=${startDate}&end_date=${endDate}`);
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.message || 'Failed to fetch correlations');
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching correlations:', error);
    throw error;
  }
};

export const getCosmicEvents = async (startDate, endDate, type) => {
  try {
    let url = `${API_BASE_URL}/api/cosmic-events?start_date=${startDate}&end_date=${endDate}`;
    if (type) {
      url += `&type=${type}`;
    }
    
    const response = await fetch(url);
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.message || 'Failed to fetch cosmic events');
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching cosmic events:', error);
    throw error;
  }
};

export const getEvolutionaryEvents = async (startDate, endDate, type) => {
  try {
    let url = `${API_BASE_URL}/api/evolutionary-events?start_date=${startDate}&end_date=${endDate}`;
    if (type) {
      url += `&type=${type}`;
    }
    
    const response = await fetch(url);
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.message || 'Failed to fetch evolutionary events');
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching evolutionary events:', error);
    throw error;
  }
};
