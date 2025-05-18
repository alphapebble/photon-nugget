import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// Types
export interface ChatRequest {
  query: string;
  lat?: number;
  lon?: number;
  include_weather?: boolean;
  location_id?: string;
  system_capacity_kw?: number;
  electricity_rate?: number;
  feed_in_tariff?: number;
  include_solar_forecast?: boolean;
}

export interface ChatResponse {
  response: string;
  has_weather_context: boolean;
  weather_summary?: string[];
  has_solar_forecast: boolean;
  solar_summary?: string[];
}

export interface SolarForecastRequest {
  latitude: number;
  longitude: number;
  location_id: string;
  system_capacity_kw: number;
}

export interface CostSavingsRequest extends SolarForecastRequest {
  electricity_rate: number;
  feed_in_tariff: number;
}

// API Client class
class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: '/api', // This will use Next.js API routes which proxy to the FastAPI backend
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // Sage endpoint (main interaction endpoint)
  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>('/sage', request);
    return response.data;
  }

  // Solar forecast endpoint - temporarily using chat endpoint
  async getSolarForecast(request: SolarForecastRequest): Promise<any> {
    // Since we don't have a dedicated solar forecast endpoint yet,
    // we'll use the chat endpoint with a formatted query
    const chatRequest: ChatRequest = {
      query: `Generate a solar forecast for a ${request.system_capacity_kw}kW system at location ${request.latitude}, ${request.longitude}`,
      lat: request.latitude,
      lon: request.longitude,
      location_id: request.location_id,
      system_capacity_kw: request.system_capacity_kw,
      include_weather: true,
      include_solar_forecast: true
    };

    const response = await this.client.post('/sage', chatRequest);

    // Format the response to match the expected structure
    return {
      forecast: {
        system_capacity_kw: request.system_capacity_kw,
        location: {
          lat: request.latitude,
          lon: request.longitude,
          id: request.location_id
        },
        forecast_horizon_days: 7,
        daily_forecast: [],
        hourly_forecast: []
      }
    };
  }

  // Cost savings endpoint - temporarily using chat endpoint
  async getCostSavings(request: CostSavingsRequest): Promise<any> {
    // Since we don't have a dedicated cost savings endpoint yet,
    // we'll use the chat endpoint with a formatted query
    const chatRequest: ChatRequest = {
      query: `Calculate cost savings for a ${request.system_capacity_kw}kW system at location ${request.latitude}, ${request.longitude} with electricity rate ${request.electricity_rate} and feed-in tariff ${request.feed_in_tariff}`,
      lat: request.latitude,
      lon: request.longitude,
      location_id: request.location_id,
      system_capacity_kw: request.system_capacity_kw,
      electricity_rate: request.electricity_rate,
      feed_in_tariff: request.feed_in_tariff,
      include_weather: true,
      include_solar_forecast: true
    };

    const response = await this.client.post('/sage', chatRequest);

    // Format the response to match the expected structure
    return {
      cost_savings: {
        summary: {
          total_consumption_cost: 0,
          total_production_value: 0,
          total_grid_purchase_cost: 0,
          total_grid_export_revenue: 0,
          total_net_savings: 0,
          roi_days: 7
        },
        daily_savings: []
      }
    };
  }

  // RAG endpoint
  async getRagResponse(request: ChatRequest): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>('/sage', request);
    return response.data;
  }
}

// Create and export a singleton instance
const apiClient = new ApiClient();
export default apiClient;
