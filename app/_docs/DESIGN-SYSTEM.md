# Design System & Style Guide

## Style Name
**"Modern Dark Dashboard"** or **"Enterprise SaaS Dark Mode"**

This design follows the contemporary data platform/dashboard aesthetic popularized by companies like Databricks, Vercel, Linear, and Stripe - characterized by deep dark backgrounds, subtle gradients, generous spacing, and premium typography.

---

## Core Design Principles

### 1. **Visual Hierarchy**
- Strong contrast between background and content cards
- Clear information density with breathing room
- Gradual color transitions (RAG: Red → Amber → Green)

### 2. **Premium Feel**
- Generous whitespace/padding
- Subtle shadows and border effects
- Smooth micro-animations
- High-quality typography

### 3. **Functional Elegance**
- Data-dense but scannable
- Color-coded information (semantic colors)
- Progressive disclosure (expand/collapse)

---

## Typography

### Primary Font: **DM Sans**
- **Purpose**: UI text, headings, body copy
- **Weights Used**: 400 (regular), 500 (medium), 700 (bold), 900 (black)
- **Why**: Clean, modern, excellent readability at all sizes
- **CDN**: `https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;900&display=swap`

### Monospace Font: **DM Mono**
- **Purpose**: Code snippets, technical data, IDs, timestamps
- **Weights Used**: 300 (light), 400 (regular), 500 (medium)
- **Why**: Pairs perfectly with DM Sans, maintains modern aesthetic
- **CDN**: `https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&display=swap`

### Font Scale
```css
text-5xl   → 48px → Main page titles
text-3xl   → 30px → Section headers
text-2xl   → 24px → Card titles
text-xl    → 20px → Sub-headings
text-base  → 16px → Body text
text-sm    → 14px → Secondary info
text-xs    → 12px → Labels, badges
```

---

## Color Palette

### Primary Colors (Databricks Brand)
```
Databricks Navy:   #0B2026  (Main background, dark panels)
Databricks Lava:   #FF3621  (Primary accent, CTAs, alerts)
Databricks Oat:    #EEEDE9  (Light text, borders at 10% opacity)
```

### Semantic Colors (Risk/Status)
```
Success (Green):   #10b981  (Complete, approved, safe)
Warning (Amber):   #f59e0b  (Investigate, medium risk)
Danger (Red):      #ef4444  (Blocked, high risk, critical)
Info (Blue):       #3b82f6  (Informational, neutral)
Purple:            #a855f7  (AI/ML features, Agent Bricks)
```

### Grayscale
```
gray-100  → #f3f4f6  (Lightest text)
gray-200  → #e5e7eb
gray-300  → #d1d5db
gray-400  → #9ca3af  (Secondary text)
gray-500  → #6b7280
gray-600  → #4b5563
gray-700  → #374151
gray-800  → #1f2937  (Card backgrounds)
gray-900  → #111827  (Dark elements)
```

### Background Layers
```
Body Background:    #0B2026 (Databricks Navy)
Card/Panel:         #0B2026 with border
Border:             rgba(238, 237, 233, 0.1) (10% opacity oat)
Hover State:        Slight border color increase
```

### Gradient Accent
```css
background: linear-gradient(135deg, #FF3621 0%, #FF5C4D 100%);
```

---

## Spacing System

### Padding/Margin Scale (Tailwind)
```
p-2  → 0.5rem (8px)   → Compact badges
p-3  → 0.75rem (12px) → Tight spacing
p-4  → 1rem (16px)    → Standard padding
p-6  → 1.5rem (24px)  → Card padding
p-8  → 2rem (32px)    → Section padding
p-12 → 3rem (48px)    → Large gaps
```

### Gap Between Elements
```
gap-2  → 0.5rem  → Tight (badges, tags)
gap-4  → 1rem    → Standard (grid items)
gap-6  → 1.5rem  → Generous (cards)
gap-8  → 2rem    → Section separation
```

---

## Layout Patterns

### Card Component
```html
<div class="bg-dark-panel border border-dark-border rounded-xl p-6 hover:border-databricks-lava transition-colors">
    <!-- Content -->
</div>
```

