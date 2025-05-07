"""
Weather dashboard UI components for Solar Sage.
"""

import gradio as gr
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional

from agents.weather_integration import (
    get_weather_for_location,
    estimate_production_impact,
    generate_weather_insights
)

def create_weather_forecast_plot(forecast_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a weather forecast plot using Plotly.
    
    Args:
        forecast_data: List of daily forecast data
        
    Returns:
        Plotly figure object
    """
    # Convert to DataFrame for easier plotting
    df = pd.DataFrame(forecast_data)
    
    # Create figure
    fig = go.Figure()
    
    # Add production factor line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['production_factor'] * 100,
        mode='lines+markers',
        name='Production Efficiency (%)',
        line=dict(color='#f39c12', width=3),
        marker=dict(size=8)
    ))
    
    # Add expected kWh line on secondary y-axis
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['expected_kwh'],
        mode='lines+markers',
        name='Expected Energy (kWh)',
        line=dict(color='#3498db', width=3),
        marker=dict(size=8),
        yaxis='y2'
    ))
    
    # Add cloud cover as area chart
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['clouds'],
        mode='none',
        name='Cloud Cover (%)',
        fill='tozeroy',
        fillcolor='rgba(189, 195, 199, 0.5)'
    ))
    
    # Update layout with dual y-axes
    fig.update_layout(
        title='7-Day Solar Production Forecast',
        xaxis_title='Date',
        yaxis=dict(
            title='Production Efficiency (%) / Cloud Cover (%)',
            titlefont=dict(color='#f39c12'),
            tickfont=dict(color='#f39c12')
        ),
        yaxis2=dict(
            title='Expected Energy (kWh)',
            titlefont=dict(color='#3498db'),
            tickfont=dict(color='#3498db'),
            anchor='x',
            overlaying='y',
            side='right'
        ),
        template='plotly_white',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=500
    )
    
    return fig

def create_current_conditions_card(current_data: Dict[str, Any]) -> str:
    """
    Create an HTML card for current weather conditions.
    
    Args:
        current_data: Current weather and production data
        
    Returns:
        HTML string for the card
    """
    # Format production factor as percentage
    production_pct = current_data['production_factor'] * 100
    
    # Determine color based on production factor
    if production_pct < 30:
        color_class = "poor"
    elif production_pct < 70:
        color_class = "moderate"
    else:
        color_class = "good"
    
    html = f"""
    <div class="weather-card current-conditions">
        <h3>Current Solar Conditions</h3>
        <div class="weather-info">
            <div class="weather-main">
                <div class="weather-icon {current_data['weather'].lower().replace(' ', '-')}"></div>
                <div class="weather-description">{current_data['weather']}</div>
            </div>
            <div class="weather-details">
                <div class="weather-detail">
                    <span class="detail-label">Temperature:</span>
                    <span class="detail-value">{current_data['temp']}°C</span>
                </div>
                <div class="weather-detail">
                    <span class="detail-label">Cloud Cover:</span>
                    <span class="detail-value">{current_data['clouds']}%</span>
                </div>
                <div class="weather-detail">
                    <span class="detail-label">Est. Irradiance:</span>
                    <span class="detail-value">{current_data['irradiance_estimate']:.1f} W/m²</span>
                </div>
            </div>
        </div>
        <div class="production-meter">
            <div class="production-label">Current Production Efficiency</div>
            <div class="meter-container">
                <div class="meter-bar {color_class}" style="width: {min(100, production_pct)}%;"></div>
                <div class="meter-value">{production_pct:.1f}%</div>
            </div>
        </div>
        <div class="expected-energy">
            <span class="energy-label">Expected Energy This Hour:</span>
            <span class="energy-value">{current_data['expected_kwh']:.2f} kWh</span>
        </div>
    </div>
    """
    
    return html

def create_insights_card(insights: Dict[str, Any]) -> str:
    """
    Create an HTML card for weather insights.
    
    Args:
        insights: Weather insights data
        
    Returns:
        HTML string for the card
    """
    # Build maintenance insights HTML
    maintenance_html = ""
    if insights['maintenance_insights']:
        maintenance_html = "<h4>Maintenance Insights</h4><ul>"
        for insight in insights['maintenance_insights']:
            maintenance_html += f"<li>{insight}</li>"
        maintenance_html += "</ul>"
    
    html = f"""
    <div class="weather-card insights-card">
        <h3>Solar Production Insights</h3>
        <div class="insight-section">
            <h4>Current Conditions</h4>
            <p>{insights['current_conditions']}</p>
        </div>
        <div class="insight-section">
            <h4>Weekly Potential</h4>
            <p>{insights['weekly_potential']}</p>
            <p>{insights['best_production_day']}</p>
        </div>
        {maintenance_html}
    </div>
    """
    
    return html

def process_location_input(location_input: str) -> Tuple[Optional[float], Optional[float], str]:
    """
    Process location input and return coordinates.
    
    Args:
        location_input: Location string (format: "latitude,longitude")
        
    Returns:
        Tuple of (latitude, longitude, status_message)
    """
    try:
        # Split input by comma
        parts = location_input.strip().split(',')
        if len(parts) != 2:
            return None, None, "Invalid format. Please enter as 'latitude,longitude'"
        
        # Parse coordinates
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
        
        # Validate coordinates
        if lat < -90 or lat > 90:
            return None, None, "Latitude must be between -90 and 90"
        if lon < -180 or lon > 180:
            return None, None, "Longitude must be between -180 and 180"
        
        return lat, lon, "Location set successfully"
    except ValueError:
        return None, None, "Invalid coordinates. Please enter numeric values."

def update_weather_dashboard(location_input: str) -> Tuple[str, Optional[go.Figure], str]:
    """
    Update the weather dashboard based on location input.
    
    Args:
        location_input: Location string (format: "latitude,longitude")
        
    Returns:
        Tuple of (current_conditions_html, forecast_plot, insights_html)
    """
    # Process location input
    lat, lon, status_message = process_location_input(location_input)
    
    if lat is None or lon is None:
        return (
            f"<div class='error-message'>{status_message}</div>",
            None,
            ""
        )
    
    try:
        # Fetch weather data
        weather_data = get_weather_for_location(lat, lon)
        
        # Calculate production impact
        impact = estimate_production_impact(weather_data)
        
        # Generate insights
        insights = generate_weather_insights(impact)
        
        # Create UI components
        current_conditions_html = create_current_conditions_card(impact['current'])
        forecast_plot = create_weather_forecast_plot(impact['daily_forecast'])
        insights_html = create_insights_card(insights)
        
        return (
            current_conditions_html,
            forecast_plot,
            insights_html
        )
    except Exception as e:
        error_message = str(e)
        return (
            f"<div class='error-message'>Error fetching weather data: {error_message}</div>",
            None,
            ""
        )

def create_weather_dashboard_ui() -> List[gr.Component]:
    """
    Create weather dashboard UI components.
    
    Returns:
        List of Gradio components
    """
    # Location input
    location_input = gr.Textbox(
        label="Location (latitude,longitude)",
        placeholder="37.7749,-122.4194",
        elem_id="location-input"
    )
    
    # Update button
    update_btn = gr.Button(
        "Update Weather Data",
        elem_id="update-weather-btn"
    )
    
    # Current conditions card
    current_conditions = gr.HTML(
        "",
        elem_id="current-conditions"
    )
    
    # Forecast plot
    forecast_plot = gr.Plot(
        label="7-Day Solar Production Forecast",
        elem_id="forecast-plot"
    )
    
    # Insights card
    insights_card = gr.HTML(
        "",
        elem_id="insights-card"
    )
    
    # Connect components
    update_btn.click(
        fn=update_weather_dashboard,
        inputs=[location_input],
        outputs=[current_conditions, forecast_plot, insights_card]
    )
    
    return [location_input, update_btn, current_conditions, forecast_plot, insights_card]
