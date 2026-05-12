# Transaction Screening Demo - Style Reference

**Quick Reference for AI Prompts**

Use this file when creating new components or pages that should match the demo style.

---

## Style Identity

**Name:** Modern Dark Dashboard / Enterprise SaaS Dark Mode  
**Aesthetic:** Databricks/Vercel/Linear-inspired data platform UI

---

## Essential Style Specifications

### Typography
```
Primary: DM Sans (400, 500, 700, 900)
Mono: DM Mono (300, 400, 500)
CDN: https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;900&family=DM+Mono:wght@300;400;500&display=swap
```

### Color Palette
```css
/* Backgrounds */
--bg-main: #0B2026;              /* Databricks Navy */
--bg-card: #0B2026;              /* Same, with border */
--border: rgba(238,237,233,0.1); /* 10% opacity oat */

/* Accents */
--accent-primary: #FF3621;       /* Databricks Lava */
--accent-success: #10b981;       /* Green */
--accent-warning: #f59e0b;       /* Amber */
--accent-danger: #ef4444;        /* Red */
--accent-info: #3b82f6;          /* Blue */
--accent-ai: #a855f7;            /* Purple */

/* Text */
--text-primary: #f3f4f6;         /* gray-100 */
--text-secondary: #9ca3af;       /* gray-400 */
--text-tertiary: #6b7280;        /* gray-500 */
```

### Layout System
```
Framework: Tailwind CSS with dark mode
Grid: Responsive (1/2/3 columns)
Breakpoints: md:768px, lg:1024px
Max Width: max-w-7xl (1280px)
```

### Spacing
```
Card Padding: p-6 (24px)
Gaps: gap-6 (24px)
Border Radius: rounded-xl (12px)
Section Padding: p-8 (32px)
```

### Component Patterns
```html
<!-- Card -->
<div class="bg-dark-panel border border-dark-border rounded-xl p-6 
            hover:border-databricks-lava transition-all duration-300">
    <h3 class="text-xl font-bold text-white mb-2">Title</h3>
    <p class="text-sm text-gray-400">Description</p>
</div>

<!-- Badge -->
<span class="text-xs bg-blue-900 text-blue-300 px-2 py-1 rounded">Label</span>

<!-- Button -->
<button class="bg-databricks-lava hover:bg-red-700 text-white 
               px-6 py-3 rounded-lg font-medium transition-colors">
    Action
</button>
```

---

## Tailwind Config (Required)

```javascript
tailwind.config = {
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                'databricks-navy': '#0B2026',
                'databricks-lava': '#FF3621',
                'databricks-oat-medium': '#EEEDE9',
                'databricks-oat-light': '#F9F7F4',
                'dark-bg': '#0B2026',
                'dark-panel': '#0B2026',
                'dark-border': 'rgba(238, 237, 233, 0.1)',
            }
        }
    }
}
```

---

## Animation Standards

```css
/* Transitions */
transition: all 0.3s ease;           /* General */
transition: colors 0.2s ease;        /* Color only */

/* Hover Effects */
hover:border-databricks-lava         /* Border color change */
hover:-translate-y-1                 /* Subtle lift */
hover:bg-red-700                     /* Background darken */

/* Fade In */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Active/Working Pulse */
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255,54,33,0.4); }
    50% { box-shadow: 0 0 0 8px rgba(255,54,33,0); }
}
```

---

## Badge Color System

```html
<!-- Use semantic colors for different types -->
<span class="text-xs bg-blue-900 text-blue-300 px-2 py-1 rounded">Technical</span>
<span class="text-xs bg-purple-900 text-purple-300 px-2 py-1 rounded">AI/ML</span>
<span class="text-xs bg-green-900 text-green-300 px-2 py-1 rounded">Success</span>
<span class="text-xs bg-amber-900 text-amber-300 px-2 py-1 rounded">Warning</span>
<span class="text-xs bg-red-900 text-red-300 px-2 py-1 rounded">Danger</span>
```

---

## Typography Scale

```html
text-5xl font-bold     → Page titles (48px)
text-3xl font-bold     → Section headers (30px)
text-2xl font-bold     → Card titles (24px)
text-xl font-bold      → Sub-headings (20px)
text-base              → Body text (16px)
text-sm text-gray-400  → Secondary text (14px)
text-xs text-gray-500  → Labels (12px)
font-mono              → Code/technical (DM Mono)
```

---

## Responsive Grid Pattern

```html
<!-- Standard 3-column grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- Mobile: 1 col, Tablet: 2 cols, Desktop: 3 cols -->
</div>
```

---

## Page Template (Complete)

```html
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Page</title>
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;900&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
    tailwind.config = {
        darkMode: 'class',
        theme: {
            extend: {
                colors: {
                    'databricks-navy': '#0B2026',
                    'databricks-lava': '#FF3621',
                    'dark-panel': '#0B2026',
                    'dark-border': 'rgba(238, 237, 233, 0.1)',
                }
            }
        }
    }
    </script>
    
    <style>
        body {
            background-color: #0B2026;
            font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        code, .font-mono {
            font-family: 'DM Mono', monospace;
        }
    </style>
</head>
<body class="min-h-screen text-gray-100 p-8">
    <div class="max-w-7xl mx-auto">
        <!-- Your content here -->
    </div>
</body>
</html>
```

---

## Key Design Principles

1. **Generous Whitespace** - Don't crowd elements, let them breathe
2. **Consistent Rounding** - Always rounded-xl (12px) for cards
3. **Subtle Borders** - 10% opacity, not harsh white lines
4. **Smooth Transitions** - 0.3s for most interactions
5. **Semantic Colors** - Green=good, amber=caution, red=danger
6. **Clear Hierarchy** - Size, weight, and color create importance
7. **Dark First** - Deep backgrounds with subtle accents

---

## Don'ts ❌

- Don't use bright backgrounds (stay dark)
- Don't mix other fonts (DM Sans + DM Mono only)
- Don't use harsh transitions (smooth 0.3s)
- Don't crowd elements (maintain 24px gaps)
- Don't ignore mobile (always responsive)
- Don't overuse accent color (sparingly)

---

## Related Files

- **Full Documentation:** `DESIGN-SYSTEM.md`
- **Quick Cheatsheet:** `STYLE-CHEATSHEET.md`
- **AI Prompt Template:** `STYLE-PROMPT.txt`
- **Live Examples:** `scene1-onboarding.html` through `scene5-sar-filing.html`

---

## Quick Prompt Template

```
Create a [component/page name] matching the Transaction Screening demo style:

Style: Modern Dark Dashboard
- BG: #0B2026, Accent: #FF3621
- Font: DM Sans (UI), DM Mono (code)
- Cards: rounded-xl, p-6, subtle borders (10% opacity)
- Spacing: gap-6 (24px) between elements
- Hover: smooth transitions (0.3s), subtle lift
- Responsive: 1/2/3 columns (mobile/tablet/desktop)
- Framework: Tailwind CSS dark mode

[Your specific requirements here]
```

---

**Version:** 1.0  
**Last Updated:** November 2024  
**Use:** Attach this file to AI prompts for consistent styling