**Key Properties:**
- Border radius: `rounded-xl` (12px)
- Subtle border: `rgba(238, 237, 233, 0.1)`
- Hover effect: Border color change
- Padding: `p-6` (24px)

### Grid Layouts
```html
<!-- 3-column responsive -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- Cards -->
</div>
```

### Stat/Metric Display
```html
<div class="text-center">
    <div class="text-4xl font-bold text-white mb-2">$2.4M</div>
    <div class="text-sm text-gray-400">Total Amount</div>
</div>
```

---

## Component Styles

### Badges/Tags
```html
<span class="text-xs bg-blue-900 text-blue-300 px-2 py-1 rounded">
    Unity Catalog
</span>
```

**Variants:**
- Blue: Technical features (Unity Catalog, Streaming)
- Purple: AI/ML (Mosaic AI, Agent Bricks)
- Green: Success states (Delta Lake, Complete)
- Red: Alerts (High Risk, Blocked)
- Orange: Warnings (MLRO, Investigate)

### Buttons
```html
<!-- Primary CTA -->
<button class="bg-databricks-lava hover:bg-red-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
    Start Investigation
</button>

<!-- Secondary -->
<button class="bg-gray-800 hover:bg-gray-700 text-gray-100 px-4 py-2 rounded-lg transition-colors">
    View Details
</button>
```

### Progress Bars
```html
<div class="h-2 bg-gray-800 rounded-full overflow-hidden">
    <div class="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-300" 
         style="width: 73%">
    </div>
</div>
```

---

## Animations

### Fade In
```css
.fade-in {
    animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
```

### Pulse (for active states)
```css
.agent-working {
    animation: agentPulse 2s infinite;
}

@keyframes agentPulse {
    0%, 100% { 
        box-shadow: 0 0 0 0 rgba(255, 54, 33, 0.4);
        border-color: #FF3621;
    }
    50% { 
        box-shadow: 0 0 0 8px rgba(255, 54, 33, 0);
        border-color: #FF5C4D;
    }
}
```

### Hover Transitions
```css
transition: all 0.3s ease;           /* General */
transition: colors 0.2s ease;        /* Color changes */
transition: transform 0.3s ease;     /* Movement */
```

### Card Hover Effect
```css
.scene-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(255, 54, 33, 0.15);
}
```

---

## Icon System

### SVG Icons
- **Source**: Heroicons (outline style)
- **Size**: `w-4 h-4` (16px) for inline, `w-6 h-6` (24px) for standalone
- **Color**: Matches parent text color

**Example:**
```html
<svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
          d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
</svg>
```

---

## Data Visualization

### Chart Colors
```javascript
colors: {
    green: '#10b981',   // Safe transactions
    amber: '#f59e0b',   // Medium risk
    red: '#ef4444',     // High risk/alerts
    blue: '#3b82f6',    // Info/metrics
    purple: '#a855f7'   // AI predictions
}
```

### Line Chart Style
- Line width: 2-3px
- Smooth curves: `tension: 0.4`
- Gradient fills under lines
- Subtle grid lines: `rgba(255,255,255,0.05)`

### World Map Style
- Fill: Dark gray (`#1e293b`)
- Borders: Light gray (`#475569`)
- Connection lines: Colored arcs (blue/green/amber/red)
- Glow effects on hover

---

## Scrollbars (Custom)

```css
.scrollbar-thin::-webkit-scrollbar {
    width: 6px;
}

.scrollbar-thin::-webkit-scrollbar-track {
    background: #334155;
    border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
    background: #64748b;
    border-radius: 3px;
}
```

---

## Responsive Breakpoints

```
sm:  640px   → Mobile landscape
md:  768px   → Tablet
lg:  1024px  → Desktop
xl:  1280px  → Large desktop
2xl: 1536px  → Extra large
```

### Typical Pattern
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- Mobile: 1 col, Tablet: 2 cols, Desktop: 3 cols -->
</div>
```

---

## Template Structure

### Basic Page Template
```html
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Page Title</title>
    
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
                        'databricks-oat-medium': '#EEEDE9',
                        'databricks-oat-light': '#F9F7F4',
                        'dark-bg': '#0B2026',
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
<body class="min-h-screen text-gray-100">
    <!-- Your content -->
