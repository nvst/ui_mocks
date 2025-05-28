# Dewey Platform Style Guide

## Core Philosophy
**Data Density + Speed + Clarity** - Every pixel serves a purpose. Information-rich interfaces that load instantly and communicate clearly.

## Design Principles

### 1. 📊 Information Density
- Maximize data per screen without feeling cramped
- Use borders and backgrounds sparingly
- Let whitespace breathe but don't waste it
- Progressive disclosure for complex data

### 2. ⚡ Performance First
- No animations or transitions
- Server-side rendering where possible
- Minimal JavaScript - only for essential interactions
- Sub-100ms response times

### 3. ⌨️ Keyboard-Centric
- Every action has a hotkey
- Visible hotkey hints in footer
- Vim-style navigation (J/K, H/L)
- Command palette with `/` or `Cmd+K`

### 4. 🎯 Clear Hierarchy
- Platform → Context → Data
- Purple for branding and primary actions
- Semantic colors for data (green/red)
- Consistent sectioning and spacing

## Visual Language

### Color System
```css
/* Brand Colors */
--ec-purple: #553C9A;        /* Primary brand, headers */
--ec-purple-light: #6B46C1;  /* Hover states */
--ec-purple-pale: #E9D8FD;   /* Active/selected states */

/* Neutral Palette */
--ec-text: #1A202C;          /* Primary text */
--ec-text-muted: #718096;    /* Secondary text */
--ec-border: #E2E8F0;        /* All borders */
--ec-bg: #FAFAFA;           /* Page background */
--ec-bg-gray: #F3F4F6;      /* Subtle backgrounds */
--ec-bg-white: #FFFFFF;     /* Content cards */

/* Semantic Colors */
--ec-positive: #22C55E;      /* Positive values, growth */
--ec-negative: #EF4444;      /* Negative values, decline */
--ec-caution: #F59E0B;       /* Warnings, alerts */

/* UI Colors */
--ec-footer: #1A202C;        /* Footer background */
--ec-header: #553C9A;        /* Header background */
```

### Typography
```css
/* Primary Font Stack */
font-family: "SF Mono", Monaco, "Courier New", monospace;

/* Font Sizes */
--font-xs: 11px;    /* Labels, metadata */
--font-sm: 12px;    /* Secondary content */
--font-base: 13px;  /* Body text */
--font-md: 14px;    /* Emphasis */
--font-lg: 16px;    /* Section headers */
--font-xl: 18px;    /* Page titles */
--font-2xl: 24px;   /* Primary display */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;

/* Line Heights */
--leading-tight: 1.2;
--leading-normal: 1.5;
--leading-relaxed: 1.7;
```

### Spacing System
Based on 4px grid:
```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
--space-20: 80px;
```

## Layout Patterns

### Application Shell
```
┌─────────────────────────────────────────────────┐
│ PLATFORM HEADER                                  │ 48px - Purple
├─────────────────────────────────────────────────┤
│ CONTEXT BAR                                      │ 56px - White
├──────────┬────────────────────────┬─────────────┤
│ SIDEBAR  │   MAIN CONTENT         │    PANEL    │
│  300px   │      Flexible          │    320px    │ Calc(100vh - 136px)
├──────────┴────────────────────────┴─────────────┤
│ FOOTER                                           │ 32px - Dark
└─────────────────────────────────────────────────┘
```

### Responsive Breakpoints
- **Mobile**: < 768px (Stack layout)
- **Tablet**: 768px - 1024px (Hide panel)
- **Desktop**: > 1024px (Full layout)

## Component Library

### Headers
```css
/* Platform Header */
.platform-header {
    background: var(--ec-purple);
    color: white;
    padding: 12px 24px;
    border-bottom: 2px solid var(--ec-purple-light);
}

/* Context Bar (Security/Page Header) */
.context-header {
    background: var(--ec-bg-white);
    padding: 16px 24px;
    border-bottom: 1px solid var(--ec-border);
}
```

### Navigation
```css
.nav-item {
    color: white;
    opacity: 0.9;
    padding-bottom: 2px;
}

.nav-item:hover { opacity: 1; }
.nav-item.active { 
    opacity: 1;
    border-bottom: 2px solid white;
}
```

### Sidebar Elements
```css
/* List Items */
.list-item {
    padding: 10px 20px;
    display: flex;
    gap: 12px;
    cursor: pointer;
}

.list-item:hover {
    background: var(--ec-bg-gray);
}

.list-item.active {
    background: var(--ec-purple-pale);
    border-left: 3px solid var(--ec-purple);
    padding-left: 17px;
}

/* Notification Box */
.notification-box {
    background: var(--ec-caution);
    color: white;
    padding: 12px;
    font-size: 11px;
}
```

### Data Display
```css
/* Data Tables */
.data-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px dotted var(--ec-border);
}

/* Metric Cards */
.metric-card {
    background: var(--ec-bg-white);
    padding: 16px;
    border: 1px solid var(--ec-border);
    border-radius: 4px;
}

/* Progress Bars */
.progress-bar {
    height: 8px;
    background: var(--ec-border);
    position: relative;
}

.progress-fill {
    height: 100%;
    background: var(--ec-purple);
}
```

