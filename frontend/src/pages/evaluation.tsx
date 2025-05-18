import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaSync, FaChartLine, FaTable } from 'react-icons/fa';
import dynamic from 'next/dynamic';
import ClientOnly from '../components/common/ClientOnly';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

// Styled components
const PageContainer = styled.div`
  padding: 2rem;
`;

const Header = styled.div`
  margin-bottom: 2rem;
`;

const Title = styled.h1`
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: ${({ theme }) => theme.colors.secondary};
`;

const Description = styled.p`
  color: ${({ theme }) => theme.colors.darkGray};
  margin-bottom: 1.5rem;
`;

const ControlsContainer = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
  gap: 1rem;
`;

const Input = styled.input`
  padding: 0.5rem;
  border: 1px solid ${({ theme }) => theme.colors.mediumGray};
  border-radius: 0.25rem;
  flex: 1;
`;

const Button = styled.button<{ $primary?: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  background-color: ${({ $primary, theme }) => $primary ? theme.colors.primary : theme.colors.lightGray};
  color: ${({ $primary, theme }) => $primary ? theme.colors.secondary : theme.colors.darkGray};
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-weight: 500;
  
  &:hover {
    background-color: ${({ $primary, theme }) => $primary ? '#ffca2c' : theme.colors.mediumGray};
  }
  
  svg {
    margin-right: 0.5rem;
  }
`;

const SummaryContainer = styled.div`
  background-color: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const SummaryTitle = styled.h2`
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: ${({ theme }) => theme.colors.secondary};
`;

const SummaryTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  
  th, td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid ${({ theme }) => theme.colors.mediumGray};
  }
  
  th {
    font-weight: 600;
    color: ${({ theme }) => theme.colors.secondary};
  }
`;

const ChartContainer = styled.div`
  background-color: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const ChartTitle = styled.h2`
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: ${({ theme }) => theme.colors.secondary};
`;

const DetailedResultsContainer = styled.div`
  background-color: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
`;

const DetailedResultsTitle = styled.h2`
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: ${({ theme }) => theme.colors.secondary};
  display: flex;
  align-items: center;
  
  svg {
    margin-right: 0.5rem;
  }
`;

const DetailedResultsTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  
  th, td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid ${({ theme }) => theme.colors.mediumGray};
  }
  
  th {
    font-weight: 600;
    color: ${({ theme }) => theme.colors.secondary};
    position: sticky;
    top: 0;
    background-color: white;
    z-index: 10;
  }
  
  tr:hover {
    background-color: ${({ theme }) => theme.colors.lightGray};
  }
`;

const LoadingMessage = styled.div`
  text-align: center;
  padding: 2rem;
  color: ${({ theme }) => theme.colors.darkGray};
`;

const ErrorMessage = styled.div`
  text-align: center;
  padding: 2rem;
  color: #dc3545;
`;

// Types
interface SummaryMetrics {
  timestamp: string;
  num_questions: number;
  basic_metrics: {
    avg_keyword_match: number;
    avg_response_time: number;
    avg_response_length: number;
  };
  ragas_metrics?: {
    [key: string]: number;
  };
  nlp_metrics?: {
    [key: string]: number;
  };
  file_name: string;
}

interface DetailedResult {
  Question: string;
  Response: string;
  'Response Length': number;
  'Response Time (s)': number;
  'Keyword Match %': number;
  'Matched Keywords': string;
  'Expected Keywords': string;
  'Used Dual Agent': boolean;
  'Included Weather': boolean;
  [key: string]: any;
}

