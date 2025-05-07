"""
SCADA data processing and visualization functions.
"""
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from typing import Tuple, List, Dict, Any, Optional
from datetime import datetime, timedelta

from ui.config import logger

def process_csv(file_obj) -> Tuple[pd.DataFrame, str]:
    """
    Process a CSV file containing SCADA data.
    
    Args:
        file_obj: File object from Gradio upload
        
    Returns:
        Tuple containing processed DataFrame and status message
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_obj)
        
        # Basic validation
        required_columns = ['timestamp']
        for col in required_columns:
            if col not in df.columns:
                return None, f"Error: Missing required column '{col}'"
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        # Drop rows with invalid timestamps
        invalid_timestamps = df['timestamp'].isna().sum()
        if invalid_timestamps > 0:
            df = df.dropna(subset=['timestamp'])
            logger.warning(f"Dropped {invalid_timestamps} rows with invalid timestamps")
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Check if we have power data
        power_columns = [col for col in df.columns if 'power' in col.lower()]
        if not power_columns:
            return None, "Error: No power data found in the file"
        
        # Use the first power column as the main power column
        if 'power' not in df.columns:
            df['power'] = df[power_columns[0]]
        
        return df, f"Successfully processed file with {len(df)} rows"
    
    except Exception as e:
        logger.error(f"Error processing CSV file: {str(e)}")
        return None, f"Error processing file: {str(e)}"

def create_daily_profile_plot(df: pd.DataFrame) -> go.Figure:
    """
    Create a daily power profile plot using Plotly.
    
    Args:
        df: DataFrame containing timestamp and power data
        
    Returns:
        Plotly figure object
    """
    # Extract hour from timestamp
    df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute / 60
    
    # Group by hour and calculate mean, min, max
    hourly = df.groupby('hour')['power'].agg(['mean', 'min', 'max']).reset_index()
    
    # Create figure
    fig = go.Figure()
    
    # Add mean line
    fig.add_trace(go.Scatter(
        x=hourly['hour'],
        y=hourly['mean'],
        mode='lines',
        name='Average Power',
        line=dict(color='blue', width=2)
    ))
    
    # Add min/max range
    fig.add_trace(go.Scatter(
        x=hourly['hour'],
        y=hourly['max'],
        mode='lines',
        name='Max Power',
        line=dict(color='rgba(0,0,255,0.2)', width=0)
    ))
    
    fig.add_trace(go.Scatter(
        x=hourly['hour'],
        y=hourly['min'],
        mode='lines',
        name='Min Power',
        line=dict(color='rgba(0,0,255,0.2)', width=0),
        fill='tonexty'
    ))
    
    # Update layout
    fig.update_layout(
        title='Daily Power Profile',
        xaxis_title='Hour of Day',
        yaxis_title='Power (kW)',
        template='plotly_white',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    return fig

def create_monthly_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Create a monthly power heatmap using Plotly.
    
    Args:
        df: DataFrame containing timestamp and power data
        
    Returns:
        Plotly figure object
    """
    # Extract date and hour
    df['date'] = df['timestamp'].dt.date
    df['hour'] = df['timestamp'].dt.hour
    
    # Group by date and hour, calculate mean power
    heatmap_data = df.groupby(['date', 'hour'])['power'].mean().reset_index()
    
    # Pivot the data for the heatmap
    pivot_data = heatmap_data.pivot(index='date', columns='hour', values='power')
    
    # Create the heatmap
    fig = px.imshow(
        pivot_data,
        labels=dict(x='Hour of Day', y='Date', color='Power (kW)'),
        x=pivot_data.columns,
        y=pivot_data.index,
        color_continuous_scale='Viridis'
    )
    
    # Update layout
    fig.update_layout(
        title='Power Output Heatmap',
        xaxis_title='Hour of Day',
        yaxis_title='Date',
        template='plotly_white'
    )
    
    return fig

def create_performance_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Create a performance summary from SCADA data.
    
    Args:
        df: DataFrame containing timestamp and power data
        
    Returns:
        Dictionary with performance metrics
    """
    # Calculate daily energy production
    df['date'] = df['timestamp'].dt.date
    daily_energy = df.groupby('date')['power'].mean() * 24  # Simplified calculation
    
    # Calculate performance metrics
    metrics = {
        'total_days': len(daily_energy),
        'avg_daily_energy': daily_energy.mean(),
        'max_daily_energy': daily_energy.max(),
        'min_daily_energy': daily_energy.min(),
        'total_energy': daily_energy.sum(),
        'max_power': df['power'].max(),
        'avg_power': df['power'].mean()
    }
    
    return metrics

def format_performance_html(metrics: Dict[str, Any]) -> str:
    """
    Format performance metrics as HTML.
    
    Args:
        metrics: Dictionary with performance metrics
        
    Returns:
        HTML string with formatted metrics
    """
    html = """
    <div class="performance-summary">
        <h3>Performance Summary</h3>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{total_energy:.1f} kWh</div>
                <div class="metric-label">Total Energy</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{avg_daily_energy:.1f} kWh</div>
                <div class="metric-label">Avg. Daily Energy</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{max_power:.1f} kW</div>
                <div class="metric-label">Peak Power</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{total_days}</div>
                <div class="metric-label">Days Analyzed</div>
            </div>
        </div>
    </div>
    """.format(**metrics)
    
    return html