</body>
</html>
```

---

## Quick Copy-Paste Prompt

### For Future Projects
When requesting designs similar to this demo, use this prompt:

```
Create a modern dark dashboard UI using:
- Design Style: Enterprise SaaS / Modern Data Platform (similar to Databricks, Vercel, Linear)
- Typography: DM Sans for UI (400, 500, 700, 900 weights), DM Mono for code
- Color Scheme: Deep dark background (#0B2026), vibrant accent color (#FF3621), subtle borders (10% opacity)
- Framework: Tailwind CSS with dark mode
- Components: Rounded cards (12px radius), generous padding (24px), subtle hover effects
- Spacing: Generous whitespace, 24px gaps between cards
- Animations: Subtle fade-ins (0.5s), smooth hover transitions (0.3s)
- Layout: Card-based grid layout, responsive (1/2/3 columns)
- Visual: Gradient accents, status colors (green/amber/red), data visualization elements
```

### Specific Component Requests
```
"Create a [component name] in the style of the Transaction Screening demo:
- Dark card with #0B2026 background
- 10% opacity white border
- 24px padding, 12px border radius
- DM Sans font
- Hover effect: border color transition to accent color
- Include [specific elements]"
```

---

## Tools & Technologies

### CSS Framework
- **Tailwind CSS v3** (CDN for prototyping)
- Utility-first approach
- Dark mode class strategy
- Custom color extensions

### Fonts
- **Google Fonts CDN**
- DM Sans + DM Mono pairing

### Visualization
- **D3.js v7** (for maps and complex charts)
- Native Canvas API (for performance-critical animations)
- SVG for icons and simple charts

### JavaScript
- Vanilla ES6+ (no framework dependency)
- Modern async/await patterns
- CSS animations over JS when possible

---

## Design References

This style is inspired by:
- **Databricks** - Enterprise data platform aesthetic
- **Vercel** - Clean dark mode, generous spacing
- **Linear** - Premium feel, subtle animations
- **Stripe Dashboard** - Data density + elegance
- **Figma** - Modern tooling interface

---

## Best Practices

### Do's ✅
- Use generous whitespace (24px+ between major elements)
- Maintain consistent border radius (12px for cards)
- Apply subtle hover effects (0.3s transitions)
- Keep text hierarchy clear (size + weight + color)
- Use semantic colors (green=good, red=bad)
- Add breathing room with padding
- Implement smooth page transitions

### Don'ts ❌
- Don't use bright backgrounds (stay dark)
- Don't crowd elements (maintain spacing)
- Don't mix fonts (stick to DM Sans + DM Mono)
- Don't use harsh transitions (keep it smooth)
- Don't overuse bright accent colors (use sparingly)
- Don't ignore mobile responsiveness
- Don't skip loading states for animations

---

## Accessibility Notes

While this is a dark demo, consider:
- Contrast ratio: Minimum 4.5:1 for text
- Focus states: Visible keyboard navigation
- ARIA labels: For screen readers
- Color blindness: Don't rely solely on color
- Font sizes: Minimum 14px for body text

---

## Export This Style

To use this style in a new project, copy:
1. ✅ The `<head>` section (fonts + Tailwind config)
2. ✅ The color palette values
3. ✅ The custom CSS animations
4. ✅ Component patterns from `asset-links-example.html`

**File to reference:** Any of the `scene*.html` files

---

## Summary

**Style Name:** Modern Dark Dashboard / Enterprise SaaS Dark Mode

**Key Characteristics:**
- Deep dark backgrounds (#0B2026)
- DM Sans + DM Mono typography
- Generous spacing (24px cards, 24px gaps)
- Rounded corners (12px)
- Subtle borders (10% opacity)
- Smooth animations (0.3-0.5s)
- Card-based layouts
- Semantic color system
- Tailwind CSS utility classes

**Perfect for:** Executive demos, dashboards, data platforms, financial applications, enterprise tools

---

**Created for:** Transaction Screening Demo  
**Version:** 1.0  
**Last Updated:** November 2024

