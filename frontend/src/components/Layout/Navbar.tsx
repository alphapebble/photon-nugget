import React from 'react';
import styled from 'styled-components';
import { FaSun } from 'react-icons/fa';

const NavbarContainer = styled.nav`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #ffffff;
  border-bottom: 1px solid ${({ theme }) => theme.colors.mediumGray};
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  font-size: 1.5rem;
  font-weight: bold;
  color: ${({ theme }) => theme.colors.secondary};
`;

const LogoIcon = styled(FaSun)`
  color: ${({ theme }) => theme.colors.primary};
  margin-right: 0.5rem;
`;

const NavLinks = styled.div`
  display: flex;
  gap: 1.5rem;
`;

const NavLink = styled.a`
  color: ${({ theme }) => theme.colors.secondary};
  text-decoration: none;
  font-weight: 500;

  &:hover {
    color: ${({ theme }) => theme.colors.primary};
  }
`;

const Navbar: React.FC = () => {
  return (
    <NavbarContainer>
      <Logo>
        <LogoIcon size={24} />
        Solar Sage
      </Logo>
      <NavLinks>
        <NavLink href="https://github.com/yourusername/solar-sage" target="_blank">
          GitHub
        </NavLink>
        <NavLink href="/about">About</NavLink>
      </NavLinks>
    </NavbarContainer>
  );
};

export default Navbar;