const EvaluationPage: React.FC = () => {
  const [resultsDir, setResultsDir] = useState<string>('evaluation/results');
  const [summaryMetrics, setSummaryMetrics] = useState<SummaryMetrics[]>([]);
  const [detailedResults, setDetailedResults] = useState<DetailedResult[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load evaluation results
  const loadResults = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // In a real implementation, this would make an API call to the backend
      // For now, we'll simulate loading data
      const response = await fetch(`/api/evaluation/results?dir=${encodeURIComponent(resultsDir)}`);
      
      if (!response.ok) {
        throw new Error(`Failed to load evaluation results: ${response.statusText}`);
      }
      
      const data = await response.json();
      setSummaryMetrics(data.summaryMetrics || []);
      setDetailedResults(data.detailedResults || []);
    } catch (err) {
      console.error('Error loading evaluation results:', err);
      setError('Failed to load evaluation results. Please check the results directory path.');
    } finally {
      setLoading(false);
    }
  };

  // Load results on initial render
  useEffect(() => {
    loadResults();
  }, []);

  // Create metrics chart
  const createMetricsChart = () => {
    if (!summaryMetrics || summaryMetrics.length === 0) {
      return {
        data: [],
        layout: {
          title: 'Evaluation Metrics Over Time',
          xaxis: { title: 'Evaluation Time' },
          yaxis: { title: 'Metric Value' },
          annotations: [{
            text: 'No evaluation data available',
            xref: 'paper',
            yref: 'paper',
            x: 0.5,
            y: 0.5,
            showarrow: false,
            font: { size: 16 }
          }]
        }
      };
    }

    // Extract data for chart
    const data = [];
    const metrics = new Set<string>();
    
    // Process each summary metrics object
    summaryMetrics.forEach(metrics => {
      const timestamp = metrics.timestamp;
      
      // Add basic metrics
      Object.entries(metrics.basic_metrics).forEach(([name, value]) => {
        const metricName = name.replace('avg_', '').replace('_', ' ');
        metrics.add(metricName);
        data.push({
          timestamp,
          metric: metricName,
          value,
          category: 'Basic'
        });
      });
      
      // Add RAGAS metrics if available
      if (metrics.ragas_metrics) {
        Object.entries(metrics.ragas_metrics).forEach(([name, value]) => {
          const metricName = name.replace('avg_', '').replace('_', ' ');
          metrics.add(metricName);
          data.push({
            timestamp,
            metric: metricName,
            value,
            category: 'RAGAS'
          });
        });
      }
      
      // Add NLP metrics if available
      if (metrics.nlp_metrics) {
        Object.entries(metrics.nlp_metrics).forEach(([name, value]) => {
          const metricName = name.replace('avg_', '').replace('_', ' ');
          metrics.add(metricName);
          data.push({
            timestamp,
            metric: metricName,
            value,
            category: 'NLP'
          });
        });
      }
    });
    
    // Create traces for each metric
    const traces = Array.from(metrics).map(metric => {
      const metricData = data.filter(d => d.metric === metric);
      return {
        x: metricData.map(d => d.timestamp),
        y: metricData.map(d => d.value),
        type: 'scatter',
        mode: 'lines+markers',
        name: metric
      };
    });
    
    return {
      data: traces,
      layout: {
        title: 'Evaluation Metrics Over Time',
        xaxis: { title: 'Evaluation Time' },
        yaxis: { title: 'Metric Value' },
        legend: { title: 'Metric' },
        hovermode: 'closest'
      }
    };
  };

  // Create comparison chart
  const createComparisonChart = () => {
    if (!detailedResults || detailedResults.length === 0) {
      return {
        data: [],
        layout: {
          title: 'Metrics Comparison Across Questions',
          xaxis: { title: 'Question' },
          yaxis: { title: 'Metric Value' },
          annotations: [{
            text: 'No detailed evaluation data available',
            xref: 'paper',
            yref: 'paper',
            x: 0.5,
            y: 0.5,
            showarrow: false,
            font: { size: 16 }
          }]
        }
      };
    }

    // Select metrics to compare
    const metrics = [];
    
    // Always include keyword match if available
    if ('Keyword Match %' in detailedResults[0]) {
      metrics.push('Keyword Match %');
    }
    
    // Add RAGAS metrics if available
    const ragasMetrics = Object.keys(detailedResults[0]).filter(key => key.startsWith('RAGAS '));
    metrics.push(...ragasMetrics.slice(0, 3)); // Limit to top 3 RAGAS metrics
    
    // Add BLEU/ROUGE if available and needed
    if (metrics.length < 4) {
      if ('BLEU Score' in detailedResults[0]) {
        metrics.push('BLEU Score');
      }
      if ('ROUGE-1 F1' in detailedResults[0]) {
        metrics.push('ROUGE-1 F1');
      }
    }
    
    // Ensure we have at least one metric
    if (metrics.length === 0) {
      return {
        data: [],
        layout: {
          title: 'Metrics Comparison Across Questions',
          xaxis: { title: 'Question' },
          yaxis: { title: 'Metric Value' },
          annotations: [{
            text: 'No metrics available for comparison',
            xref: 'paper',
            yref: 'paper',
            x: 0.5,
            y: 0.5,
            showarrow: false,
            font: { size: 16 }
          }]
        }
      };
    }
    
    // Create traces for each metric
    const traces = metrics.map(metric => {
      return {
        x: detailedResults.map(result => {
          const question = result.Question;
          return question.length > 30 ? question.substring(0, 27) + '...' : question;
        }),
        y: detailedResults.map(result => result[metric] || 0),
        type: 'bar',
        name: metric
      };
    });
    
    return {
      data: traces,
      layout: {
        title: 'Metrics Comparison Across Questions',
        xaxis: { title: 'Question' },
        yaxis: { title: 'Metric Value' },
        legend: { title: 'Metric' },
        barmode: 'group'
      }
    };
  };

  const metricsChart = createMetricsChart();
  const comparisonChart = createComparisonChart();

  return (
    <PageContainer>
      <Header>
        <Title>Evaluation Dashboard</Title>
        <Description>
          View and analyze RAG system evaluation results
        </Description>
      </Header>
      
      <ControlsContainer>
        <Input
          type="text"
          value={resultsDir}
          onChange={(e) => setResultsDir(e.target.value)}
          placeholder="Results directory path"
        />
        <Button $primary onClick={loadResults}>
          <FaSync /> Refresh Data
        </Button>
      </ControlsContainer>
      
      {loading ? (
        <LoadingMessage>Loading evaluation results...</LoadingMessage>
      ) : error ? (
        <ErrorMessage>{error}</ErrorMessage>
      ) : (
        <>
          <SummaryContainer>
            <SummaryTitle>Summary Metrics</SummaryTitle>
            {summaryMetrics.length > 0 ? (
              <SummaryTable>
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Questions</th>
                    <th>Keyword Match</th>
                    <th>Response Time</th>
                    {summaryMetrics[0].ragas_metrics && Object.keys(summaryMetrics[0].ragas_metrics).map(metric => (
                      <th key={metric}>{metric.replace('avg_', '').replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {summaryMetrics.map((metrics, index) => (
                    <tr key={index}>
                      <td>{metrics.timestamp}</td>
                      <td>{metrics.num_questions}</td>
                      <td>{metrics.basic_metrics.avg_keyword_match.toFixed(2)}%</td>
                      <td>{metrics.basic_metrics.avg_response_time.toFixed(3)}s</td>
                      {metrics.ragas_metrics && Object.values(metrics.ragas_metrics).map((value, i) => (
                        <td key={i}>{value.toFixed(4)}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </SummaryTable>
            ) : (
              <p>No summary metrics available.</p>
            )}
          </SummaryContainer>
          
          <ChartContainer>
            <ChartTitle>Metrics Over Time</ChartTitle>
            <ClientOnly>
              <Plot
                data={metricsChart.data}
                layout={metricsChart.layout}
                style={{ width: '100%', height: '400px' }}
                useResizeHandler={true}
              />
            </ClientOnly>
          </ChartContainer>
          
          <ChartContainer>
            <ChartTitle>Metrics Comparison Across Questions</ChartTitle>
            <ClientOnly>
              <Plot
                data={comparisonChart.data}
                layout={comparisonChart.layout}
                style={{ width: '100%', height: '400px' }}
                useResizeHandler={true}
              />
            </ClientOnly>
          </ChartContainer>
          
          <DetailedResultsContainer>
            <DetailedResultsTitle>
              <FaTable /> Detailed Results
            </DetailedResultsTitle>
            {detailedResults.length > 0 ? (
              <DetailedResultsTable>
                <thead>
                  <tr>
                    <th>Question</th>
                    <th>Response Preview</th>
                    <th>Keyword Match %</th>
                    <th>Response Time (s)</th>
                    <th>Used Dual Agent</th>
                    <th>Included Weather</th>
                  </tr>
                </thead>
                <tbody>
                  {detailedResults.map((result, index) => (
                    <tr key={index}>
                      <td>{result.Question}</td>
                      <td>{result.Response.substring(0, 100)}...</td>
                      <td>{result['Keyword Match %'].toFixed(2)}%</td>
                      <td>{result['Response Time (s)'].toFixed(3)}s</td>
                      <td>{result['Used Dual Agent'] ? 'Yes' : 'No'}</td>
                      <td>{result['Included Weather'] ? 'Yes' : 'No'}</td>
                    </tr>
                  ))}
                </tbody>
              </DetailedResultsTable>
            ) : (
              <p>No detailed results available.</p>
            )}
          </DetailedResultsContainer>
        </>
      )}
    </PageContainer>
  );
};

export default EvaluationPage;
