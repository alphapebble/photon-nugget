/**
 * Simple JavaScript for Photon-Nugget UI
 */

// Function to set up tabs
function setupTabs() {
    console.log('Setting up tabs...');

    // Find tab buttons
    const tabButtons = document.querySelectorAll('.tab-nav button');
    console.log(`Found ${tabButtons.length} tab buttons`);

    // Find tab content
    const tabItems = document.querySelectorAll('.tabitem');
    console.log(`Found ${tabItems.length} tab items`);

    if (tabButtons.length === 0 || tabItems.length === 0) {
        console.log('Tabs not found yet, trying again later...');
        setTimeout(setupTabs, 500);
        return;
    }

    // Initially hide all tab content except the first one
    tabItems.forEach((item, index) => {
        if (index === 0) {
            item.style.display = 'block';
            item.classList.add('active');
        } else {
            item.style.display = 'none';
            item.classList.remove('active');
        }
    });

    // Add click handlers to tab buttons
    tabButtons.forEach((button, index) => {
        // Remove existing event listeners
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);

        // Add new click handler
        newButton.addEventListener('click', function() {
            console.log(`Tab ${index} clicked`);

            // Update active class on buttons
            tabButtons.forEach(btn => btn.classList.remove('selected'));
            newButton.classList.add('selected');

            // Show the corresponding tab content
            tabItems.forEach((item, i) => {
                if (i === index) {
                    item.style.display = 'block';
                    item.classList.add('active');
                } else {
                    item.style.display = 'none';
                    item.classList.remove('active');
                }
            });
        });
    });

    // Activate the first tab
    if (tabButtons[0]) {
        tabButtons[0].classList.add('selected');
    }

    console.log('Tabs setup complete');
}

// Function to set up dark mode toggle
function setupDarkMode() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('change', function() {
            document.body.classList.toggle('dark-mode', this.checked);
            localStorage.setItem('dark-mode', this.checked ? 'enabled' : 'disabled');
        });

        // Load saved theme preference
        const savedTheme = localStorage.getItem('dark-mode');
        if (savedTheme === 'enabled') {
            themeToggle.checked = true;
            document.body.classList.add('dark-mode');
        }
    }
}

// Function to set up action buttons
function setupActionButtons() {
    console.log('Setting up action buttons');

    // Set up clear button
    setupClearButton();

    // Set up save button
    setupSaveButton();

    // Set up load button
    setupLoadButton();
}

// Function to set up clear button
function setupClearButton() {
    const clearBtn = document.getElementById('clear-btn');
    if (clearBtn) {
        // Find the actual button element (Gradio wraps buttons in a div)
        const actualButton = clearBtn.querySelector('button');
        if (actualButton) {
            console.log('Found clear button, setting up click handler');

            // Remove existing event listeners by cloning and replacing
            const newButton = actualButton.cloneNode(true);
            actualButton.parentNode.replaceChild(newButton, actualButton);

            // Add new click handler
            newButton.addEventListener('click', function() {
                console.log('Clear button clicked');

                // Find the chatbot element
                const chatbot = document.querySelector('#chatbot');
                if (chatbot) {
                    console.log('Found chatbot element, clearing');

                    // Try to clear the chatbot
                    const messages = chatbot.querySelectorAll('.message');
                    if (messages.length > 0) {
                        console.log(`Found ${messages.length} messages, removing`);
                        messages.forEach(msg => msg.remove());
                    }

                    // Also try to clear the input field
                    const inputField = document.querySelector('#msg textarea');
                    if (inputField) {
                        inputField.value = '';
                    }
                }
            });
        }
    }
}

