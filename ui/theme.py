"""
Theme and styling for the UI application.
"""

# JavaScript for theme toggling and history persistence
js_functions = """
function saveHistory(history) {
    if (history && history.length > 0) {
        localStorage.setItem('solarbot_history', JSON.stringify(history));
        return true;
    }
    return false;
}

function loadHistory() {
    const saved = localStorage.getItem('solarbot_history');
    if (saved) {
        try {
            return JSON.parse(saved);
        } catch (e) {
            console.error('Failed to parse saved history:', e);
        }
    }
    return [];
}

function clearHistory() {
    localStorage.removeItem('solarbot_history');
    return [];
}

function toggleTheme() {
    const isDark = document.documentElement.classList.contains('dark');
    if (isDark) {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('solarbot_theme', 'light');
    } else {
        document.documentElement.classList.add('dark');
        localStorage.setItem('solarbot_theme', 'dark');
    }
    return !isDark;
}

function loadTheme() {
    const savedTheme = localStorage.getItem('solarbot_theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const shouldBeDark = savedTheme === 'dark' || (savedTheme === null && prefersDark);

    if (shouldBeDark) {
        document.documentElement.classList.add('dark');
        return true;
    } else {
        document.documentElement.classList.remove('dark');
        return false;
    }
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', loadTheme);
"""

# CSS for styling the application
css_styles = """
/* Base styles */
:root {
    --primary-color: #3498db;
    --secondary-color: #f39c12;
    --background-color: #ffffff;
    --text-color: #333333;
    --card-bg-color: #f5f5f5;
    --border-color: #e0e0e0;
    --shadow-color: rgba(0, 0, 0, 0.1);
    --status-color: #666666;
    --positive-color: #27ae60;
    --negative-color: #e74c3c;
    --button-hover-color: #2980b9;
    --button-active-color: #1f6aa5;
}

/* Dark mode styles */
.dark {
    --primary-color: #2980b9;
    --secondary-color: #e67e22;
    --background-color: #1a1a1a;
    --text-color: #f0f0f0;
    --card-bg-color: #2c2c2c;
    --border-color: #444444;
    --shadow-color: rgba(0, 0, 0, 0.3);
    --status-color: #aaaaaa;
    --button-hover-color: #3498db;
    --button-active-color: #2980b9;
}

body {
    background-color: var(--background-color);
    color: var(--text-color);
    transition: background-color 0.3s, color 0.3s;
}

/* Status indicator */
#status_indicator {
    color: var(--status-color);
    min-height: 1.5em;
    margin-top: 0.5em;
    font-style: italic;
    font-weight: 500;
    text-align: center;
}

/* Theme toggle button */
#theme_toggle {
    margin-top: 1rem;
    margin-bottom: 1rem;
    background-color: var(--card-bg-color);
    border: 1px solid var(--border-color);
    color: var(--text-color);
    transition: all 0.3s;
    border-radius: 8px;
    font-weight: 500;
}

#theme_toggle:hover {
    background-color: var(--primary-color);
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px var(--shadow-color);
}

#theme_toggle:active {
    transform: translateY(0);
    background-color: var(--button-active-color);
}

/* Chatbot styling */
#chatbot {
    border-radius: 12px;
    box-shadow: 0 4px 12px var(--shadow-color);
    transition: box-shadow 0.3s;
}

#chatbot:hover {
    box-shadow: 0 6px 16px var(--shadow-color);
}

/* User input styling */
#user_input {
    border-radius: 20px;
    padding: 12px 18px;
    border: 1px solid var(--border-color);
    transition: border-color 0.3s, box-shadow 0.3s;
}

#user_input:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

/* Control buttons styling */
#clear_btn, #save_btn, #load_btn {
    width: 100%;
    border-radius: 8px;
    transition: all 0.3s;
    font-weight: 500;
    margin: 0 4px;
    background-color: var(--card-bg-color);
    border: 1px solid var(--border-color);
    color: var(--text-color);
}

#clear_btn:hover, #save_btn:hover, #load_btn:hover {
    background-color: var(--button-hover-color);
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px var(--shadow-color);
}

#clear_btn:active, #save_btn:active, #load_btn:active {
    transform: translateY(0);
    background-color: var(--button-active-color);
}

/* Specific button colors */
#clear_btn:hover {
    background-color: var(--negative-color);
}

#save_btn:hover {
    background-color: var(--positive-color);
}

#load_btn:hover {
    background-color: var(--secondary-color);
}

/* Feedback section styling */
#feedback_header:empty {
    display: none;
}

#feedback_status:empty {
    display: none;
}

/* Feedback buttons container */
#feedback_buttons_container {
    display: flex;
    justify-content: center;
    margin-top: 0.5rem;
    gap: 1rem;
}

/* Style the feedback buttons */
#feedback_buttons_container button {
    padding: 0.5rem 1rem;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    background-color: var(--card-bg-color);
    color: var(--text-color);
    cursor: pointer;
    transition: all 0.3s;
    font-weight: 500;
}

#thumbs_up:hover {
    background-color: var(--positive-color);
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px var(--shadow-color);
}

#thumbs_down:hover {
    background-color: var(--negative-color);
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px var(--shadow-color);
}

/* Feedback status styling */
#feedback_status {
    margin-top: 1rem;
    text-align: center;
    font-style: italic;
    color: var(--primary-color);
    font-weight: 500;
}

#feedback_header {
    margin-top: 1rem;
    font-weight: 600;
    color: var(--text-color);
    text-align: center;
}

#thumbs_up, #thumbs_down {
    transition: transform 0.2s, background-color 0.3s;
    border-radius: 8px;
    margin: 0 0.5rem;
}

#thumbs_up:hover {
    transform: scale(1.05);
    background-color: var(--positive-color);
    color: white;
}

#thumbs_down:hover {
    transform: scale(1.05);
    background-color: var(--negative-color);
    color: white;
}

#feedback_status {
    margin-top: 0.5rem;
    font-style: italic;
    text-align: center;
    color: var(--primary-color);
    font-weight: 500;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    .gradio-container {
        padding: 0 !important;
    }

    .gradio-row {
        flex-direction: column !important;
    }

    .gradio-column {
        width: 100% !important;
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }

    #chatbot {
        height: 60vh !important;
    }

    /* Improve button spacing on mobile */
    #clear_btn, #save_btn, #load_btn {
        margin: 4px 0;
        padding: 8px 12px;
    }
}
"""

def toggle_theme(current_theme: str) -> str:
    """
    Toggle between light and dark themes.

    Args:
        current_theme: The current theme ('light' or 'dark')

    Returns:
        The new theme
    """
    new_theme = "dark" if current_theme == "light" else "light"
    return new_theme
