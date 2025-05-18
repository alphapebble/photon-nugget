import React from 'react';
import styled from 'styled-components';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { FaHome, FaChartLine, FaComments, FaInfoCircle, FaChartBar } from 'react-icons/fa';

const SidebarContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 2rem 0;
`;

const SidebarHeader = styled.div`
  padding: 0 1.5rem 2rem;
  font-size: 1.5rem;
  font-weight: bold;
  color: ${({ theme }) => theme.colors.secondary};
  display: flex;
  align-items: center;
`;

const SidebarIcon = styled(FaChartLine)`
  color: ${({ theme }) => theme.colors.primary};
  margin-right: 0.5rem;
`;

const NavItems = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

interface NavItemProps {
  $active: boolean;
}

const NavItem = styled.li<NavItemProps>`
  margin-bottom: 0.5rem;

  a {
    display: flex;
    align-items: center;
    padding: 0.75rem 1.5rem;
    color: ${(props) => (props.$active ? props.theme.colors.primary : props.theme.colors.secondary)};
    text-decoration: none;
    font-weight: ${(props) => (props.$active ? 'bold' : 'normal')};
    background-color: ${(props) => (props.$active ? props.theme.colors.lightGray : 'transparent')};
    border-left: ${(props) => (props.$active ? `4px solid ${props.theme.colors.primary}` : '4px solid transparent')};

    &:hover {
      background-color: ${({ theme }) => theme.colors.lightGray};
      color: ${({ theme }) => theme.colors.primary};
    }

    svg {
      margin-right: 0.75rem;
    }
  }
`;

const Sidebar: React.FC = () => {
  const router = useRouter();

  const navItems = [
    { path: '/', label: 'Home', icon: <FaHome /> },
    { path: '/solar-forecast', label: 'Solar Forecast', icon: <FaChartLine /> },
    { path: '/chat', label: 'Chat', icon: <FaComments /> },
    { path: '/evaluation', label: 'Evaluation', icon: <FaChartBar /> },
    { path: '/about', label: 'About', icon: <FaInfoCircle /> },
  ];

  return (
    <SidebarContainer>
      <SidebarHeader>
        <SidebarIcon size={24} />
        Solar Sage
      </SidebarHeader>
      <NavItems>
        {navItems.map((item) => (
          <NavItem key={item.path} $active={router.pathname === item.path}>
            <Link href={item.path} passHref legacyBehavior>
              <a>
                {item.icon}
                {item.label}
              </a>
            </Link>
          </NavItem>
        ))}
      </NavItems>
    </SidebarContainer>
  );
};

export default Sidebar;