// Function to set up save button
function setupSaveButton() {
    const saveBtn = document.getElementById('save-btn');
    if (saveBtn) {
        // Find the actual button element
        const actualButton = saveBtn.querySelector('button');
        if (actualButton) {
            console.log('Found save button, setting up click handler');

            // Remove existing event listeners by cloning and replacing
            const newButton = actualButton.cloneNode(true);
            actualButton.parentNode.replaceChild(newButton, actualButton);

            // Add new click handler
            newButton.addEventListener('click', function() {
                console.log('Save button clicked');

                // Find the chatbot element
                const chatbot = document.querySelector('#chatbot');
                if (chatbot) {
                    // Get all messages
                    const messages = chatbot.querySelectorAll('.message');
                    if (messages.length > 0) {
                        // Create an array to store the conversation
                        const conversation = [];

                        // Extract text from each message
                        messages.forEach(msg => {
                            // Check if it's a user message or assistant message
                            const isUser = msg.classList.contains('user');
                            const text = msg.textContent.trim();

                            conversation.push({
                                role: isUser ? 'user' : 'assistant',
                                content: text
                            });
                        });

                        // Convert to JSON
                        const conversationJson = JSON.stringify(conversation, null, 2);

                        // Create a blob and download link
                        const blob = new Blob([conversationJson], { type: 'application/json' });
                        const url = URL.createObjectURL(blob);

                        // Create a download link
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `conversation-${new Date().toISOString().slice(0, 10)}.json`;
                        document.body.appendChild(a);
                        a.click();

                        // Clean up
                        setTimeout(() => {
                            document.body.removeChild(a);
                            URL.revokeObjectURL(url);
                        }, 100);

                        console.log('Conversation saved');
                    } else {
                        console.log('No messages to save');
                        alert('No conversation to save.');
                    }
                }
            });
        }
    }
}

// Function to set up load button
function setupLoadButton() {
    const loadBtn = document.getElementById('load-btn');
    if (loadBtn) {
        // Find the actual button element
        const actualButton = loadBtn.querySelector('button');
        if (actualButton) {
            console.log('Found load button, setting up click handler');

            // Remove existing event listeners by cloning and replacing
            const newButton = actualButton.cloneNode(true);
            actualButton.parentNode.replaceChild(newButton, actualButton);

            // Add new click handler
            newButton.addEventListener('click', function() {
                console.log('Load button clicked');

                // Create a file input element
                const fileInput = document.createElement('input');
                fileInput.type = 'file';
                fileInput.accept = '.json';
                fileInput.style.display = 'none';
                document.body.appendChild(fileInput);

                // Add change event listener
                fileInput.addEventListener('change', function() {
                    if (fileInput.files.length > 0) {
                        const file = fileInput.files[0];
                        const reader = new FileReader();

                        reader.onload = function(e) {
                            try {
                                // Parse the JSON
                                const conversation = JSON.parse(e.target.result);

                                // Find the chatbot element
                                const chatbot = document.querySelector('#chatbot');
                                if (chatbot) {
                                    // Clear existing messages
                                    while (chatbot.firstChild) {
                                        chatbot.removeChild(chatbot.firstChild);
                                    }

                                    // Add each message to the chatbot
                                    conversation.forEach(msg => {
                                        // Create a new message element
                                        const messageDiv = document.createElement('div');
                                        messageDiv.classList.add('message');

                                        if (msg.role === 'user') {
                                            messageDiv.classList.add('user');
                                        } else {
                                            messageDiv.classList.add('assistant');
                                        }

                                        messageDiv.textContent = msg.content;
                                        chatbot.appendChild(messageDiv);
                                    });

                                    console.log('Conversation loaded');
                                }
                            } catch (error) {
                                console.error('Error parsing conversation file:', error);
                                alert('Error loading conversation: Invalid file format.');
                            }
                        };

                        reader.readAsText(file);
                    }

                    // Clean up
                    document.body.removeChild(fileInput);
                });

                // Trigger the file input
                fileInput.click();
            });
        }
    }
}

