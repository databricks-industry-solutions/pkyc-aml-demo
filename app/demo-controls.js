// ========================================
// DEMO CONTROLS
// ========================================
// Note: Keyboard shortcuts have been removed - navigation via UI only

// Navigation structure
const DEMO_SCENES = [
    { id: 1, file: 'scene1-onboarding.html', title: 'Seamless KYC Onboarding' },
    { id: 2, file: 'scene2-txn-screening.html', title: 'Real-Time Transaction Screening' },
    { id: 3, file: 'scene3-ai-monitoring.html', title: 'AI-Powered Transaction Monitoring' },
    { id: 4, file: 'scene4-edd-investigation.html', title: 'EDD Investigation' },
    { id: 5, file: 'scene5-sar-filing.html', title: 'SAR Filing & Case Closure' },
    { id: 6, file: 'scene6-cco-dashboard.html', title: 'CCO Executive Dashboard' }
];

// Get current scene from URL
function getCurrentScene() {
    const currentFile = window.location.pathname.split('/').pop();
    return DEMO_SCENES.find(scene => scene.file === currentFile);
}

// Navigate to next/previous scene
function navigateScene(direction) {
    const current = getCurrentScene();
    if (!current) return;
    
    const nextIndex = current.id - 1 + direction;
    if (nextIndex >= 0 && nextIndex < DEMO_SCENES.length) {
        // Add fade-out transition
        document.body.style.opacity = '0';
        document.body.style.transition = 'opacity 0.3s ease-out';
        
        setTimeout(() => {
            window.location.href = DEMO_SCENES[nextIndex].file;
        }, 300);
    }
}

// Toggle presenter mode (hide navigation bar)
let presenterMode = false;
function togglePresenterMode() {
    presenterMode = !presenterMode;
    const navBar = document.querySelector('.demo-nav-bar');
    const timestamp = document.querySelector('.demo-timestamp');
    
    if (navBar) {
        if (presenterMode) {
            navBar.style.transform = 'translateY(100%)';
            navBar.style.transition = 'transform 0.3s ease-out';
            if (timestamp) timestamp.style.opacity = '0';
        } else {
            navBar.style.transform = 'translateY(0)';
            if (timestamp) timestamp.style.opacity = '1';
        }
    }
}

// Update real-time timestamp
function updateTimestamp() {
    const timestampElement = document.querySelector('.demo-timestamp');
    if (timestampElement) {
        const now = new Date();
        const options = { 
            weekday: 'short', 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric', 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        };
        timestampElement.textContent = now.toLocaleDateString('en-US', options);
    }
}

// Keyboard shortcuts removed - navigation via UI only

// Page transition fade-in on load
window.addEventListener('DOMContentLoaded', () => {
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.3s ease-in';
    
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);
    
    // Start timestamp updates
    updateTimestamp();
    setInterval(updateTimestamp, 1000);
});

// Keyboard shortcuts hint removed

