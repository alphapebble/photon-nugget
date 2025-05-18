import type { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

/**
 * API route that proxies all requests to the FastAPI backend.
 * This allows us to avoid CORS issues and keep the API URL consistent.
 */
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  try {
    // Get the path from the request
    const { path } = req.query;
    
    // Build the target URL
    const apiUrl = process.env.API_URL || 'http://localhost:8000';
    const targetUrl = `${apiUrl}/${Array.isArray(path) ? path.join('/') : path}`;
    
    // Forward the request to the FastAPI backend
    const response = await axios({
      method: req.method,
      url: targetUrl,
      data: req.body,
      headers: {
        'Content-Type': 'application/json',
        // Forward other headers as needed
        ...req.headers,
        // Remove headers that would cause issues
        host: undefined,
        connection: undefined,
      },
      validateStatus: () => true, // Don't throw on non-2xx responses
    });
    
    // Set the response status code
    res.status(response.status);
    
    // Set response headers
    Object.entries(response.headers).forEach(([key, value]) => {
      if (value !== undefined) {
        res.setHeader(key, value as string);
      }
    });
    
    // Send the response data
    res.json(response.data);
  } catch (error) {
    console.error('API proxy error:', error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
}
