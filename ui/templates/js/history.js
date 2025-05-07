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
