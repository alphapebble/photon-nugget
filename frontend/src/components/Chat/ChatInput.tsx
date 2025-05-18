import React, { useState } from 'react';
import styled from 'styled-components';
import { FaPaperPlane } from 'react-icons/fa';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

const InputContainer = styled.div`
  display: flex;
  margin-top: 1rem;
`;

const StyledInput = styled.input`
  flex: 1;
  padding: 1rem;
  border: 1px solid #ced4da;
  border-radius: 0.5rem 0 0 0.5rem;
  font-size: 1rem;
  outline: none;

  &:focus {
    border-color: #ffc107;
    box-shadow: 0 0 0 0.2rem rgba(255, 193, 7, 0.25);
  }
`;

const SendButton = styled.button<{ $isLoading: boolean }>`
  padding: 0 1.5rem;
  background-color: ${(props) => (props.$isLoading ? '#e9ecef' : '#ffc107')};
  color: ${(props) => (props.$isLoading ? '#6c757d' : '#212529')};
  border: none;
  border-radius: 0 0.5rem 0.5rem 0;
  cursor: ${(props) => (props.$isLoading ? 'not-allowed' : 'pointer')};
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;

  &:hover {
    background-color: ${(props) => (props.$isLoading ? '#e9ecef' : '#ffca2c')};
  }
`;

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <InputContainer>
        <StyledInput
          type="text"
          placeholder="Ask a question about solar energy..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={isLoading}
        />
        <SendButton type="submit" $isLoading={isLoading}>
          <FaPaperPlane />
        </SendButton>
      </InputContainer>
    </form>
  );
};

export default ChatInput;
