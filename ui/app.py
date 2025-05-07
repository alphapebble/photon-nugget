"""
Main UI application for the Photon-Nugget Solar AI Assistant.
"""
import gradio as gr
from typing import List, Tuple, Generator

# Import modules
from ui.config import (
    SERVER_NAME,
    CHATBOT_HEIGHT,
    APP_TITLE,
    APP_DESCRIPTION,
    MODEL_INFO,
    KNOWLEDGE_INFO,
    GITHUB_LINK
)
from ui.api import ask_model
from ui.theme import js_functions, css_styles, toggle_theme
from ui.history import (
    clear_chat,
    save_chat_history,
    load_chat_history_from_storage
)


def respond(message: str, history: List[Tuple[str, str]]) -> Generator[Tuple[str, List[Tuple[str, str]], str, int, str], None, None]:
    """
    Process user message and get response from the model.

    Args:
        message: User's input message
        history: Current chat history

    Returns:
        Generator yielding tuples containing: empty string (to clear input), updated history, status message,
        response index, and feedback header content
    """
    if not message.strip():
        yield "", history, "<div class='error-message'><i class='fas fa-exclamation-circle'></i> Please enter a question.</div>", -1, ""
        return

    # Show thinking status with a more professional look
    yield "", history, "<div class='thinking-indicator'><div class='thinking-dots'><span></span><span></span><span></span></div><div class='thinking-text'>Thinking...</div></div>", -1, ""

    # Get response from model
    reply = ask_model(message, history)

    # Update history and clear status
    history.append((message, reply))
    response_idx = len(history) - 1

    # Return updated state and show feedback components
    # Use "### Was this response helpful?" for feedback_header to make it visible
    yield "", history, "", response_idx, "### Was this response helpful?"


