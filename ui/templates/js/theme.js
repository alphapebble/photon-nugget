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
document.addEventListener('DOMContentLoaded', function() {
    loadTheme();
    setupThemeToggle();
});

// Also try to set up when the page changes
setInterval(setupThemeToggle, 1000);
