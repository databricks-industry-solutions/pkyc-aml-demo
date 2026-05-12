// ========================================
// BANK THEME CONFIGURATION
// ========================================
// Change the ACTIVE_BANK variable to switch between bank themes
// Available options: 'databricks', 'rabobank', 'ing', 'abn'

const ACTIVE_BANK = 'rabobank'; // <-- CHANGE THIS TO SWITCH THEMES

const BANK_THEMES = {
    databricks: {
        name: 'Databricks',
        logo: 'DBLogo.png',
        colors: {
            primary: '#FF3621',      // Databricks red
            secondary: '#00A972',    // Databricks green
            accent: '#3b82f6',       // Blue
            success: '#10b981',      // Green
            warning: '#f59e0b',      // Yellow
            danger: '#ef4444',       // Red
            dark: '#0f172a',         // Dark background
            darkPanel: '#1e293b',    // Panel background
            darkBorder: '#334155'    // Border color
        }
    },
    rabobank: {
        name: 'Rabobank',
        logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Rabobank_logo.svg/320px-Rabobank_logo.svg.png',
        colors: {
            primary: '#FF6200',      // Rabobank orange
            secondary: '#00539F',    // Rabobank blue
            accent: '#FF6200',       // Orange accent
            success: '#10b981',      // Green
            warning: '#f59e0b',      // Yellow
            danger: '#ef4444',       // Red
            dark: '#001F3F',         // Dark blue background
            darkPanel: '#003366',    // Panel background
            darkBorder: '#FF6200'    // Orange border
        }
    },
    ing: {
        name: 'ING',
        logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/ING_Group_N.V._Logo.svg/320px-ING_Group_N.V._Logo.svg.png',
        colors: {
            primary: '#FF6200',      // ING orange
            secondary: '#00539F',    // ING blue
            accent: '#FF6200',       // Orange accent
            success: '#10b981',      // Green
            warning: '#f59e0b',      // Yellow
            danger: '#ef4444',       // Red
            dark: '#0f172a',         // Dark background
            darkPanel: '#1e293b',    // Panel background
            darkBorder: '#FF6200'    // Orange border
        }
    },
    abn: {
        name: 'ABN AMRO',
        logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/ABN_AMRO_Logo.svg/320px-ABN_AMRO_Logo.svg.png',
        colors: {
            primary: '#00C800',      // ABN green
            secondary: '#FFD200',    // ABN yellow
            accent: '#00C800',       // Green accent
            success: '#10b981',      // Green
            warning: '#f59e0b',      // Yellow
            danger: '#ef4444',       // Red
            dark: '#0f172a',         // Dark background
            darkPanel: '#1e293b',    // Panel background
            darkBorder: '#00C800'    // Green border
        }
    }
};

// Get current active theme
const THEME = BANK_THEMES[ACTIVE_BANK];

// Apply theme to document
function applyTheme() {
    // Update logo
    const logoElements = document.querySelectorAll('.bank-logo');
    logoElements.forEach(logo => {
        logo.src = THEME.logo;
        logo.alt = `${THEME.name} Logo`;
    });

    // Update bank name
    const nameElements = document.querySelectorAll('.bank-name');
    nameElements.forEach(el => {
        el.textContent = THEME.name;
    });

    // Apply CSS variables for dynamic theming
    document.documentElement.style.setProperty('--color-primary', THEME.colors.primary);
    document.documentElement.style.setProperty('--color-secondary', THEME.colors.secondary);
    document.documentElement.style.setProperty('--color-accent', THEME.colors.accent);
    document.documentElement.style.setProperty('--color-success', THEME.colors.success);
    document.documentElement.style.setProperty('--color-warning', THEME.colors.warning);
    document.documentElement.style.setProperty('--color-danger', THEME.colors.danger);
    document.documentElement.style.setProperty('--color-dark', THEME.colors.dark);
    document.documentElement.style.setProperty('--color-dark-panel', THEME.colors.darkPanel);
    document.documentElement.style.setProperty('--color-dark-border', THEME.colors.darkBorder);

    // Update background
    document.body.style.backgroundColor = THEME.colors.dark;

    // Apply theme-specific classes
    applyThemeClasses();
}

// Apply theme-specific CSS classes
function applyThemeClasses() {
    // Update all elements with theme-aware classes
    const primaryElements = document.querySelectorAll('.theme-primary');
    primaryElements.forEach(el => {
        el.style.color = THEME.colors.primary;
    });

    const primaryBgElements = document.querySelectorAll('.theme-primary-bg');
    primaryBgElements.forEach(el => {
        el.style.backgroundColor = THEME.colors.primary;
    });

    const primaryBorderElements = document.querySelectorAll('.theme-primary-border');
    primaryBorderElements.forEach(el => {
        el.style.borderColor = THEME.colors.primary;
    });

    const accentElements = document.querySelectorAll('.theme-accent');
    accentElements.forEach(el => {
        el.style.color = THEME.colors.accent;
    });
}

// Initialize theme on page load
if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', applyTheme);
}

