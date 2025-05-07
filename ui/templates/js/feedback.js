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

// Set up the feedback buttons when the page loads
document.addEventListener('DOMContentLoaded', setupFeedbackButtons);
// Also try to set up when the page changes
setInterval(setupFeedbackButtons, 2000);
