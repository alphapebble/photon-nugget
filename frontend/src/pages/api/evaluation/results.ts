import type { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';

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

interface EvaluationResults {
  summaryMetrics: SummaryMetrics[];
  detailedResults: DetailedResult[];
}

/**
 * Load evaluation results from the specified directory
 */
function loadEvaluationResults(resultsDir: string): EvaluationResults {
  try {
    // Ensure the directory exists
    if (!fs.existsSync(resultsDir)) {
      return { summaryMetrics: [], detailedResults: [] };
    }

    // Find summary metrics files
    const jsonFiles = fs.readdirSync(resultsDir)
      .filter(file => file.startsWith('summary_metrics_') && file.endsWith('.json'))
      .sort()
      .reverse(); // Sort by timestamp (newest first)

    if (jsonFiles.length === 0) {
      return { summaryMetrics: [], detailedResults: [] };
    }

    // Load summary metrics
    const summaryMetrics: SummaryMetrics[] = jsonFiles.map(jsonFile => {
      const filePath = path.join(resultsDir, jsonFile);
      const fileContent = fs.readFileSync(filePath, 'utf-8');
      const metrics = JSON.parse(fileContent);
      
      // Add file name for reference
      metrics.file_name = jsonFile;
      return metrics;
    });

    // Find detailed results files
    const csvFiles = fs.readdirSync(resultsDir)
      .filter(file => file.startsWith('evaluation_results_') && file.endsWith('.csv'))
      .sort()
      .reverse(); // Sort by timestamp (newest first)

    if (csvFiles.length === 0) {
      return { summaryMetrics, detailedResults: [] };
    }

    // Load the latest detailed results
    const latestCsv = csvFiles[0];
    const csvPath = path.join(resultsDir, latestCsv);
    const csvContent = fs.readFileSync(csvPath, 'utf-8');
    
    // Parse CSV content
    const lines = csvContent.split('\n');
    const headers = lines[0].split(',').map(header => header.trim());
    
    const detailedResults: DetailedResult[] = [];
    
    for (let i = 1; i < lines.length; i++) {
      if (!lines[i].trim()) continue;
      
      const values = lines[i].split(',');
      const result: any = {};
      
      headers.forEach((header, index) => {
        let value = values[index] || '';
        
        // Convert boolean strings
        if (value === 'True') value = true;
        if (value === 'False') value = false;
        
        // Convert numeric strings
        if (!isNaN(Number(value)) && value !== '') {
          value = Number(value);
        }
        
        result[header] = value;
      });
      
      detailedResults.push(result as DetailedResult);
    }

    return { summaryMetrics, detailedResults };
  } catch (error) {
    console.error('Error loading evaluation results:', error);
    return { summaryMetrics: [], detailedResults: [] };
  }
}

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<EvaluationResults>
) {
  // Get the results directory from the query parameters
  const resultsDir = req.query.dir as string || 'evaluation/results';
  
  // Load evaluation results
  const results = loadEvaluationResults(resultsDir);
  
  // Return the results
  res.status(200).json(results);
}
