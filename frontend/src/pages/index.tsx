import React from 'react';
import styled from 'styled-components';
import Link from 'next/link';
import { FaChartLine, FaComments, FaInfoCircle } from 'react-icons/fa';

const HomeContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const Hero = styled.div`
  text-align: center;
  margin-bottom: 3rem;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: #343a40;
`;

const Subtitle = styled.p`
  font-size: 1.25rem;
  color: #6c757d;
  max-width: 800px;
  margin: 0 auto;
`;

const FeaturesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 3rem;
`;

const FeatureCard = styled.div`
  background-color: #ffffff;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;

  &:hover {
    transform: translateY(-5px);
  }
`;

const FeatureIcon = styled.div`
  font-size: 2rem;
  color: #ffc107;
  margin-bottom: 1rem;
`;

const FeatureTitle = styled.h3`
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #343a40;
`;

const FeatureDescription = styled.p`
  color: #6c757d;
  margin-bottom: 1.5rem;
`;

const FeatureLink = styled.a`
  display: inline-block;
  color: #ffc107;
  font-weight: bold;

  &:hover {
    text-decoration: underline;
  }
`;

const HomePage: React.FC = () => {
  return (
    <HomeContainer>
      <Hero>
        <Title>Welcome to Solar Sage</Title>
        <Subtitle>
          Your intelligent solar energy assistant, providing forecasting, insights, and answers to all your solar energy questions.
        </Subtitle>
      </Hero>

      <FeaturesGrid>
        <FeatureCard>
          <FeatureIcon>
            <FaChartLine />
          </FeatureIcon>
          <FeatureTitle>Solar Energy Forecasting</FeatureTitle>
          <FeatureDescription>
            Predict your solar production and cost savings based on your location and system specifications.
          </FeatureDescription>
          <Link href="/solar-forecast" passHref legacyBehavior>
            <FeatureLink>Try Solar Forecast →</FeatureLink>
          </Link>
        </FeatureCard>

        <FeatureCard>
          <FeatureIcon>
            <FaComments />
          </FeatureIcon>
          <FeatureTitle>Chat with Solar Sage</FeatureTitle>
          <FeatureDescription>
            Ask questions about solar energy and get accurate, contextual answers enhanced with real-time data.
          </FeatureDescription>
          <Link href="/chat" passHref legacyBehavior>
            <FeatureLink>Start Chatting →</FeatureLink>
          </Link>
        </FeatureCard>

        <FeatureCard>
          <FeatureIcon>
            <FaInfoCircle />
          </FeatureIcon>
          <FeatureTitle>About Solar Sage</FeatureTitle>
          <FeatureDescription>
            Learn more about how Solar Sage works, including its RAG system, weather integration, and forecasting capabilities.
          </FeatureDescription>
          <Link href="/about" passHref legacyBehavior>
            <FeatureLink>Learn More →</FeatureLink>
          </Link>
        </FeatureCard>
      </FeaturesGrid>
    </HomeContainer>
  );
};

export default HomePage;
