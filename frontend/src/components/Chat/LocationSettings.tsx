import React from 'react';
import styled from 'styled-components';
import { FaMapMarkerAlt, FaSolarPanel, FaMoneyBillWave } from 'react-icons/fa';

interface LocationSettingsProps {
  lat: number;
  setLat: (lat: number) => void;
  lon: number;
  setLon: (lon: number) => void;
  locationId: string;
  setLocationId: (id: string) => void;
  systemCapacityKw: number;
  setSystemCapacityKw: (capacity: number) => void;
  electricityRate: number;
  setElectricityRate: (rate: number) => void;
  feedInTariff: number;
  setFeedInTariff: (tariff: number) => void;
}

const SettingsContainer = styled.div`
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
`;

const SettingsTitle = styled.h3`
  font-size: 1.25rem;
  margin-bottom: 1rem;
  color: #343a40;
  display: flex;
  align-items: center;
  
  svg {
    margin-right: 0.5rem;
    color: #ffc107;
  }
`;

const SettingsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
`;

const SettingsGroup = styled.div`
  margin-bottom: 1rem;
`;

const SettingsLabel = styled.label`
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #495057;
`;

const SettingsInput = styled.input`
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  font-size: 1rem;
  
  &:focus {
    border-color: #ffc107;
    outline: none;
    box-shadow: 0 0 0 0.2rem rgba(255, 193, 7, 0.25);
  }
`;

const LocationSettings: React.FC<LocationSettingsProps> = ({
  lat,
  setLat,
  lon,
  setLon,
  locationId,
  setLocationId,
  systemCapacityKw,
  setSystemCapacityKw,
  electricityRate,
  setElectricityRate,
  feedInTariff,
  setFeedInTariff,
}) => {
  return (
    <SettingsContainer>
      <SettingsTitle>
        <FaMapMarkerAlt />
        Location Settings
      </SettingsTitle>
      <SettingsGrid>
        <SettingsGroup>
          <SettingsLabel htmlFor="latitude">Latitude</SettingsLabel>
          <SettingsInput
            id="latitude"
            type="number"
            step="0.0001"
            min="-90"
            max="90"
            value={lat}
            onChange={(e) => setLat(parseFloat(e.target.value))}
          />
        </SettingsGroup>
        
        <SettingsGroup>
          <SettingsLabel htmlFor="longitude">Longitude</SettingsLabel>
          <SettingsInput
            id="longitude"
            type="number"
            step="0.0001"
            min="-180"
            max="180"
            value={lon}
            onChange={(e) => setLon(parseFloat(e.target.value))}
          />
        </SettingsGroup>
        
        <SettingsGroup>
          <SettingsLabel htmlFor="locationId">Location ID</SettingsLabel>
          <SettingsInput
            id="locationId"
            type="text"
            value={locationId}
            onChange={(e) => setLocationId(e.target.value)}
          />
        </SettingsGroup>
      </SettingsGrid>
      
      <SettingsTitle>
        <FaSolarPanel />
        System Settings
      </SettingsTitle>
      <SettingsGrid>
        <SettingsGroup>
          <SettingsLabel htmlFor="systemCapacity">System Capacity (kW)</SettingsLabel>
          <SettingsInput
            id="systemCapacity"
            type="number"
            step="0.1"
            min="0.1"
            max="100"
            value={systemCapacityKw}
            onChange={(e) => setSystemCapacityKw(parseFloat(e.target.value))}
          />
        </SettingsGroup>
        
        <SettingsGroup>
          <SettingsLabel htmlFor="electricityRate">Electricity Rate ($/kWh)</SettingsLabel>
          <SettingsInput
            id="electricityRate"
            type="number"
            step="0.01"
            min="0.01"
            max="1"
            value={electricityRate}
            onChange={(e) => setElectricityRate(parseFloat(e.target.value))}
          />
        </SettingsGroup>
        
        <SettingsGroup>
          <SettingsLabel htmlFor="feedInTariff">Feed-in Tariff ($/kWh)</SettingsLabel>
          <SettingsInput
            id="feedInTariff"
            type="number"
            step="0.01"
            min="0"
            max="1"
            value={feedInTariff}
            onChange={(e) => setFeedInTariff(parseFloat(e.target.value))}
          />
        </SettingsGroup>
      </SettingsGrid>
    </SettingsContainer>
  );
};

export default LocationSettings;
