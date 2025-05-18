import React from 'react';
import styled from 'styled-components';
import dynamic from 'next/dynamic';
import { format } from 'date-fns';
import ClientOnly from '../common/ClientOnly';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface ForecastResultsProps {
  forecast: any;
  costSavings: any;
}

const ResultsContainer = styled.div`
  background-color: #ffffff;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 2rem;
`;

const SectionTitle = styled.h2`
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: #343a40;
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const MetricCard = styled.div`
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1.5rem;
  text-align: center;
`;

const MetricValue = styled.div`
  font-size: 1.75rem;
  font-weight: bold;
  color: #343a40;
  margin-bottom: 0.5rem;
`;

const MetricLabel = styled.div`
  font-size: 0.875rem;
  color: #6c757d;
`;

const ChartContainer = styled.div`
  margin-bottom: 2rem;
`;

const InsightsContainer = styled.div`
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-top: 2rem;
`;

const InsightsList = styled.ul`
  list-style-type: none;
  padding: 0;
  margin: 0;
`;

const InsightItem = styled.li`
  margin-bottom: 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
  color: #495057;

  &:last-child {
    margin-bottom: 0;
  }
`;

const ForecastResults: React.FC<ForecastResultsProps> = ({ forecast, costSavings }) => {
  if (!forecast || !costSavings) {
    return null;
  }

  // Prepare data for daily forecast chart
  const dailyData = forecast.daily_forecast.map((day: any) => ({
    date: new Date(day.date),
    production: day.production,
    demand: day.demand,
    net: day.net,
  }));

  // Prepare data for hourly forecast chart
  const hourlyData = forecast.hourly_forecast.slice(0, 24).map((hour: any) => ({
    hour: new Date(hour.datetime).getHours(),
    production: hour.production,
    demand: hour.demand,
  }));

  // Prepare data for savings chart
  const savingsData = costSavings.daily_savings.map((day: any) => ({
    date: new Date(day.date),
    netSavings: day.net_savings,
  }));

  // Check if we have valid data
  if (!forecast.daily_forecast || forecast.daily_forecast.length === 0 ||
      !costSavings.daily_savings || costSavings.daily_savings.length === 0) {
    return (
      <ResultsContainer>
        <SectionTitle>No Forecast Data Available</SectionTitle>
        <p>Sorry, we couldn't generate a forecast with the provided parameters. Please try again with different inputs.</p>
      </ResultsContainer>
    );
  }

  // Calculate insights
  const totalProduction = dailyData.reduce((sum: number, day: any) => sum + day.production, 0);
  const totalDemand = dailyData.reduce((sum: number, day: any) => sum + day.demand, 0);
  const coveragePercent = (totalProduction / totalDemand) * 100;

  // Find the best day for production
  const bestDay = dailyData.length > 0 ?
    dailyData.reduce((best: any, day: any) => day.production > best.production ? day : best, dailyData[0]) :
    { date: new Date(), production: 0 };

  const summary = costSavings.summary;
  const dailySavings = summary.total_net_savings / summary.roi_days;
  const annualSavings = dailySavings * 365;

  const systemCostEstimate = forecast.system_capacity_kw * 1000; // $1000 per kW
  const simplePaybackYears = systemCostEstimate / annualSavings;

  return (
    <ResultsContainer>
      <SectionTitle>Solar Forecast Results</SectionTitle>

      {/* System Information */}
      <MetricsGrid>
        <MetricCard>
          <MetricValue>{forecast.system_capacity_kw} kW</MetricValue>
          <MetricLabel>System Capacity</MetricLabel>
        </MetricCard>

        <MetricCard>
          <MetricValue>
            {forecast.location.lat.toFixed(4)}, {forecast.location.lon.toFixed(4)}
          </MetricValue>
          <MetricLabel>Location</MetricLabel>
        </MetricCard>

        <MetricCard>
          <MetricValue>{forecast.forecast_horizon_days} days</MetricValue>
          <MetricLabel>Forecast Period</MetricLabel>
        </MetricCard>
      </MetricsGrid>

      {/* Daily Forecast Chart */}
      <ChartContainer>
        <SectionTitle>Daily Forecast</SectionTitle>
        <ClientOnly>
          <Plot
            data={[
              {
                x: dailyData.map((day: any) => day.date),
                y: dailyData.map((day: any) => day.production),
                type: 'bar',
                name: 'Production (kWh)',
                marker: { color: 'green', opacity: 0.7 },
              },
              {
                x: dailyData.map((day: any) => day.date),
                y: dailyData.map((day: any) => day.demand),
                type: 'bar',
                name: 'Demand (kWh)',
                marker: { color: 'blue', opacity: 0.7 },
              },
              {
                x: dailyData.map((day: any) => day.date),
                y: dailyData.map((day: any) => day.net),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Net (kWh)',
                line: { color: 'red', width: 2 },
              },
            ]}
            layout={{
              title: 'Daily Energy Production and Demand',
              xaxis: { title: 'Date' },
              yaxis: { title: 'Energy (kWh)' },
              barmode: 'group',
              legend: {
                orientation: 'h',
                y: 1.1,
                x: 0.5,
                xanchor: 'center',
              },
              autosize: true,
            }}
            style={{ width: '100%', height: '400px' }}
            useResizeHandler={true}
          />
        </ClientOnly>
      </ChartContainer>

      {/* Hourly Forecast Chart */}
      <ChartContainer>
        <SectionTitle>Hourly Forecast (Next 24 Hours)</SectionTitle>
        <ClientOnly>
          <Plot
            data={[
              {
                x: hourlyData.map((hour: any) => hour.hour),
                y: hourlyData.map((hour: any) => hour.production),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Production (kWh)',
                line: { color: 'green', width: 2 },
              },
              {
                x: hourlyData.map((hour: any) => hour.hour),
                y: hourlyData.map((hour: any) => hour.demand),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Demand (kWh)',
                line: { color: 'blue', width: 2 },
              },
            ]}
            layout={{
              title: 'Hourly Energy Production and Demand',
              xaxis: { title: 'Hour of Day' },
              yaxis: { title: 'Energy (kWh)' },
              legend: {
                orientation: 'h',
                y: 1.1,
                x: 0.5,
                xanchor: 'center',
              },
              autosize: true,
            }}
            style={{ width: '100%', height: '400px' }}
            useResizeHandler={true}
          />
        </ClientOnly>
      </ChartContainer>

      {/* Cost Savings */}
      <SectionTitle>Cost Savings Analysis</SectionTitle>
      <MetricsGrid>
        <MetricCard>
          <MetricValue>${summary.total_consumption_cost.toFixed(2)}</MetricValue>
          <MetricLabel>Total Consumption Cost</MetricLabel>
        </MetricCard>

        <MetricCard>
          <MetricValue>${summary.total_production_value.toFixed(2)}</MetricValue>
          <MetricLabel>Total Production Value</MetricLabel>
        </MetricCard>

        <MetricCard>
          <MetricValue>${summary.total_grid_purchase_cost.toFixed(2)}</MetricValue>
          <MetricLabel>Grid Purchase Cost</MetricLabel>
        </MetricCard>

        <MetricCard>
          <MetricValue>${summary.total_grid_export_revenue.toFixed(2)}</MetricValue>
          <MetricLabel>Grid Export Revenue</MetricLabel>
        </MetricCard>
      </MetricsGrid>

      <MetricCard>
        <MetricValue>${summary.total_net_savings.toFixed(2)}</MetricValue>
        <MetricLabel>Total Net Savings (${(summary.total_net_savings / summary.roi_days).toFixed(2)} per day)</MetricLabel>
      </MetricCard>

      {/* Daily Savings Chart */}
      <ChartContainer>
        <SectionTitle>Daily Savings</SectionTitle>
        <ClientOnly>
          <Plot
            data={[
              {
                x: savingsData.map((day: any) => day.date),
                y: savingsData.map((day: any) => day.netSavings),
                type: 'bar',
                name: 'Net Savings ($)',
                marker: { color: 'green' },
              },
            ]}
            layout={{
              title: 'Daily Cost Savings',
              xaxis: { title: 'Date' },
              yaxis: { title: 'Savings ($)' },
              autosize: true,
            }}
            style={{ width: '100%', height: '400px' }}
            useResizeHandler={true}
          />
        </ClientOnly>
      </ChartContainer>

      {/* ROI Calculation */}
      <SectionTitle>Return on Investment</SectionTitle>
      <MetricsGrid>
        <MetricCard>
          <MetricValue>${systemCostEstimate.toFixed(2)}</MetricValue>
          <MetricLabel>Estimated System Cost</MetricLabel>
        </MetricCard>

        <MetricCard>
          <MetricValue>${annualSavings.toFixed(2)}</MetricValue>
          <MetricLabel>Annual Savings</MetricLabel>
        </MetricCard>

        <MetricCard>
          <MetricValue>{simplePaybackYears.toFixed(1)} years</MetricValue>
          <MetricLabel>Simple Payback Period</MetricLabel>
        </MetricCard>
      </MetricsGrid>

      {/* Insights */}
      <InsightsContainer>
        <SectionTitle>Insights</SectionTitle>
        <InsightsList>
          <InsightItem>
            Your solar system is expected to produce <strong>{totalProduction.toFixed(1)} kWh</strong> over the next {forecast.forecast_horizon_days} days.
          </InsightItem>
          <InsightItem>
            This covers approximately <strong>{coveragePercent.toFixed(1)}%</strong> of your expected energy demand.
          </InsightItem>
          <InsightItem>
            The best day for production is <strong>{format(bestDay.date, 'EEEE, MMMM d')}</strong> with <strong>{bestDay.production.toFixed(1)} kWh</strong> expected.
          </InsightItem>
          <InsightItem>
            Your estimated daily savings are <strong>${dailySavings.toFixed(2)}</strong>, which projects to <strong>${annualSavings.toFixed(2)}</strong> annually.
          </InsightItem>
          {simplePaybackYears < Infinity && (
            <InsightItem>
              Based on these savings, a {forecast.system_capacity_kw} kW system might pay for itself in approximately <strong>{simplePaybackYears.toFixed(1)} years</strong>.
            </InsightItem>
          )}
        </InsightsList>
      </InsightsContainer>
    </ResultsContainer>
  );
};

export default ForecastResults;
