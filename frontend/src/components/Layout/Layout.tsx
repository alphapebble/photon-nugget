import React, { ReactNode } from 'react';
import styled from 'styled-components';
import Navbar from './Navbar';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: ReactNode;
}

const LayoutContainer = styled.div`
  display: flex;
  min-height: 100vh;
`;

const SidebarContainer = styled.div`
  width: 250px;
  background-color: ${({ theme }) => theme.colors.lightGray};
  border-right: 1px solid ${({ theme }) => theme.colors.mediumGray};
`;

const MainContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
`;

const ContentContainer = styled.main`
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
`;

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <LayoutContainer>
      <SidebarContainer>
        <Sidebar />
      </SidebarContainer>
      <MainContainer>
        <Navbar />
        <ContentContainer>{children}</ContentContainer>
      </MainContainer>
    </LayoutContainer>
  );
};

export default Layout;
