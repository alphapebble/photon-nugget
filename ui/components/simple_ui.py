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
# Import the API client
from ui.api import get_model_response
# Removed non-conversational components
from ui.utils.template_loader import render_template, load_template, load_icon

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

    # No evaluation notification
    yield "", history, ""

# Removed non-conversational functions

def create_ui() -> gr.Blocks:
    """Create the UI with simple design."""
    # Load CSS from files
    css = load_template("css/simple.css")

    with gr.Blocks(css=css) as app:
        # Header
        gr.HTML(render_template("components/simple_header.html", {
            "APP_TITLE": APP_TITLE,
            "APP_DESCRIPTION": APP_DESCRIPTION,
            "MODEL_INFO": MODEL_INFO,
            "SUN_ICON": load_icon("sun"),
            "CPU_ICON": load_icon("cpu")
        }))

        # Main content
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

        # Removed non-conversational component connections

        return app
