"""
Theme and styling for the UI application.
"""

# JavaScript for theme toggling, history persistence, and tab navigation
js_functions = """
// History management functions
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

// Theme management functions
function toggleTheme() {
    const isDark = document.documentElement.classList.contains('dark');
    if (isDark) {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('solarbot_theme', 'light');
        updateThemeIcon(false);
    } else {
        document.documentElement.classList.add('dark');
        localStorage.setItem('solarbot_theme', 'dark');
        updateThemeIcon(true);
    }
    return !isDark;
}

function updateThemeIcon(isDark) {
    const themeBtn = document.getElementById('theme_toggle');
    if (!themeBtn) return;

    const icon = themeBtn.querySelector('i');
    if (icon) {
        if (isDark) {
            icon.className = 'fas fa-sun';
        } else {
            icon.className = 'fas fa-moon';
        }
    }
}

function loadTheme() {
    const savedTheme = localStorage.getItem('solarbot_theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const shouldBeDark = savedTheme === 'dark' || (savedTheme === null && prefersDark);

    if (shouldBeDark) {
        document.documentElement.classList.add('dark');
        updateThemeIcon(true);
        return true;
    } else {
        document.documentElement.classList.remove('dark');
        updateThemeIcon(false);
        return false;
    }
}

// Tab navigation functions
function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    if (!tabButtons.length || !tabContents.length) {
        setTimeout(setupTabs, 500);
        return;
    }

    tabButtons.forEach((button, index) => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to current button and content
            button.classList.add('active');
            tabContents[index].classList.add('active');

            // Save active tab to localStorage
            localStorage.setItem('active_tab', index);
        });
    });

    // Load active tab from localStorage
    const activeTab = localStorage.getItem('active_tab');
    if (activeTab !== null) {
        tabButtons[parseInt(activeTab)].click();
    } else {
        // Set first tab as active by default
        tabButtons[0].classList.add('active');
        tabContents[0].classList.add('active');
    }
}

// Feedback handling functions
function setupFeedbackButtons() {
    const thumbsUpBtn = document.getElementById('thumbs_up');
    const thumbsDownBtn = document.getElementById('thumbs_down');
    const feedbackHeader = document.getElementById('feedback_header');

    if (!thumbsUpBtn || !thumbsDownBtn) {
        setTimeout(setupFeedbackButtons, 500);
        return;
    }

    // Show feedback container when header has content
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.target.innerHTML.trim() !== "") {
                document.getElementById('feedback_container').style.display = "block";
            } else {
                document.getElementById('feedback_container').style.display = "none";
            }
        });
    });

    if (feedbackHeader) {
        observer.observe(feedbackHeader, { childList: true, subtree: true });
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
        document.getElementById('feedback_status').innerHTML = "Thank you for your feedback! We'll work to improve. ✅";
    });
}

// Initialize everything on page load
document.addEventListener('DOMContentLoaded', function() {
    loadTheme();
    setupTabs();
    setupFeedbackButtons();
});

// Also try to set up when the page changes
setInterval(function() {
    setupTabs();
    setupFeedbackButtons();
}, 2000);
"""

