import React, { useEffect, useState } from 'react';
import type { AppProps } from 'next/app';
import { createGlobalStyle, ThemeProvider } from 'styled-components';
import Layout from '../components/Layout';
import Head from 'next/head';
import ClientOnly from '../components/common/ClientOnly';

// Define theme
const theme = {
  colors: {
    primary: '#ffc107',
    secondary: '#343a40',
    background: '#f9f9f9',
    text: '#333',
    lightGray: '#f8f9fa',
    mediumGray: '#e9ecef',
    darkGray: '#6c757d',
  },
};

// Global styles
const GlobalStyle = createGlobalStyle`
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
      Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    color: ${({ theme }) => theme.colors.text};
    background-color: ${({ theme }) => theme.colors.background};
  }

  a {
    color: inherit;
    text-decoration: none;
  }
`;

function MyApp({ Component, pageProps }: AppProps) {
  // Use state to track if we're on the client
  const [mounted, setMounted] = useState(false);

  // When the app is mounted on the client, update the state
  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <>
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Solar Sage</title>
      </Head>

      <ThemeProvider theme={theme}>
        <GlobalStyle />
        <ClientOnly fallback={<div style={{ visibility: 'hidden' }}>Loading...</div>}>
          <Layout>
            <Component {...pageProps} />
          </Layout>
        </ClientOnly>
      </ThemeProvider>
    </>
  );
}

export default MyApp;
