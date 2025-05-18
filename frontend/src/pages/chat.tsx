import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { FaComments } from 'react-icons/fa';
import { ChatMessage, ChatInput, LocationSettings } from '../components/Chat';
import apiClient, { ChatRequest, ChatResponse } from '../api/apiClient';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const ChatContainer = styled.div`
  max-width: 1000px;
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

const ChatBox = styled.div`
  background-color: #ffffff;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const MessagesContainer = styled.div`
  padding: 1.5rem;
  height: 500px;
  overflow-y: auto;
`;

const InputContainer = styled.div`
  padding: 1rem;
  border-top: 1px solid #e9ecef;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6c757d;
  text-align: center;
  padding: 2rem;
`;

const EmptyStateIcon = styled(FaComments)`
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #e9ecef;
`;

const EmptyStateText = styled.p`
  font-size: 1.1rem;
  max-width: 400px;
`;

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Location and system settings
  const [lat, setLat] = useState(37.7749);
  const [lon, setLon] = useState(-122.4194);
  const [locationId, setLocationId] = useState('home');
  const [systemCapacityKw, setSystemCapacityKw] = useState(5.0);
  const [electricityRate, setElectricityRate] = useState(0.15);
  const [feedInTariff, setFeedInTariff] = useState(0.08);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = { role: 'user', content };
    setMessages((prev) => [...prev, userMessage]);

    setIsLoading(true);

    try {
      // Prepare request
      const request: ChatRequest = {
        query: content,
        lat,
        lon,
        include_weather: true,
        location_id: locationId,
        system_capacity_kw: systemCapacityKw,
        electricity_rate: electricityRate,
        feed_in_tariff: feedInTariff,
        include_solar_forecast: true,
      };

      // Send request to API
      const response = await apiClient.getRagResponse(request);

      // Format the response content
      let responseContent = response.response;

      // Add weather context if available
      if (response.has_weather_context && response.weather_summary && response.weather_summary.length > 0) {
        responseContent += "\n\n**Weather Context:**\n";
        response.weather_summary.forEach((item) => {
          responseContent += `- ${item}\n`;
        });
      }

      // Add solar forecast if available
      if (response.has_solar_forecast && response.solar_summary && response.solar_summary.length > 0) {
        responseContent += "\n\n**Solar Forecast:**\n";
        response.solar_summary.forEach((item) => {
          responseContent += `- ${item}\n`;
        });
      }

      // Add assistant message
      const assistantMessage: Message = {
        role: 'assistant',
        content: responseContent,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.',
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ChatContainer>
      <Title>
        <FaComments />
        Chat with Solar Sage
      </Title>

      <LocationSettings
        lat={lat}
        setLat={setLat}
        lon={lon}
        setLon={setLon}
        locationId={locationId}
        setLocationId={setLocationId}
        systemCapacityKw={systemCapacityKw}
        setSystemCapacityKw={setSystemCapacityKw}
        electricityRate={electricityRate}
        setElectricityRate={setElectricityRate}
        feedInTariff={feedInTariff}
        setFeedInTariff={setFeedInTariff}
      />

      <ChatBox>
        <MessagesContainer>
          {messages.length === 0 ? (
            <EmptyState>
              <EmptyStateIcon />
              <EmptyStateText>
                Ask Solar Sage anything about solar energy, weather impacts, forecasting, or cost savings.
              </EmptyStateText>
            </EmptyState>
          ) : (
            messages.map((message, index) => (
              <ChatMessage
                key={index}
                role={message.role}
                content={message.content}
              />
            ))
          )}
          <div ref={messagesEndRef} />
        </MessagesContainer>

        <InputContainer>
          <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
        </InputContainer>
      </ChatBox>
    </ChatContainer>
  );
};

export default ChatPage;
