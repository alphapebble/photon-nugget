import React from 'react';
import styled from 'styled-components';
import { FaServer, FaReact, FaDatabase, FaChartBar, FaRobot } from 'react-icons/fa';

const AboutContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  margin-bottom: 1.5rem;
  color: #343a40;
`;

const Section = styled.section`
  margin-bottom: 3rem;
`;

const SectionTitle = styled.h2`
  font-size: 1.75rem;
  margin-bottom: 1rem;
  color: #343a40;
  display: flex;
  align-items: center;
  
  svg {
    margin-right: 0.75rem;
    color: #ffc107;
  }
`;

const Paragraph = styled.p`
  font-size: 1.1rem;
  line-height: 1.6;
  color: #495057;
  margin-bottom: 1rem;
`;

const TechList = styled.ul`
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
`;

const TechItem = styled.li`
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  font-weight: 500;
  display: flex;
  align-items: center;
  
  svg {
    margin-right: 0.5rem;
    color: #ffc107;
  }
`;

const AboutPage: React.FC = () => {
  return (
    <AboutContainer>
      <Title>About Solar Sage</Title>
      
      <Section>
        <Paragraph>
          Solar Sage is an intelligent solar energy assistant that combines advanced RAG (Retrieval Augmented Generation) techniques with real-time weather data and solar forecasting to provide accurate, contextual answers to your questions about solar energy.
        </Paragraph>
      </Section>
      
      <Section>
        <SectionTitle>
          <FaRobot />
          Intelligent Assistance
        </SectionTitle>
        <Paragraph>
          Solar Sage uses a dual-agent architecture for RAG, with a retriever agent and a generator agent working together to provide accurate, contextual responses. The system is enhanced with real-time weather data and solar forecasting to provide location-specific insights.
        </Paragraph>
      </Section>
      
      <Section>
        <SectionTitle>
          <FaChartBar />
          Solar Forecasting
        </SectionTitle>
        <Paragraph>
          The solar forecasting system uses weather data and system specifications to predict solar production and cost savings. It provides daily and hourly forecasts, as well as cost savings analysis and ROI calculations.
        </Paragraph>
      </Section>
      
      <Section>
        <SectionTitle>
          <FaServer />
          Technical Details
        </SectionTitle>
        <Paragraph>
          Solar Sage is built with modern technologies to provide a fast, responsive, and reliable experience.
        </Paragraph>
        <TechList>
          <TechItem>
            <FaServer /> FastAPI Backend
          </TechItem>
          <TechItem>
            <FaReact /> Next.js Frontend
          </TechItem>
          <TechItem>
            <FaDatabase /> LanceDB Vector Store
          </TechItem>
          <TechItem>
            <FaRobot /> RAG Architecture
          </TechItem>
          <TechItem>
            <FaChartBar /> Plotly Visualizations
          </TechItem>
        </TechList>
      </Section>
    </AboutContainer>
  );
};

export default AboutPage;
