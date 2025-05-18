import React from 'react';
import styled from 'styled-components';
import { FaUser, FaRobot } from 'react-icons/fa';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
}

const MessageContainer = styled.div<{ $isUser: boolean }>`
  display: flex;
  margin-bottom: 1.5rem;
  flex-direction: ${(props) => (props.$isUser ? 'row-reverse' : 'row')};
`;

const Avatar = styled.div<{ $isUser: boolean }>`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: ${(props) => (props.$isUser ? '#ffc107' : '#6c757d')};
  color: white;
  margin: ${(props) => (props.$isUser ? '0 0 0 1rem' : '0 1rem 0 0')};
`;

const MessageContent = styled.div<{ $isUser: boolean }>`
  max-width: 70%;
  padding: 1rem;
  border-radius: 1rem;
  background-color: ${(props) => (props.$isUser ? '#fff3cd' : '#f8f9fa')};
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const MessageText = styled.div`
  font-size: 1rem;
  line-height: 1.5;
  color: #343a40;

  p {
    margin-bottom: 0.75rem;

    &:last-child {
      margin-bottom: 0;
    }
  }

  ul, ol {
    margin-left: 1.5rem;
    margin-bottom: 0.75rem;
  }

  a {
    color: #0d6efd;
    text-decoration: underline;

    &:hover {
      text-decoration: none;
    }
  }

  code {
    background-color: #f1f3f5;
    padding: 0.2rem 0.4rem;
    border-radius: 0.25rem;
    font-family: monospace;
  }

  pre {
    background-color: #f1f3f5;
    padding: 1rem;
    border-radius: 0.5rem;
    overflow-x: auto;
    margin-bottom: 0.75rem;

    code {
      background-color: transparent;
      padding: 0;
    }
  }
`;

const ChatMessage: React.FC<ChatMessageProps> = ({ role, content }) => {
  const isUser = role === 'user';

  // Convert markdown-like content to HTML
  const formatContent = (text: string) => {
    return { __html: text };
  };

  return (
    <MessageContainer $isUser={isUser}>
      <Avatar $isUser={isUser}>
        {isUser ? <FaUser /> : <FaRobot />}
      </Avatar>
      <MessageContent $isUser={isUser}>
        <MessageText dangerouslySetInnerHTML={formatContent(content)} />
      </MessageContent>
    </MessageContainer>
  );
};

export default ChatMessage;