// Function to ensure buttons have the correct styling
function fixButtonStyling() {
    console.log('Fixing button styling');

    // Find all buttons that should have primary styling
    const primaryButtons = [
        document.querySelector('#send-btn button'),
        document.querySelector('#process_btn button'),
        document.querySelector('#tilt-btn button')
    ];

    // Special fix for the Send button which is often problematic
    const sendBtn = document.querySelector('#send-btn button');
    if (sendBtn) {
        console.log('Found Send button, applying direct styling');
        sendBtn.style.backgroundColor = '#1565c0';
        sendBtn.style.color = 'white';
        sendBtn.style.border = 'none';
        sendBtn.style.borderRadius = '4px';
        sendBtn.style.padding = '10px 20px';
        sendBtn.style.fontWeight = '500';
        sendBtn.style.cursor = 'pointer';
        sendBtn.style.transition = 'background-color 0.2s ease';

        // Add hover effect
        sendBtn.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#0d47a1';
        });

        sendBtn.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '#1565c0';
        });
    } else {
        console.log('Send button not found, will try again later');
        setTimeout(() => {
            const retryBtn = document.querySelector('#send-btn button');
            if (retryBtn) {
                retryBtn.style.backgroundColor = '#1565c0';
                retryBtn.style.color = 'white';
            }
        }, 1000);
    }

    // Apply styling to each button
    primaryButtons.forEach(button => {
        if (button) {
            button.style.backgroundColor = '#1565c0';
            button.style.color = 'white';
            button.style.border = 'none';
            button.style.borderRadius = '4px';
            button.style.padding = '10px 20px';
            button.style.fontWeight = '500';
            button.style.cursor = 'pointer';
            button.style.transition = 'background-color 0.2s ease';

            // Add hover effect
            button.addEventListener('mouseenter', function() {
                this.style.backgroundColor = '#0d47a1';
            });

            button.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '#1565c0';
            });

            console.log('Applied styling to button:', button);
        }
    });
}

// Function to initialize all UI components
function initializeUI() {
    console.log('Initializing UI components...');

    // Set up dark mode
    setupDarkMode();

    // Set up action buttons
    setupActionButtons();

    // Set up tabs
    setupTabs();

    // Fix button styling
    fixButtonStyling();
}

// Run initialization immediately
console.log('Running immediate initialization');
initializeUI();

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing UI');
    initializeUI();

    // Also try again after short delay
    setTimeout(initializeUI, 100);
});

// Also try again after longer delays to ensure Gradio has fully loaded
setTimeout(initializeUI, 300);
setTimeout(initializeUI, 500);
setTimeout(initializeUI, 1000);
setTimeout(initializeUI, 2000);

// Special fix for the Send button that runs after everything else
setTimeout(() => {
    console.log('Running special Send button fix');
    const allButtons = document.querySelectorAll('button');
    allButtons.forEach(button => {
        // Check if this is the Send button by its text content or parent ID
        if (button.textContent.trim() === 'Send' ||
            button.parentElement.id === 'send-btn' ||
            button.closest('#send-btn')) {
            console.log('Found Send button via text content or parent ID');
            button.style.backgroundColor = '#1565c0';
            button.style.color = 'white';
        }
    });

    // Also try direct selector
    const sendBtn = document.querySelector('#send-btn button');
    if (sendBtn) {
        sendBtn.style.backgroundColor = '#1565c0';
        sendBtn.style.color = 'white';
    }
}, 3000);

// Add a mutation observer to detect when Gradio adds new elements
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.addedNodes.length > 0) {
            // If new nodes were added, check if they're related to tabs
            const tabsAdded = Array.from(mutation.addedNodes).some(node =>
                node.nodeType === 1 && (
                    node.classList?.contains('tab-nav') ||
                    node.querySelector?.('.tab-nav')
                )
            );

            if (tabsAdded) {
                console.log('Tab elements detected, reinitializing...');
                setTimeout(initializeUI, 100);
            }
        }
    });
});

// Start observing the document body for changes
observer.observe(document.body, { childList: true, subtree: true });
