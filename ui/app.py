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
from api import get_model_response
from ui.theme import css_styles
from ui.messages import format_html_message, format_thinking_animation
from ui.template_loader import render_template, load_js_bundle


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
        yield "", history, format_html_message("empty_input", "error"), -1, ""
        return

    # Show thinking status with a more professional look
    yield "", history, format_thinking_animation(), -1, ""

    # Get response from model
    reply = get_model_response(message, history)

    # Update history and clear status
    history.append((message, reply))
    response_idx = len(history) - 1

    # Return updated state and show feedback components
    yield "", history, "", response_idx, f"### {format_html_message('feedback_prompt')}"


def create_ui() -> gr.Blocks:
    """
    Create the Gradio UI interface.

    Returns:
        Gradio Blocks interface
    """
    with gr.Blocks(theme=gr.themes.Soft()) as app:
        # Add JavaScript for client-side functionality
        gr.HTML(load_js_bundle("theme.js", "history.js", "tabs.js", "feedback.js"))

        # State variables for feedback
        current_response_index = gr.State(-1)

        # Header with app info and theme toggle
        with gr.Row(equal_height=True):
            with gr.Column():
                # Modern header with logo and title
                gr.HTML(render_template("components/header.html", {
                    "APP_TITLE": APP_TITLE,
                    "APP_DESCRIPTION": APP_DESCRIPTION
                }))

            # Theme toggle button with icon (will be controlled by JavaScript)
            gr.Button(
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
                            gr.HTML(render_template("components/info_card.html", {
                                "MODEL_INFO": MODEL_INFO,
                                "KNOWLEDGE_INFO": KNOWLEDGE_INFO,
                                "GITHUB_LINK": GITHUB_LINK
                            }))

                        # Controls card
                        with gr.Group(elem_id="controls_card"):
                            gr.HTML("""<h3 class="card-title">Conversation</h3>""")

                            # Buttons will be controlled by JavaScript
                            gr.Button(
                                "Clear Chat",
                                elem_id="clear_btn",
                                variant="secondary",
                                size="sm"
                            )

                            gr.Button(
                                "Save History",
                                elem_id="save_btn",
                                variant="secondary",
                                size="sm"
                            )

                            gr.Button(
                                "Load History",
                                elem_id="load_btn",
                                variant="secondary",
                                size="sm"
                            )

                            # Add icons to buttons via JavaScript
                            gr.HTML(render_template("components/button_icons.html"))

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
                                gr.HTML(render_template("components/feedback.html"))

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
                gr.HTML(render_template("components/placeholder_scada.html"))

            # Tilt Optimization Tab (Placeholder)
            with gr.Tab("Tilt Optimization"):
                gr.HTML(render_template("components/placeholder_tilt.html"))

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

        # Theme toggle - using a custom JavaScript function
        gr.HTML("""
        <script>
        // Create a direct event listener for the theme toggle button
        function setupThemeToggle() {
            const themeBtn = document.getElementById('theme_toggle');
            if (!themeBtn) {
                setTimeout(setupThemeToggle, 100);
                return;
            }

            // Remove any existing event listeners
            const newBtn = themeBtn.cloneNode(true);
            themeBtn.parentNode.replaceChild(newBtn, themeBtn);

            // Add click event listener
            newBtn.addEventListener('click', function() {
                // Toggle the dark class on the document element
                document.documentElement.classList.toggle('dark');

                // Save the theme preference to localStorage
                const isDark = document.documentElement.classList.contains('dark');
                localStorage.setItem('solarbot_theme', isDark ? 'dark' : 'light');

                // Update the button text based on the theme
                this.innerHTML = isDark ?
                    '<i class="fas fa-sun"></i> Light Mode' :
                    '<i class="fas fa-moon"></i> Dark Mode';
            });

            // Set initial button text based on current theme
            const isDark = document.documentElement.classList.contains('dark');
            newBtn.innerHTML = isDark ?
                '<i class="fas fa-sun"></i> Light Mode' :
                '<i class="fas fa-moon"></i> Dark Mode';
        }

        // Set up the theme toggle when the page loads
        document.addEventListener('DOMContentLoaded', setupThemeToggle);
        // Also try to set up when the page changes
        setInterval(setupThemeToggle, 1000);
        </script>
        """)

        # History management with browser localStorage
        gr.HTML("""
        <script>
        // Function to save chat history to localStorage
        function saveHistory() {
            const chatbot = document.querySelector('#chatbot');
            if (!chatbot) {
                showMessage('warning', 'Could not find chat history to save.');
                return;
            }

            // Extract messages from the DOM
            const messages = [];
            const userMessages = chatbot.querySelectorAll('.user-message');
            const botMessages = chatbot.querySelectorAll('.bot-message');

            for (let i = 0; i < userMessages.length; i++) {
                if (botMessages[i]) {
                    messages.push([
                        userMessages[i].textContent.trim(),
                        botMessages[i].textContent.trim()
                    ]);
                }
            }

            if (messages.length === 0) {
                showMessage('warning', 'No messages to save. Try asking a question first!');
                return;
            }

            // Save to localStorage
            localStorage.setItem('solarbot_history', JSON.stringify(messages));
            showMessage('success', 'Chat history saved successfully!');
        }

        // Function to load chat history from localStorage
        function loadHistory() {
            const saved = localStorage.getItem('solarbot_history');
            if (!saved) {
                showMessage('warning', 'No saved history found. Start a new conversation!');
                return;
            }

            try {
                const messages = JSON.parse(saved);
                if (messages.length === 0) {
                    showMessage('warning', 'Saved history is empty.');
                    return;
                }

                // Clear current chat
                clearChat();

                // Add a small delay to ensure chat is cleared
                setTimeout(() => {
                    // Simulate typing each message to recreate the conversation
                    simulateConversation(messages);
                    showMessage('success', 'Chat history loaded successfully!');
                }, 100);
            } catch (e) {
                showMessage('error', 'Error loading chat history: ' + e.message);
            }
        }

        // Function to clear chat
        function clearChat() {
            // Find the clear button in the Gradio interface and click it
            const clearBtn = document.querySelector('#clear_btn');
            if (clearBtn) {
                clearBtn.click();
                showMessage('success', 'Chat cleared successfully!');
            } else {
                // Fallback: Try to clear the chatbot directly
                const chatbot = document.querySelector('#chatbot');
                if (chatbot) {
                    while (chatbot.firstChild) {
                        chatbot.removeChild(chatbot.firstChild);
                    }
                    showMessage('success', 'Chat cleared successfully!');
                } else {
                    showMessage('error', 'Could not clear chat.');
                }
            }

            // Also clear from localStorage
            localStorage.removeItem('solarbot_history');
        }

        // Function to simulate a conversation by typing messages
        function simulateConversation(messages) {
            const userInput = document.querySelector('#user_input textarea');
            const sendBtn = document.querySelector('#send_btn');

            if (!userInput || !sendBtn) {
                showMessage('error', 'Could not find input elements.');
                return;
            }

            let i = 0;

            function typeNextMessage() {
                if (i >= messages.length) return;

                const [userMsg, _] = messages[i];

                // Type user message
                userInput.value = userMsg;

                // Trigger input event to make sure Gradio recognizes the change
                userInput.dispatchEvent(new Event('input', { bubbles: true }));

                // Click send button
                sendBtn.click();

                // Move to next message after a delay
                i++;
                if (i < messages.length) {
                    setTimeout(typeNextMessage, 1000); // Wait for response
                }
            }

            // Start typing messages
            typeNextMessage();
        }

        // Function to show status messages
        function showMessage(type, text) {
            const statusIndicator = document.querySelector('#status_indicator');
            if (!statusIndicator) return;

            let icon = 'info-circle';
            if (type === 'success') icon = 'check-circle';
            if (type === 'warning') icon = 'exclamation-triangle';
            if (type === 'error') icon = 'exclamation-circle';

            statusIndicator.innerHTML = `<div class='${type}-message'><i class='fas fa-${icon}'></i> ${text}</div>`;

            // Clear message after 5 seconds
            setTimeout(() => {
                if (statusIndicator.querySelector(`.${type}-message`)) {
                    statusIndicator.innerHTML = '';
                }
            }, 5000);
        }

        // Set up event listeners for the history buttons
        function setupHistoryButtons() {
            const saveBtn = document.querySelector('#save_btn');
            const loadBtn = document.querySelector('#load_btn');
            const clearBtn = document.querySelector('#clear_btn');

            if (!saveBtn || !loadBtn || !clearBtn) {
                setTimeout(setupHistoryButtons, 100);
                return;
            }

            // Remove existing listeners
            const newSaveBtn = saveBtn.cloneNode(true);
            const newLoadBtn = loadBtn.cloneNode(true);
            const newClearBtn = clearBtn.cloneNode(true);

            saveBtn.parentNode.replaceChild(newSaveBtn, saveBtn);
            loadBtn.parentNode.replaceChild(newLoadBtn, loadBtn);
            clearBtn.parentNode.replaceChild(newClearBtn, clearBtn);

            // Add new listeners
            newSaveBtn.addEventListener('click', saveHistory);
            newLoadBtn.addEventListener('click', loadHistory);
            newClearBtn.addEventListener('click', clearChat);
        }

        // Set up the history buttons when the page loads
        document.addEventListener('DOMContentLoaded', setupHistoryButtons);
        // Also try to set up when the page changes
        setInterval(setupHistoryButtons, 1000);
        </script>
        """)

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
        server_port=8504,  # Explicitly set port
        share=False,
        show_error=True
    )