# CSS for styling the application
css_styles = """
/* Import FontAwesome */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

/* Base styles */
:root {
    --primary-color: #3498db;
    --secondary-color: #f39c12;
    --accent-color: #9b59b6;
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
    --border-radius: 10px;
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

/* Dark mode styles */
.dark {
    --primary-color: #3498db;
    --secondary-color: #f39c12;
    --accent-color: #9b59b6;
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
    font-family: var(--font-family);
}

/* App header styling */
.app-header {
    display: flex;
    align-items: center;
    padding: var(--spacing-md);
    background-color: var(--card-bg-color);
    border-radius: var(--border-radius);
    margin-bottom: var(--spacing-md);
    box-shadow: 0 2px 4px var(--shadow-color);
}

.app-logo {
    font-size: 24px;
    margin-right: var(--spacing-md);
    color: var(--primary-color);
}

.app-title {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
}

.app-description {
    margin: 0;
    font-size: 14px;
    color: var(--status-color);
    font-style: italic;
}

/* Tab styling */
.tabs > .tab-nav {
    background-color: var(--card-bg-color);
    border-radius: var(--border-radius) var(--border-radius) 0 0;
    overflow: hidden;
    margin-bottom: var(--spacing-md);
    display: flex;
    border-bottom: 1px solid var(--border-color);
}

.tabs > .tab-nav > button {
    padding: var(--spacing-md);
    border: none;
    background: none;
    cursor: pointer;
    font-weight: 500;
    color: var(--text-color);
    transition: all 0.3s;
    flex: 1;
    text-align: center;
    border-bottom: 3px solid transparent;
    margin: 0;
}

.tabs > .tab-nav > button.selected {
    border-bottom: 3px solid var(--primary-color);
    color: var(--primary-color);
    font-weight: 600;
}

.tabs > .tab-nav > button:hover:not(.selected) {
    background-color: rgba(0, 0, 0, 0.05);
}

.tabs > .tab-nav > button i {
    margin-right: var(--spacing-sm);
}

/* Style the tab content */
.tabs > .tabitem {
    padding: var(--spacing-md);
    background-color: var(--background-color);
    border-radius: 0 0 var(--border-radius) var(--border-radius);
}

/* Card styling */
.card {
    background-color: var(--card-bg-color);
    border-radius: var(--border-radius);
    box-shadow: 0 4px 6px var(--shadow-color);
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-md);
}

.card-title {
    font-size: 16px;
    font-weight: 600;
    margin-top: 0;
    margin-bottom: var(--spacing-md);
    color: var(--primary-color);
    border-bottom: 1px solid var(--border-color);
    padding-bottom: var(--spacing-sm);
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

/* Thinking animation */
.thinking-indicator {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-md);
    margin: var(--spacing-md) auto;
    max-width: 200px;
    background-color: var(--card-bg-color);
    border-radius: 30px;
    box-shadow: 0 4px 8px var(--shadow-color);
}

.thinking-text {
    margin-top: var(--spacing-sm);
    color: var(--primary-color);
    font-weight: 500;
}

.thinking-dots {
    display: flex;
    justify-content: center;
    gap: 8px;
}

.thinking-dots span {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: var(--primary-color);
    display: inline-block;
    animation: thinking-bounce 1.4s infinite ease-in-out both;
}

.thinking-dots span:nth-child(1) {
    animation-delay: -0.32s;
}

.thinking-dots span:nth-child(2) {
    animation-delay: -0.16s;
}

@keyframes thinking-bounce {
    0%, 80%, 100% {
        transform: scale(0);
        opacity: 0.5;
    }
    40% {
        transform: scale(1);
        opacity: 1;
    }
}

/* Status message styling */
.error-message, .success-message, .warning-message {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-md);
    margin: var(--spacing-md) auto;
    max-width: 300px;
    border-radius: var(--border-radius);
    font-weight: 500;
}

.error-message {
    background-color: rgba(231, 76, 60, 0.1);
    border-left: 4px solid var(--negative-color);
    color: var(--negative-color);
}

.success-message {
    background-color: rgba(46, 204, 113, 0.1);
    border-left: 4px solid var(--positive-color);
    color: var(--positive-color);
}

.warning-message {
    background-color: rgba(243, 156, 18, 0.1);
    border-left: 4px solid var(--secondary-color);
    color: var(--secondary-color);
}

.error-message i, .success-message i, .warning-message i {
    margin-right: var(--spacing-sm);
    font-size: 16px;
}

/* Theme toggle button */
#theme_toggle {
    background-color: var(--card-bg-color);
    border: 1px solid var(--border-color);
    color: var(--text-color);
    transition: all 0.3s;
    cursor: pointer;
    position: absolute;
    top: var(--spacing-md);
    right: var(--spacing-md);
    border-radius: var(--border-radius);
    padding: 8px 16px;
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
    border-radius: var(--border-radius);
    box-shadow: 0 4px 12px var(--shadow-color);
    transition: box-shadow 0.3s;
    height: 450px;
    overflow-y: auto;
}

#chatbot:hover {
    box-shadow: 0 6px 16px var(--shadow-color);
}

/* User input styling */
#user_input {
    border-radius: 30px;
    padding: 12px 18px;
    border: 1px solid var(--border-color);
    transition: border-color 0.3s, box-shadow 0.3s;
    font-size: 14px;
}

#user_input:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

/* Send button styling */
#send_btn {
    border-radius: 30px;
    background-color: var(--primary-color);
    color: white;
    border: none;
    padding: 10px 20px;
    cursor: pointer;
    transition: all 0.3s;
    font-weight: 500;
    min-width: 80px;
}

#send_btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px var(--shadow-color);
    background-color: var(--button-hover-color);
}

#send_btn:active {
    transform: translateY(0);
    background-color: var(--button-active-color);
}

/* Control buttons styling */
#clear_btn, #save_btn, #load_btn {
    width: 100%;
    border-radius: var(--border-radius);
    transition: all 0.3s;
    font-weight: 500;
    margin: var(--spacing-xs) 0;
    background-color: var(--card-bg-color);
    border: 1px solid var(--border-color);
    color: var(--text-color);
    padding: var(--spacing-sm) var(--spacing-md);
    display: flex;
    align-items: center;
    justify-content: center;
}

#clear_btn i, #save_btn i, #load_btn i {
    margin-right: var(--spacing-sm);
}

#clear_btn:hover, #save_btn:hover, #load_btn:hover {
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px var(--shadow-color);
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
    margin-top: var(--spacing-md);
    gap: var(--spacing-md);
}

/* Style the feedback buttons */
#feedback_buttons_container button {
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--border-radius);
    border: 1px solid var(--border-color);
    background-color: var(--card-bg-color);
    color: var(--text-color);
    cursor: pointer;
    transition: all 0.3s;
    font-weight: 500;
    display: flex;
    align-items: center;
}

#feedback_buttons_container button i {
    margin-right: var(--spacing-sm);
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
    margin-top: var(--spacing-md);
    text-align: center;
    font-style: italic;
    color: var(--primary-color);
    font-weight: 500;
}

#feedback_header {
    margin-top: var(--spacing-md);
    font-weight: 600;
    color: var(--text-color);
    text-align: center;
}

/* Info items styling */
.info-item {
    display: flex;
    align-items: center;
    margin-bottom: var(--spacing-sm);
}

.info-item i {
    width: 20px;
    margin-right: var(--spacing-sm);
    color: var(--primary-color);
}

/* Placeholder content for future tabs */
.placeholder-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-lg);
    text-align: center;
    height: 300px;
}

.placeholder-icon {
    font-size: 48px;
    color: var(--primary-color);
    margin-bottom: var(--spacing-md);
    opacity: 0.7;
}

.coming-soon {
    margin-top: var(--spacing-md);
    font-weight: bold;
    color: var(--accent-color);
    font-size: 18px;
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
        margin: var(--spacing-xs) 0;
        padding: var(--spacing-sm) var(--spacing-md);
    }

    /* Adjust tab buttons for mobile */
    .tab-button {
        padding: var(--spacing-sm);
        font-size: 14px;
    }

    .tab-button i {
        margin-right: 0;
    }

    /* Stack sidebar on mobile */
    #sidebar {
        margin-bottom: var(--spacing-md);
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
