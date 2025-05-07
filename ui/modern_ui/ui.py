"""
Modern UI implementation with clean design.
"""
import gradio as gr
import datetime
from typing import List, Tuple, Generator

# Import modules
from ui.config import (
    SERVER_NAME,
    SERVER_PORT,
    APP_TITLE,
    APP_DESCRIPTION,
    MODEL_INFO,
    KNOWLEDGE_INFO
)
from api import get_model_response
from ui.scada import process_csv, create_daily_profile_plot, create_monthly_heatmap, create_performance_summary, format_performance_html
from ui.template_loader import render_template, load_template, load_icon

def respond(message: str, history: List[Tuple[str, str]]) -> Generator[Tuple[str, List[Tuple[str, str]]], None, None]:
    """Process user message and get response from the model."""
    if not message.strip():
        yield "", history
        return

    # Get response from model
    reply = get_model_response(message, history)

    # Update history
    history.append((message, reply))

    yield "", history

def process_scada_data(file_obj):
    """Process SCADA data file and generate visualizations."""
    if file_obj is None:
        return (
            "<div class='error-message'><i class='fas fa-exclamation-circle'></i> Please upload a file first.</div>",
            None,
            None,
            ""
        )

    try:
        # Process the CSV file
        df, status_message = process_csv(file_obj)

        if df is None:
            return (
                f"<div class='error-message'><i class='fas fa-exclamation-circle'></i> {status_message}</div>",
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
            f"<div class='success-message'><i class='fas fa-check-circle'></i> {status_message}</div>",
            daily_plot,
            monthly_plot,
            metrics_html
        )
    except Exception as e:
        # Handle any errors
        error_message = str(e)
        return (
            f"<div class='error-message'><i class='fas fa-exclamation-circle'></i> Error processing file: {error_message}</div>",
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
    """Create the UI with modern design."""
    # Load CSS from file
    css = load_template("css/modern.css")

    # Add critical CSS fixes to ensure content is visible
    css += """
    /* Critical fixes to ensure content is visible */
    .gradio-container {
        display: flex !important;
        flex-direction: column !important;
        min-height: 100vh !important;
    }

    .tabitem {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        height: auto !important;
    }

    .main-content {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* Fix for Gradio's root elements */
    #root, #component-0, #component-1, #component-2, #component-3 {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        height: auto !important;
    }
    """

    with gr.Blocks(css=css) as app:
        # Header with icons
        gr.HTML(render_template("components/modern_header.html", {
            "APP_TITLE": APP_TITLE,
            "APP_DESCRIPTION": APP_DESCRIPTION,
            "MODEL_INFO": MODEL_INFO,
            "SETTINGS_ICON": load_icon("settings"),
            "CPU_ICON": load_icon("cpu")
        }))

        # Use Gradio's native tabs
        with gr.Tabs(elem_id="main-tabs") as tabs:
            # Chat Tab
            with gr.TabItem("Chat", id="chat-tab", elem_id="chat-tab-content"):
                with gr.Row(elem_id="main-content", elem_classes="main-content"):
                    # Sidebar
                    with gr.Column(scale=1, elem_id="sidebar", elem_classes="sidebar"):
                        # Model info and actions with icons
                        gr.HTML(render_template("components/modern_sidebar.html", {
                            "MODEL_INFO": MODEL_INFO,
                            "KNOWLEDGE_INFO": KNOWLEDGE_INFO,
                            "CPU_ICON": load_icon("cpu"),
                            "BOOK_ICON": load_icon("book")
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

                        # Input area with improved styling
                        with gr.Row(elem_classes="chat-input-container"):
                            with gr.Column(scale=5):
                                msg = gr.Textbox(
                                    placeholder="Ask a question about solar...",
                                    elem_id="chat-input",
                                    elem_classes="chat-input",
                                    show_label=False
                                )

                            with gr.Column(scale=1, min_width=100):
                                submit_btn = gr.Button(
                                    "Send",
                                    elem_id="send-btn",
                                    elem_classes="send-btn"
                                )

            # SCADA Upload Tab
            with gr.TabItem("SCADA Upload", id="scada-tab", elem_id="scada-tab-content"):
                with gr.Row(elem_id="main-content", elem_classes="main-content"):
                    # Left sidebar with instructions and uploader
                    with gr.Column(scale=1, elem_id="scada_sidebar"):
                        # Use the Uppy uploader component
                        gr.HTML(render_template("components/modern_uppy.html"))

                        # Hidden file upload component for Gradio backend
                        file_upload = gr.File(
                            label="Upload SCADA CSV",
                            file_types=[".csv", ".xlsx"],
                            type="binary",
                            elem_id="scada-file-upload",
                            elem_classes="scada-file-upload hidden-upload"
                        )

                        # Process button
                        process_btn = gr.Button(
                            "Process Data",
                            variant="primary",
                            elem_id="process_btn"
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

            # Tilt Optimization Tab
            with gr.TabItem("Tilt Optimization", id="tilt-tab", elem_id="tilt-tab-content"):
                with gr.Row(elem_id="main-content", elem_classes="main-content"):
                    with gr.Column(scale=1, elem_id="tilt-sidebar", elem_classes="sidebar"):
                        gr.HTML(render_template("components/modern_tilt.html"))

                        tilt_input = gr.Textbox(
                            label="Tilt Angle (degrees)",
                            placeholder="Enter angle in degrees...",
                            elem_id="tilt-input",
                            elem_classes="tilt-input-field"
                        )

                        tilt_btn = gr.Button(
                            "Calculate Optimal Angle",
                            variant="primary",
                            elem_id="tilt-btn",
                            elem_classes="send-btn"  # Reuse the send button styling
                        )

                    with gr.Column(scale=3, elem_id="tilt-result-column"):
                        tilt_result = gr.Textbox(
                            label="Optimization Result",
                            elem_id="tilt-result",
                            interactive=False
                        )

        # Footer
        gr.HTML(render_template("components/modern_footer.html", {
            "CURRENT_YEAR": datetime.datetime.now().year,
            "APP_TITLE": APP_TITLE
        }))

        # Load JavaScript dependencies and our combined script directly
        gr.HTML("""
        <!-- Include Uppy.js and CSS -->
        <link href="https://releases.transloadit.com/uppy/v3.21.0/uppy.min.css" rel="stylesheet">
        <script src="https://releases.transloadit.com/uppy/v3.21.0/uppy.min.js"></script>
        """)

        # Include the combined script directly
        gr.HTML(f"""
        <script>
        {load_template("js/combined.js")}
        </script>
        """)

        # Add a debug script to check the DOM structure
        gr.HTML("""
        <script>
        // Debug script to check DOM structure
        function debugGradioStructure() {
            console.log('Debugging Gradio structure...');

            // Check for tabs
            const tabs = document.querySelectorAll('.tab-nav');
            console.log(`Found ${tabs.length} tab navs`);

            // Check for tab content
            const tabItems = document.querySelectorAll('.tabitem');
            console.log(`Found ${tabItems.length} tab items`);

            // Make all tab content visible
            tabItems.forEach((item, index) => {
                console.log(`Tab item ${index} display: ${getComputedStyle(item).display}`);
                item.style.display = 'block';
                item.style.visibility = 'visible';
                item.style.opacity = '1';
            });

            // Check for main content
            const mainContent = document.querySelectorAll('.main-content');
            console.log(`Found ${mainContent.length} main content elements`);

            // Make all main content visible
            mainContent.forEach((item, index) => {
                console.log(`Main content ${index} display: ${getComputedStyle(item).display}`);
                item.style.display = 'flex';
                item.style.visibility = 'visible';
                item.style.opacity = '1';
            });
        }

        // Run debug immediately
        debugGradioStructure();

        // Also run after delays
        setTimeout(debugGradioStructure, 1000);
        setTimeout(debugGradioStructure, 2000);
        setTimeout(debugGradioStructure, 3000);
        </script>
        """)

        # Connect the input and button to the chatbot
        submit_btn.click(respond, [msg, chatbot], [msg, chatbot])
        msg.submit(respond, [msg, chatbot], [msg, chatbot])

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
