import React, { useState } from 'react';
import styled from 'styled-components';
import { FaSearch } from 'react-icons/fa';

interface ForecastFormProps {
  onSubmit: (formData: {
    latitude: number;
    longitude: number;
    locationId: string;
    systemCapacityKw: number;
    electricityRate: number;
    feedInTariff: number;
  }) => void;
  isLoading: boolean;
}

const FormContainer = styled.div`
  background-color: #ffffff;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 2rem;
`;

const FormTitle = styled.h2`
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: #343a40;
`;

const FormGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
`;

const FormGroup = styled.div`
  margin-bottom: 1rem;
`;

const Label = styled.label`
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #495057;
`;

const Input = styled.input`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  font-size: 1rem;

  &:focus {
    border-color: #ffc107;
    outline: none;
    box-shadow: 0 0 0 0.2rem rgba(255, 193, 7, 0.25);
  }
`;

const SubmitButton = styled.button<{ $isLoading: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.5rem;
  background-color: ${(props) => (props.$isLoading ? '#e9ecef' : '#ffc107')};
  color: ${(props) => (props.$isLoading ? '#6c757d' : '#212529')};
  border: none;
  border-radius: 0.25rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: ${(props) => (props.$isLoading ? 'not-allowed' : 'pointer')};
  transition: background-color 0.2s;
  margin-top: 1rem;

  &:hover {
    background-color: ${(props) => (props.$isLoading ? '#e9ecef' : '#ffca2c')};
  }

  svg {
    margin-right: 0.5rem;
  }
`;

const ForecastForm: React.FC<ForecastFormProps> = ({ onSubmit, isLoading }) => {
  const [latitude, setLatitude] = useState(37.7749);
  const [longitude, setLongitude] = useState(-122.4194);
  const [locationId, setLocationId] = useState('home');
  const [systemCapacityKw, setSystemCapacityKw] = useState(5.0);
  const [electricityRate, setElectricityRate] = useState(0.15);
  const [feedInTariff, setFeedInTariff] = useState(0.08);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    onSubmit({
      latitude,
      longitude,
      locationId,
      systemCapacityKw,
      electricityRate,
      feedInTariff,
    });
  };

  return (
    <FormContainer>
      <FormTitle>Solar Forecast Parameters</FormTitle>
      <form onSubmit={handleSubmit}>
        <FormGrid>
          <FormGroup>
            <Label htmlFor="latitude">Latitude</Label>
            <Input
              id="latitude"
              type="number"
              step="0.0001"
              min="-90"
              max="90"
              value={latitude}
              onChange={(e) => setLatitude(parseFloat(e.target.value))}
              required
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="longitude">Longitude</Label>
            <Input
              id="longitude"
              type="number"
              step="0.0001"
              min="-180"
              max="180"
              value={longitude}
              onChange={(e) => setLongitude(parseFloat(e.target.value))}
              required
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="locationId">Location ID</Label>
            <Input
              id="locationId"
              type="text"
              value={locationId}
              onChange={(e) => setLocationId(e.target.value)}
              required
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="systemCapacity">System Capacity (kW)</Label>
            <Input
              id="systemCapacity"
              type="number"
              step="0.1"
              min="0.1"
              max="100"
              value={systemCapacityKw}
              onChange={(e) => setSystemCapacityKw(parseFloat(e.target.value))}
              required
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="electricityRate">Electricity Rate ($/kWh)</Label>
            <Input
              id="electricityRate"
              type="number"
              step="0.01"
              min="0.01"
              max="1"
              value={electricityRate}
              onChange={(e) => setElectricityRate(parseFloat(e.target.value))}
              required
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="feedInTariff">Feed-in Tariff ($/kWh)</Label>
            <Input
              id="feedInTariff"
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={feedInTariff}
              onChange={(e) => setFeedInTariff(parseFloat(e.target.value))}
              required
            />
          </FormGroup>
        </FormGrid>

        <SubmitButton type="submit" $isLoading={isLoading} disabled={isLoading}>
          <FaSearch />
          {isLoading ? 'Generating Forecast...' : 'Generate Forecast'}
        </SubmitButton>
      </form>
    </FormContainer>
  );
};

export default ForecastForm;
