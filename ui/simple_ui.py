"""
Simple UI implementation with clean design.
"""
import gradio as gr
import datetime
from typing import List, Tuple, Generator

# Import modules
from ui.config import (
    APP_TITLE,
    APP_DESCRIPTION,
    MODEL_INFO,
    KNOWLEDGE_INFO,
    GITHUB_LINK
)
try:
    from api import get_model_response
except ImportError:
    # Try to import from the src directory
    from ui.api import get_model_response
from ui.scada import process_csv, create_daily_profile_plot, create_monthly_heatmap, create_performance_summary, format_performance_html
from ui.weather_dashboard import create_weather_dashboard_ui, update_weather_dashboard
from ui.template_loader import render_template, load_template, load_icon

def respond(message: str, history: List[Tuple[str, str]], location_input: str = None, notification_html: gr.HTML = None) -> Generator[Tuple[str, List[Tuple[str, str]], str], None, None]:
    """Process user message and get response from the model."""
    if not message.strip():
        yield "", history, ""
        return

    # Process location if provided
    lat, lon = None, None
    if location_input:
        try:
            parts = location_input.strip().split(',')
            if len(parts) == 2:
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
        except ValueError:
            pass  # Invalid location format, ignore

    # Get response from model with weather context if location is provided
    try:
        reply = get_model_response(message, history, lat, lon)
    except Exception as e:
        # Handle API connection errors gracefully
        error_message = str(e)
        if "Connection refused" in error_message:
            reply = "⚠️ I'm sorry, but I can't connect to the API server right now. Please make sure the API server is running by executing `./start_solar_sage.sh --api-only` in a separate terminal."
        else:
            reply = f"⚠️ I'm sorry, but an error occurred: {error_message}"

    # Update history
    history.append((message, reply))

    # Show evaluation notification
    eval_notification = """
    <div class="eval-notification">
        <span class="eval-icon">📊</span>
        <span>Want to see how well the system is performing? Check out the
        <a href="/?mode=evaluation" class="eval-link">Evaluation Dashboard</a>
        </span>
    </div>
    """

    yield "", history, eval_notification

def process_scada_data(file_obj):
    """Process SCADA data file and generate visualizations."""
    if file_obj is None:
        return (
            "<div class='error-message'>Please upload a file first.</div>",
            None,
            None,
            ""
        )

    try:
        # Process the CSV file
        df, status_message = process_csv(file_obj)

        if df is None:
            return (
                f"<div class='error-message'>{status_message}</div>",
                None,
                None,
                ""
            )

        # Create visualizations
        daily_plot = create_daily_profile_plot(df)
        monthly_plot = create_monthly_heatmap(df)

        # Calculate performance metrics
        metrics = create_performance_summary(df)
        metrics_html = format_performance_html(metrics)

        return (
            f"<div class='success-message'>{status_message}</div>",
            daily_plot,
            monthly_plot,
            metrics_html
        )
    except Exception as e:
        # Handle any errors
        error_message = str(e)
        return (
            f"<div class='error-message'>Error processing file: {error_message}</div>",
            None,
            None,
            ""
        )

def calculate_tilt(angle_input):
    """Calculate optimal tilt angle for solar panels."""
    try:
        angle = float(angle_input)
        if angle < 0 or angle > 90:
            return "Please enter a valid angle between 0 and 90 degrees."

        # Simple calculation for demonstration
        optimal_angle = angle
        clockwise_angle = optimal_angle
        anti_clockwise_angle = 360 - optimal_angle if optimal_angle > 0 else 0

        return f"{clockwise_angle} degrees clockwise ({anti_clockwise_angle} degrees anti-clockwise)"
    except ValueError:
        return "Please enter a valid number for the angle."
    except Exception as e:
        return f"Error: {str(e)}"

