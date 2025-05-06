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
        yield "", history, "Please enter a question.", -1, ""
        return

    # Show thinking status
    yield "", history, "🤔 Thinking...", -1, ""

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
            with gr.Column(scale=1):
                gr.Markdown(f"### ☀️ **{APP_TITLE}**")
                gr.Markdown(f"_{APP_DESCRIPTION}_")
                gr.Markdown(f"📦 Model: `{MODEL_INFO}`")
                gr.Markdown(f"🧠 Knowledge: {KNOWLEDGE_INFO}")

                # Theme toggle button
                theme_btn = gr.Button("🌓 Toggle Dark Mode", elem_id="theme_toggle")

                gr.Markdown(f"🔗 [GitHub]({GITHUB_LINK})")

            # Main chat interface
            with gr.Column(scale=4):
                # Chatbot component with increased height for better mobile experience
                chatbot = gr.Chatbot(
                    label="Ask SolarBot 🌞",
                    height=CHATBOT_HEIGHT,
                    elem_id="chatbot"
                )

                # Input area
                with gr.Row():
                    user_input = gr.Textbox(
                        placeholder="Ask a question about solar...",
                        show_label=False,
                        container=False,
                        scale=12,
                        elem_id="user_input"
                    )
                    send_btn = gr.Button("🚀", variant="primary", scale=1)

                # Controls row with improved styling
                with gr.Row(equal_height=True):
                    with gr.Column(scale=1):
                        clear_btn = gr.Button(
                            "🧹 Clear Chat",
                            size="sm",
                            elem_id="clear_btn",
                            variant="secondary"
                        )
                    with gr.Column(scale=1):
                        save_btn = gr.Button(
                            "💾 Save History",
                            size="sm",
                            elem_id="save_btn",
                            variant="secondary"
                        )
                    with gr.Column(scale=1):
                        load_btn = gr.Button(
                            "📂 Load History",
                            size="sm",
                            elem_id="load_btn",
                            variant="secondary"
                        )

                # Status indicator and feedback area
                with gr.Row():
                    status_indicator = gr.Markdown("", elem_id="status_indicator")

                # Feedback section - using a container div for visibility control
                with gr.Column(elem_id="feedback_container"):
                    feedback_header = gr.Markdown("", elem_id="feedback_header")
                    # Use HTML for the buttons and status to avoid component issues
                    gr.HTML("""
                    <div id="feedback_buttons_container">
                        <button id="thumbs_up" class="feedback-btn">👍 Yes</button>
                        <button id="thumbs_down" class="feedback-btn">👎 No</button>
                    </div>
                    <div id="feedback_status"></div>
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

        # Add JavaScript for feedback buttons
        gr.HTML("""
        <script>
        // Function to set up feedback button handlers
        function setupFeedbackButtons() {
            // Check if buttons exist
            const thumbsUpBtn = document.getElementById('thumbs_up');
            const thumbsDownBtn = document.getElementById('thumbs_down');

            if (!thumbsUpBtn || !thumbsDownBtn) {
                // If buttons don't exist yet, try again in 500ms
                setTimeout(setupFeedbackButtons, 500);
                return;
            }

            // Add click handlers for feedback buttons
            thumbsUpBtn.addEventListener('click', function() {
                document.getElementById('feedback_header').innerHTML = "";
                document.getElementById('feedback_buttons_container').style.display = "none";
                document.getElementById('feedback_status').innerHTML = "Thank you for your positive feedback! ✅";
            });

            thumbsDownBtn.addEventListener('click', function() {
                document.getElementById('feedback_header').innerHTML = "";
                document.getElementById('feedback_buttons_container').style.display = "none";
                document.getElementById('feedback_status').innerHTML = "Thank you for your negative feedback! We'll work to improve. ✅";
            });
        }

        // Set up the feedback buttons when the page loads
        document.addEventListener('DOMContentLoaded', setupFeedbackButtons);
        // Also try to set up when the page changes
        setInterval(setupFeedbackButtons, 2000);
        </script>
        """)

        # History management with improved feedback
        def clear_chat_and_feedback():
            # Clear chat and hide feedback components
            chat_result, _, idx, _ = clear_chat()
            # Return empty string for feedback header to hide it
            return chat_result, "Chat cleared successfully! ✨", idx, ""

        def save_history_with_feedback(history):
            if not history:
                return "No messages to save. Try asking a question first! 📝"
            result = save_chat_history(history)
            return f"{result} ✅"

        def load_history_with_feedback():
            history, message = load_chat_history_from_storage()
            if not history:
                return history, "No saved history found. Start a new conversation! 🆕"
            return history, f"{message} ✅"

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