### Form Elements
```css
/* Text Inputs */
.input {
    font-family: inherit;
    font-size: var(--font-base);
    padding: 8px 12px;
    border: 2px solid var(--ec-border);
    background: var(--ec-bg-white);
}

.input:focus {
    outline: none;
    border-color: var(--ec-purple);
}

/* Tick Input (Special) */
.tick-input {
    font-size: 20px;
    font-weight: 600;
    width: 80px;
    text-align: center;
    border: 2px solid var(--ec-purple);
    color: var(--ec-purple);
}

/* Textareas */
.textarea {
    font-family: inherit;
    padding: 12px;
    border: 1px solid var(--ec-border);
    resize: vertical;
    min-height: 100px;
}
```

### Buttons
```css
/* Primary Action */
.btn-primary {
    background: var(--ec-purple);
    color: white;
    padding: 12px 24px;
    border: none;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    cursor: pointer;
}

.btn-primary:hover {
    background: var(--ec-purple-light);
}

/* Secondary Action */
.btn-secondary {
    background: white;
    color: var(--ec-purple);
    border: 2px solid var(--ec-purple);
    padding: 10px 22px;
}
```

### Footer
```css
.footer {
    background: var(--ec-text);
    color: white;
    padding: 8px 24px;
    font-size: 12px;
}

/* Hotkey Display */
.hotkey {
    background: rgba(255, 255, 255, 0.2);
    padding: 2px 8px;
    border-radius: 3px;
    font-weight: 600;
    font-size: 11px;
}
```

## Interaction Patterns

### Keyboard Shortcuts
- **Navigation**: J/K (up/down), H/L (sections)
- **Actions**: I (analyze), N (note), Space (search)
- **Modifiers**: +/- (adjust values), ? (help)
- **System**: Cmd+K (command palette), Esc (cancel)

### Focus States
- 2px purple border on all interactive elements
- No outline removal without replacement
- Clear tab order through sections

### Loading States
- Skeleton screens for data tables
- Progress bars for long operations
- Inline spinners for quick updates

## Data Visualization

### Chart Guidelines
- Multi-panel layouts for complex data stories
- Consistent color coding across panels
- Minimal gridlines and chrome
- Data labels on hover only

### Status Indicators
- **Positive**: Green text/background
- **Negative**: Red text/background  
- **Neutral**: Gray text
- **Warning**: Orange background

## Content Guidelines

### Naming Conventions
- **Tickers**: Always uppercase (AAPL, MSFT)
- **Metrics**: Title case with units (Revenue Growth 3Y)
- **Actions**: Imperative verb + noun (Start Analysis)
- **Status**: Present tense (Processing, Complete)

### Data Formatting
- **Numbers**: Comma separators (1,234.56)
- **Percentages**: One decimal (12.4%)
- **Currency**: Symbol prefix ($1.2M)
- **Dates**: ISO format (2024-03-15)

## Implementation Notes

### Performance Checklist
- [ ] CSS minified and inlined for critical path
- [ ] Fonts preloaded
- [ ] Images lazy loaded below fold
- [ ] JavaScript deferred/async
- [ ] Server-side rendering for initial paint

### Accessibility Requirements
- [ ] WCAG AA contrast ratios
- [ ] Keyboard navigation complete
- [ ] Screen reader landmarks
- [ ] Focus indicators visible
- [ ] Alt text for data visualizations

### Browser Support
- Chrome/Edge 90+
- Safari 14+
- Firefox 88+
- No IE11 support

## File Structure
```
/static/
  /css/
    dewey.css          # Core framework
    dewey.min.css      # Production build
  /js/
    dewey-core.js      # Core interactions
    dewey-charts.js    # Chart library
  /fonts/
    # System fonts only, no custom downloads
```

## Example Implementation
```html
<!-- Basic Page Structure -->
<body>
    <header class="platform-header">
        <div class="platform-logo">DEWEY</div>
        <nav class="platform-nav">...</nav>
    </header>
    
    <div class="context-header">
        <!-- Page-specific header -->
    </div>
    
    <main class="main-layout">
        <aside class="sidebar">...</aside>
        <div class="content">...</div>
        <aside class="panel">...</aside>
    </main>
    
    <footer class="footer">
        <div class="hotkey-list">...</div>
        <div class="status-info">...</div>
    </footer>
</body>
```

## Design Tokens
For easy theming and consistency, export as JSON:
```json
{
  "color": {
    "brand": {
      "primary": "#553C9A",
      "light": "#6B46C1",
      "pale": "#E9D8FD"
    },
    "semantic": {
      "positive": "#22C55E",
      "negative": "#EF4444",
      "caution": "#F59E0B"
    }
  },
  "spacing": {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px"
  }
}
```

## Remember
Every element should justify its existence through utility. If it doesn't help the user make a decision or take an action, it shouldn't be there. This is a tool for serious work - make it fast, make it dense, make it clear.