def create_ui() -> gr.Blocks:
    """
    Create the Gradio UI interface.

    Returns:
        Gradio Blocks interface
    """
    with gr.Blocks(theme=gr.themes.Soft()) as app:
        # Add JavaScript for client-side functionality
        gr.HTML(f"""
        <script>
        {js_functions}
        </script>
        """)

        # State variables for theme and feedback
        theme_state = gr.State("light")
        current_response_index = gr.State(-1)

        # Header with app info and theme toggle
        with gr.Row(equal_height=True):
            with gr.Column():
                # Modern header with logo and title
                gr.HTML(f"""
                <div class="app-header">
                    <div class="app-logo"><i class="fas fa-sun"></i></div>
                    <div>
                        <h2 class="app-title">{APP_TITLE}</h2>
                        <p class="app-description">{APP_DESCRIPTION}</p>
                    </div>
                </div>
                """)

            # Theme toggle button with icon
            theme_btn = gr.Button(
                "Toggle Theme",
                elem_id="theme_toggle",
                variant="secondary",
                size="sm"
            )

        # Create tabs using Gradio's Tabs component
        with gr.Tabs():
            # Chat Tab
            with gr.Tab("Chat"):
                # Add icon to tab via JavaScript
                gr.HTML("""
                <script>
                document.addEventListener('DOMContentLoaded', function() {
                    // Add icon to Chat tab
                    const tabLabels = document.querySelectorAll('.tabs > .tab-nav > button');
                    if (tabLabels.length > 0) {
                        tabLabels[0].innerHTML = '<i class="fas fa-comments"></i> ' + tabLabels[0].innerHTML;
                        if (tabLabels.length > 1) {
                            tabLabels[1].innerHTML = '<i class="fas fa-upload"></i> ' + tabLabels[1].innerHTML;
                        }
                        if (tabLabels.length > 2) {
                            tabLabels[2].innerHTML = '<i class="fas fa-sliders"></i> ' + tabLabels[2].innerHTML;
                        }
                    }
                });
                </script>
                """)

                with gr.Row():
                    # Sidebar with info and controls
                    with gr.Column(scale=1, elem_id="sidebar"):
                        # Info card
                        with gr.Group(elem_id="info_card"):
                            gr.HTML(f"""
                            <h3 class="card-title">Information</h3>
                            <div class="info-item">
                                <i class="fas fa-microchip"></i>
                                <span>Model: {MODEL_INFO}</span>
                            </div>
                            <div class="info-item">
                                <i class="fas fa-brain"></i>
                                <span>Knowledge: {KNOWLEDGE_INFO}</span>
                            </div>
                            <div class="info-item">
                                <i class="fas fa-github"></i>
                                <a href="{GITHUB_LINK}" target="_blank">GitHub</a>
                            </div>
                            """)

                        # Controls card
                        with gr.Group(elem_id="controls_card"):
                            gr.HTML("""<h3 class="card-title">Conversation</h3>""")

                            clear_btn = gr.Button(
                                "Clear Chat",
                                elem_id="clear_btn",
                                variant="secondary",
                                size="sm"
                            )

                            save_btn = gr.Button(
                                "Save History",
                                elem_id="save_btn",
                                variant="secondary",
                                size="sm"
                            )

                            load_btn = gr.Button(
                                "Load History",
                                elem_id="load_btn",
                                variant="secondary",
                                size="sm"
                            )

                            # Add icons to buttons via JavaScript
                            gr.HTML("""
                            <script>
                            document.addEventListener('DOMContentLoaded', function() {
                                // Add icons to buttons
                                const clearBtn = document.getElementById('clear_btn');
                                const saveBtn = document.getElementById('save_btn');
                                const loadBtn = document.getElementById('load_btn');

                                if (clearBtn) {
                                    clearBtn.innerHTML = '<i class="fas fa-broom"></i> ' + clearBtn.innerHTML;
                                }

                                if (saveBtn) {
                                    saveBtn.innerHTML = '<i class="fas fa-save"></i> ' + saveBtn.innerHTML;
                                }

                                if (loadBtn) {
                                    loadBtn.innerHTML = '<i class="fas fa-folder-open"></i> ' + loadBtn.innerHTML;
                                }
                            });
                            </script>
                            """)

                    # Main chat interface
                    with gr.Column(scale=3, elem_id="chat_column"):
                        with gr.Group(elem_id="chat_card"):
                            # Chatbot component
                            chatbot = gr.Chatbot(
                                label="Solar Assistant",
                                height=CHATBOT_HEIGHT,
                                elem_id="chatbot"
                            )

                            # Status indicator
                            status_indicator = gr.Markdown("", elem_id="status_indicator")

                            # Feedback section
                            with gr.Column(elem_id="feedback_container", visible=False):
                                feedback_header = gr.Markdown("", elem_id="feedback_header")
                                # Use HTML for the buttons and status to avoid component issues
                                gr.HTML("""
                                <div id="feedback_buttons_container">
                                    <button id="thumbs_up" class="feedback-btn">
                                        <i class="fas fa-thumbs-up"></i> Yes
                                    </button>
                                    <button id="thumbs_down" class="feedback-btn">
                                        <i class="fas fa-thumbs-down"></i> No
                                    </button>
                                </div>
                                <div id="feedback_status"></div>
                                """)

                            # Input area
                            with gr.Row(elem_id="input_row"):
                                user_input = gr.Textbox(
                                    placeholder="Ask a question about solar...",
                                    show_label=False,
                                    container=False,
                                    scale=20,
                                    elem_id="user_input"
                                )
                                send_btn = gr.Button(
                                    "Send",
                                    variant="primary",
                                    scale=1,
                                    elem_id="send_btn"
                                )

            # SCADA Upload Tab (Placeholder)
            with gr.Tab("SCADA Upload"):
                gr.HTML("""
                <div class="placeholder-container">
                    <i class="fas fa-upload placeholder-icon"></i>
                    <h3>SCADA Data Upload</h3>
                    <p>This feature will allow you to upload SCADA data for analysis.</p>
                    <p class="coming-soon">Coming Soon</p>
                </div>
                """)

            # Tilt Optimization Tab (Placeholder)
            with gr.Tab("Tilt Optimization"):
                gr.HTML("""
                <div class="placeholder-container">
                    <i class="fas fa-sliders placeholder-icon"></i>
                    <h3>Solar Panel Tilt Optimization</h3>
                    <p>This feature will help you calculate the optimal tilt angle for your solar panels.</p>
                    <p class="coming-soon">Coming Soon</p>
                </div>
                """)

        # Connect UI components to functions

        # Message sending
        send_btn.click(
            fn=respond,
            inputs=[user_input, chatbot],
            outputs=[user_input, chatbot, status_indicator, current_response_index, feedback_header],
            api_name="chat"
        )

        # Also trigger on Enter key
        user_input.submit(
            fn=respond,
            inputs=[user_input, chatbot],
            outputs=[user_input, chatbot, status_indicator, current_response_index, feedback_header]
        )

        # Theme toggle - using a normal function since _js is not supported
        theme_btn.click(
            fn=toggle_theme,
            inputs=[theme_state],
            outputs=[theme_state]
        )

        # History management with improved feedback
        def clear_chat_and_feedback():
            # Clear chat and hide feedback components
            chat_result, _, idx, _ = clear_chat()
            # Return empty string for feedback header to hide it
            return chat_result, "<div class='success-message'><i class='fas fa-check-circle'></i> Chat cleared successfully!</div>", idx, ""

        def save_history_with_feedback(history):
            if not history:
                return "<div class='warning-message'><i class='fas fa-exclamation-triangle'></i> No messages to save. Try asking a question first!</div>"
            result = save_chat_history(history)
            return f"<div class='success-message'><i class='fas fa-check-circle'></i> {result}</div>"

        def load_history_with_feedback():
            history, message = load_chat_history_from_storage()
            if not history:
                return history, "<div class='warning-message'><i class='fas fa-exclamation-triangle'></i> No saved history found. Start a new conversation!</div>"
            return history, f"<div class='success-message'><i class='fas fa-check-circle'></i> {message}</div>"

        clear_btn.click(
            fn=clear_chat_and_feedback,
            outputs=[chatbot, status_indicator, current_response_index, feedback_header],
            api_name="clear"
        )

        save_btn.click(
            fn=save_history_with_feedback,
            inputs=[chatbot],
            outputs=[status_indicator]
        )

        load_btn.click(
            fn=load_history_with_feedback,
            outputs=[chatbot, status_indicator]
        )

        # Add JavaScript for tab navigation
        gr.HTML("""
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            const tabButtons = document.querySelectorAll('.tab-button');
            const tabContents = document.querySelectorAll('.tab-content');

            tabButtons.forEach(button => {
                button.addEventListener('click', function() {
                    // Get the tab name
                    const tabName = this.getAttribute('data-tab');

                    // Remove active class from all buttons and contents
                    tabButtons.forEach(btn => btn.classList.remove('active'));
                    tabContents.forEach(content => content.classList.remove('active'));

                    // Add active class to current button
                    this.classList.add('active');

                    // Add active class to corresponding content
                    document.getElementById(tabName + '-tab').classList.add('active');

                    // Save active tab to localStorage
                    localStorage.setItem('active_tab', tabName);
                });
            });

            // Load active tab from localStorage
            const activeTab = localStorage.getItem('active_tab');
            if (activeTab) {
                const activeButton = document.querySelector(`.tab-button[data-tab="${activeTab}"]`);
                if (activeButton) {
                    activeButton.click();
                }
            }
        });
        </script>
        """)

        # Add custom CSS for styling, dark mode, and mobile responsiveness
        gr.HTML(f"""
        <style>
        {css_styles}
        </style>
        """)

        return app


if __name__ == "__main__":
    # Create and launch the UI
    ui = create_ui()
    # Use a different port to avoid conflicts
    ui.launch(
        server_name=SERVER_NAME,
        server_port=8502,  # Explicitly set port
        share=False,
        show_error=True
    )