def create_ui() -> gr.Blocks:
    """Create the UI with simple design."""
    # Load CSS from files
    css = load_template("css/simple.css")
    weather_css = load_template("css/weather_dashboard.css")
    css = css + "\n" + weather_css

    with gr.Blocks(css=css) as app:
        # Header
        gr.HTML(render_template("components/simple_header.html", {
            "APP_TITLE": APP_TITLE,
            "APP_DESCRIPTION": APP_DESCRIPTION,
            "MODEL_INFO": MODEL_INFO,
            "SUN_ICON": load_icon("sun"),
            "CPU_ICON": load_icon("cpu")
        }))

        # Main content with tabs
        with gr.Tabs(elem_id="main-tabs"):
            # Chat Tab
            with gr.TabItem("Chat", elem_id="chat-tab-content"):
                with gr.Row(elem_id="main-content", elem_classes="main-content"):
                    # Sidebar
                    with gr.Column(scale=1, elem_id="sidebar", elem_classes="sidebar"):
                        # Model info and actions
                        gr.HTML(render_template("components/simple_sidebar.html", {
                            "MODEL_INFO": MODEL_INFO,
                            "KNOWLEDGE_INFO": KNOWLEDGE_INFO,
                            "CPU_ICON": load_icon("cpu"),
                            "BOOK_ICON": load_icon("book"),
                            "TRASH_ICON": load_icon("trash"),
                            "SAVE_ICON": load_icon("save"),
                            "DOWNLOAD_ICON": load_icon("download")
                        }))

                    # Chat area
                    with gr.Column(scale=3, elem_id="chat-area", elem_classes="chat-area"):
                        # Chat messages
                        chatbot = gr.Chatbot(
                            value=[
                                [None, "Hello! How can I help you with your solar questions today?"]
                            ],
                            elem_id="chatbot",
                            height=400,
                            show_label=False
                        )

                        # Evaluation notification area
                        notification_html = gr.HTML(
                            "",
                            elem_id="eval-notification-area"
                        )

                        # Weather location input (hidden by default, toggled by JavaScript)
                        with gr.Row(elem_id="weather-location-container", visible=False):
                            chat_location_input = gr.Textbox(
                                label="Your Location (latitude,longitude)",
                                placeholder="37.7749,-122.4194",
                                elem_id="chat-location-input",
                                elem_classes="location-input"
                            )

                            location_toggle = gr.Checkbox(
                                label="Include weather data",
                                elem_id="location-toggle",
                                value=False
                            )

                        # Input area with improved styling
                        with gr.Row(elem_classes="chat-input-container"):
                            with gr.Column(scale=5):
                                msg = gr.Textbox(
                                    placeholder="Ask a question about solar...",
                                    elem_id="msg",
                                    elem_classes="chat-input",
                                    show_label=False
                                )

                            with gr.Column(scale=1, min_width=100):
                                submit_btn = gr.Button(
                                    "Send",
                                    elem_id="send-btn",
                                    elem_classes="button-primary",
                                    variant="primary",
                                    scale=1,
                                    min_width=100,
                                    size="lg"
                                )

            # SCADA Upload Tab
            with gr.TabItem("SCADA Upload", elem_id="scada-tab-content"):
                with gr.Row(elem_id="main-content", elem_classes="main-content"):
                    # Left sidebar with instructions and uploader
                    with gr.Column(scale=1, elem_id="scada_sidebar"):
                        gr.HTML("""
                        <div class="scada-container">
                            <div class="scada-header">
                                <h3>SCADA Data Upload</h3>
                                <p>Upload your SCADA data files to visualize and analyze solar performance metrics.</p>
                            </div>

                            <div class="upload-instructions">
                                <h4>Supported File Formats</h4>
                                <ul>
                                    <li>CSV files with timestamp and power data</li>
                                    <li>Excel files with solar metrics</li>
                                </ul>
                                <p>Files should contain columns for timestamp, power output, irradiance, and temperature (optional).</p>
                            </div>
                        </div>
                        """)

                        # File upload component
                        file_upload = gr.File(
                            label="Upload SCADA CSV",
                            file_types=[".csv", ".xlsx"],
                            type="binary",
                            elem_id="scada-file-upload"
                        )

                        # Process button
                        process_btn = gr.Button(
                            "Process Data",
                            elem_id="process_btn",
                            elem_classes="button-primary"
                        )

                        # Status indicator
                        scada_status = gr.Markdown("", elem_id="scada_status")

                    # Main visualization area
                    with gr.Column(scale=3, elem_id="scada_viz_column"):
                        with gr.Group(elem_id="scada_viz_card"):
                            # Tabs for different visualizations
                            with gr.Tabs(elem_id="viz_tabs"):
                                with gr.TabItem("Daily Profile"):
                                    daily_profile_plot = gr.Plot(
                                        label="Daily Power Profile",
                                        elem_id="daily-plot"
                                    )

                                with gr.TabItem("Monthly Heatmap"):
                                    monthly_heatmap_plot = gr.Plot(
                                        label="Power Output Heatmap",
                                        elem_id="monthly-plot"
                                    )

                            # Performance metrics
                            performance_metrics = gr.HTML("", elem_id="performance_metrics")

            # Weather Dashboard Tab
            with gr.TabItem("Weather Dashboard", elem_id="weather-dashboard-tab-content"):
                with gr.Row(elem_id="main-content", elem_classes="main-content"):
                    # Location input and update button
                    with gr.Row(elem_classes="location-container"):
                        location_input, update_btn, current_conditions, forecast_plot, insights_card = create_weather_dashboard_ui()

                    # Weather visualization grid
                    with gr.Row(elem_classes="weather-grid"):
                        with gr.Column():
                            gr.HTML(elem_id="current-conditions-container")

                        with gr.Column():
                            gr.HTML(elem_id="insights-container")

                    with gr.Row():
                        gr.HTML(elem_id="forecast-container")

            # Tilt Optimization Tab
            with gr.TabItem("Tilt Optimization", elem_id="tilt-tab-content"):
                with gr.Row(elem_id="main-content", elem_classes="main-content"):
                    with gr.Column(scale=1, elem_id="tilt-sidebar", elem_classes="sidebar"):
                        gr.HTML("""
                        <div class="tilt-container">
                            <h3>Tilt Angle Optimization</h3>
                            <p>Calculate the optimal tilt angle for your solar panels based on your location.</p>

                            <div class="upload-instructions">
                                <h4>How it works</h4>
                                <p>Enter the angle in degrees and click Calculate to get the optimal orientation.</p>
                            </div>
                        </div>
                        """)

                        tilt_input = gr.Textbox(
                            label="Tilt Angle (degrees)",
                            placeholder="Enter angle in degrees...",
                            elem_id="tilt-input",
                            elem_classes="tilt-input-field"
                        )

                        tilt_btn = gr.Button(
                            "Calculate Optimal Angle",
                            elem_id="tilt-btn",
                            elem_classes="button-primary"
                        )

                    with gr.Column(scale=3, elem_id="tilt-result-column"):
                        tilt_result = gr.Textbox(
                            label="Optimization Result",
                            elem_id="tilt-result",
                            interactive=False
                        )

        # Footer with evaluation dashboard link
        gr.HTML(render_template("components/simple_footer.html", {
            "CURRENT_YEAR": datetime.datetime.now().year,
            "APP_TITLE": APP_TITLE,
            "GITHUB_LINK": GITHUB_LINK
        }))

        # Load JavaScript
        gr.HTML(f"""
        <script src="https://releases.transloadit.com/uppy/v3.21.0/uppy.min.js"></script>
        <script>
        {load_template("js/simple.js")}
        </script>
        """)

        # Add direct style fix for Send button
        gr.HTML("""
        <!-- Direct style fixes -->
        <style>
        #send-btn button,
        button#send-btn,
        div[id^="component"] #send-btn button,
        .gradio-container #send-btn button {
            background-color: #1565c0 !important;
            color: white !important;
        }

        .footer-link {
            display: inline-block;
            margin-top: 10px;
            padding: 5px 10px;
            background-color: #1565c0;
            color: white !important;
            text-decoration: none;
            border-radius: 4px;
            font-weight: 500;
            transition: background-color 0.3s;
        }

        .footer-link:hover {
            background-color: #0d47a1;
        }
        </style>

        <!-- Inline script to fix Send button -->
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Fix for Send button
            function fixSendButton() {
                const sendBtn = document.querySelector('#send-btn button');
                if (sendBtn) {
                    sendBtn.style.backgroundColor = '#1565c0';
                    sendBtn.style.color = 'white';
                    console.log('Fixed Send button via inline script');
                } else {
                    setTimeout(fixSendButton, 500);
                }
            }

            // Run immediately and after a delay
            fixSendButton();
            setTimeout(fixSendButton, 1000);
            setTimeout(fixSendButton, 2000);
        });
        </script>
        """)

        # Connect the input and button to the chatbot
        submit_btn.click(respond, [msg, chatbot, chat_location_input], [msg, chatbot, notification_html])
        msg.submit(respond, [msg, chatbot, chat_location_input], [msg, chatbot, notification_html])

        # Add JavaScript to toggle weather location input visibility
        gr.HTML("""
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Add weather toggle button to the chat interface
            const chatInputContainer = document.querySelector('.chat-input-container');
            if (chatInputContainer) {
                const toggleBtn = document.createElement('button');
                toggleBtn.innerHTML = '🌤️';
                toggleBtn.className = 'weather-toggle-btn';
                toggleBtn.title = 'Toggle weather data';
                toggleBtn.onclick = function(e) {
                    e.preventDefault();
                    const container = document.getElementById('weather-location-container');
                    if (container) {
                        container.style.display = container.style.display === 'none' ? 'flex' : 'none';
                    }
                };
                chatInputContainer.appendChild(toggleBtn);
            }

            // Initialize weather location container as hidden
            const weatherContainer = document.getElementById('weather-location-container');
            if (weatherContainer) {
                weatherContainer.style.display = 'none';
            }
        });
        </script>
        <style>
        .weather-toggle-btn {
            position: absolute;
            right: 120px;
            bottom: 10px;
            background: transparent;
            border: none;
            font-size: 20px;
            cursor: pointer;
            z-index: 100;
        }
        #weather-location-container {
            padding: 10px;
            background: var(--bg-secondary);
            border-radius: 8px;
            margin-bottom: 10px;
        }
        </style>
        """)

        # Connect SCADA processing function to UI
        process_btn.click(
            fn=process_scada_data,
            inputs=[file_upload],
            outputs=[scada_status, daily_profile_plot, monthly_heatmap_plot, performance_metrics]
        )

        # Connect tilt optimization function to UI
        tilt_btn.click(
            fn=calculate_tilt,
            inputs=[tilt_input],
            outputs=[tilt_result]
        )

        return app
