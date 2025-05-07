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
    
    // Find the clear button
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

// Function to initialize all UI components
function initializeUI() {
    console.log('Initializing UI components...');
    
    // Set up dark mode
    setupDarkMode();
    
    // Set up action buttons
    setupActionButtons();
    
    // Set up tabs
    setupTabs();
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
