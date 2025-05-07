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

// Add icons to tabs
function addTabIcons() {
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
}

// Initialize tabs when the page loads
document.addEventListener('DOMContentLoaded', function() {
    setupTabs();
    addTabIcons();
});

// Also try to set up when the page changes
setInterval(function() {
    setupTabs();
    addTabIcons();
}, 2000);
