import React, { useState } from 'react';
import styled from 'styled-components';
import { FaChartLine } from 'react-icons/fa';
import { ForecastForm, ForecastResults } from '../components/SolarForecast';
import apiClient from '../api/apiClient';

const ForecastContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const Title = styled.h1`
  font-size: 2rem;
  margin-bottom: 1.5rem;
  color: #343a40;
  display: flex;
  align-items: center;
  
  svg {
    margin-right: 0.75rem;
    color: #ffc107;
  }
`;

const ErrorMessage = styled.div`
  background-color: #f8d7da;
  color: #721c24;
  padding: 1rem;
  border-radius: 0.25rem;
  margin-bottom: 1.5rem;
`;

const SolarForecastPage: React.FC = () => {
  const [forecast, setForecast] = useState<any>(null);
  const [costSavings, setCostSavings] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const handleSubmit = async (formData: {
    latitude: number;
    longitude: number;
    locationId: string;
    systemCapacityKw: number;
    electricityRate: number;
    feedInTariff: number;
  }) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Get solar forecast
      const forecastResponse = await apiClient.getSolarForecast({
        latitude: formData.latitude,
        longitude: formData.longitude,
        location_id: formData.locationId,
        system_capacity_kw: formData.systemCapacityKw,
      });
      
      setForecast(forecastResponse.forecast);
      
      // Get cost savings
      const costSavingsResponse = await apiClient.getCostSavings({
        latitude: formData.latitude,
        longitude: formData.longitude,
        location_id: formData.locationId,
        system_capacity_kw: formData.systemCapacityKw,
        electricity_rate: formData.electricityRate,
        feed_in_tariff: formData.feedInTariff,
      });
      
      setCostSavings(costSavingsResponse.cost_savings);
    } catch (err) {
      console.error('Error fetching forecast:', err);
      setError('Error generating forecast. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <ForecastContainer>
      <Title>
        <FaChartLine />
        Solar Energy Forecast
      </Title>
      
      {error && <ErrorMessage>{error}</ErrorMessage>}
      
      <ForecastForm onSubmit={handleSubmit} isLoading={isLoading} />
      
      {forecast && costSavings && (
        <ForecastResults forecast={forecast} costSavings={costSavings} />
      )}
    </ForecastContainer>
  );
};

export default SolarForecastPage;
