# UX Design Specification — città.

## Overview

This document defines the visual identity, design principles, and responsive layout specifications for **città.**, a modern web application for comparing casa vs affitto investment scenarios in Italy.

**Version:** 1.0  
**Last Updated:** May 2026  
**Framework:** Streamlit + Plotly + Modern CSS

---

## Design Principles

### 1. Modern Dark-First Design
- **Primary:** Dark mode as default, supporting eye comfort and contemporary aesthetics
- **Secondary:** Light mode toggle available in sidebar for user preference
- Inspired by GitHub's modern design language
- Clean, minimalist approach with intentional use of whitespace

### 2. Typography-Driven Hierarchy
- **Headlines:** Crimson Pro (italic serif) + Inter (sans-serif) for contrast
- **Body:** Inter 400-500 for clarity and legibility
- **Monospace:** Courier New for technical labels and monetary values
- Font sizes scale responsively using `clamp()` for optimal reading at any viewport

### 3. Accessibility & Clarity
- High contrast ratios for all text elements
- Clear visual hierarchy with deliberate use of color and weight
- Accessible color palette tested for colorblindness
- Touch-friendly interactive elements (min 44px targets on mobile)

### 4. Interactive Excellence
- Smooth transitions and hover states (0.3s cubic-bezier animations)
- Metric cards lift on hover with subtle shadow enhancement
- Consistent feedback patterns for all interactive elements
- Responsive chart interactions (unified hover, optimized legends)

---

## Color Palette

### Dark Mode (Primary)

| Purpose | Color | Hex | Usage |
|---------|-------|-----|-------|
| Background | GitHub Dark | `#0F1117` | Main app background |
| Cards | Dark Gray | `#161B22` | Content containers |
| Text | Light Gray | `#E6EDF3` | Primary text |
| Muted Text | Light Gray 60% | `rgba(230, 237, 243, 0.6)` | Captions, labels |
| Accent | Warm Gold | `#F2C14E` | Highlights, emphasis |
| Success | Modern Green | `#58A66D` | Positive metrics (BE ≤15yr) |
| Warning | Amber | `#E89E2A` | Caution metrics (BE 15-25yr) |
| Danger | Modern Red | `#F85149` | Critical metrics (BE >25yr) |
| Border | Subtle Dark | `#30363D` | Dividers, card edges |

### Light Mode (Secondary)

| Purpose | Color | Hex | Usage |
|---------|-------|-----|-------|
| Background | GitHub Light | `#F6F8FA` | Main app background |
| Cards | Pure White | `#FFFFFF` | Content containers |
| Text | Dark Gray | `#1F2937` | Primary text |
| Muted Text | Dark Gray 60% | `rgba(31, 41, 55, 0.6)` | Captions, labels |
| Accent | Warm Gold | `#F2C14E` | Highlights (consistent) |
| Success/Warning/Danger | Same as dark mode | See above | Consistent semantics |
| Border | Light Gray | `#E5E7EB` | Dividers, card edges |

---

## Layout Sections

### 1. Hero Section

**Purpose:** Immediate visual impact and key insight communication

**Desktop (>1200px)**
- Full width, gradient background (135deg, dark→darker)
- Padding: 4rem top/bottom, 2rem sides
- Large headline with animated gold accent text
- Descriptive subheading with bold numerical emphasis
- Decorative gradient circle (radial, 0.08 opacity gold) top-right

**Tablet (600-1200px)**
- Padding reduced to 3rem top/bottom, 1.5rem sides
- Headline scales via `clamp(1.7rem, 3vw, 2.5rem)`
- Subheading adjusted for narrower viewport

**Mobile (<600px)**
- Padding: 2rem, 1rem sides
- Headline: `clamp(1.5rem, 2.5vw, 2rem)`
- Subheading: 0.9rem
- Decorative circle scaled to 300x300px

**Responsive Breakpoint CSS**
```css
.hero {
    padding: 4rem 2rem;  /* desktop */
}

@media (max-width: 768px) {
    .hero { padding: 2.5rem 1rem; }
}

@media (max-width: 600px) {
    .hero { padding: 2rem 1rem; }
    .hero::before { width: 300px; height: 300px; }
}
```

### 2. Metric Cards (5-Column Grid)

**Purpose:** Key financial metrics at a glance

**Desktop Layout**
- 5 equal columns using Streamlit `st.columns(5)`
- Card dimensions: fluid width, minimum 150px
- Height: 100% (self-aligning)

**Card Contents**
```
┌─────────────────────────┐
│ LABEL (12px, caps)      │
│ VALUE (1.5-2.2rem, 900) │
│ subtext (12px, muted)   │
└─────────────────────────┘
```

**Responsive Behavior**
- Tablet: 3 columns → 2 rows
- Mobile: 1 column → 5 rows (stacked)
- Cards maintain padding (1.5rem desktop, 1.2rem mobile)

**Interactive States**
- Hover: Gold border + lifted shadow + -2px Y translation
- Color-coded values:
  - `.success`: Green text (Break-even ≤15 years)
  - `.warning`: Amber text (Break-even 15-25 years)
  - `.danger`: Red text (Break-even >25 years)

### 3. Comparison Cards (2-Column Flex)

**Purpose:** Side-by-side city comparison with visual differentiation

**Desktop Layout**
```
[Primary Card] [Secondary Card]
flex: 1, min-width: 280px, gap: 1.5rem
```

**Card Styling**
- Primary: Dark gradient (135deg), gold text accent
- Secondary: Light card variant, bordered
- Padding: 2rem all sides
- Border-radius: 12px

**Content Hierarchy**
```
CITY (11px, caps, gold)
BREAK-EVEN VALUE (2.5rem, 900)
metrics (13px, muted)
metrics (13px, muted)
```

**Responsive Behavior**
- Tablet (600-1200px): flex-wrap, reduced gap
- Mobile (<600px): flex-direction column, full width
- Values scale: 2.5rem → 2rem on mobile

### 4. Input Forms (Sidebar)

**Purpose:** Clean, organized parameter controls

**Sidebar Structure**
```
[Brand Logo] [Theme Toggle]
─────────────────────────────
📍 LOCATION
  [City Selector]

📐 SUPERFICIE
  [Metratura Slider]

─────────────────────────────
💰 PARAMETRI MUTUO
  [Anticipo Slider]
  [Durata Select]
  [Tasso Slider]
  [Regime Fiscale]
  [Base Catastale Slider]

─────────────────────────────
📈 PARAMETRI INVESTIMENTO
  [ETF Rendimento Slider]
  [Rivalutazione Slider]

─────────────────────────────
🔀 CONFRONTO
  [City Comparison Select]
```

**Section Headers**
- Font: Inter, 13px, 700 weight
- Letter-spacing: 0.1em
- Text-transform: uppercase
- Color: Theme text
- Margin-bottom: 1rem

**Input Elements**
- Streamlit-native controls (no custom styling)
- `label_visibility="collapsed"` for clean layout
- Help text provided for technical parameters
- Dividers between logical groups

**Dark Mode Toggle**
- Location: Top-right of sidebar
- Button: "🌙" (dark mode active) / "☀️" (light mode active)
- Triggers full page rerun with updated colors

### 5. Tabs & Charts

**Purpose:** Multi-view data exploration

**Tab Headers**
- Font: Inter, 12px, 600 weight
- Letter-spacing: 0.08em
- Text-transform: uppercase
- Color: Muted (unselected) → Gold (active)
- Border-bottom: 2px gold on active

**Chart Styling**
```
plot_bgcolor: cards['plot_bg'] (theme-aware)
paper_bgcolor: colors['bg'] (theme-aware)
font: Inter, theme text color
gridcolor: rgba(100, 100, 100, 0.1)
hovermode: "x unified"
```

**Chart Data Series**
- Break-even line: Gold (#F2C14E), 3px width
- Comparison line: Red (#F85149), 3px width dashed
- Reference line: Green (#58A66D), 2px width dotted

---

## Responsive Breakpoints

| Device Type | Width Range | Adjustments |
|-------------|------------|-------------|
| Desktop | >1200px | Full layout, all columns visible, 4rem hero padding |
| Tablet | 600-1200px | 3-column metric grid, reduced gaps, 3rem hero padding |
| Mobile | <600px | Stacked single column, full-width cards, 2rem hero padding |
| Small Mobile | <480px | Minimum padding 1rem, font reduction, compact sidebar |

---

## Interactive States & Animations

### Metric Cards
```css
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

:hover {
    border-color: {gold};
    box-shadow: 0 4px 12px rgba(242, 193, 78, 0.1);
    transform: translateY(-2px);
}
```

### Comparison Cards
- Static presentation, no hover effects
- Clear visual differentiation (primary vs secondary)
- Consistent padding and typography

### Charts
- Smooth line transitions
- Unified hover information
- Color-coded annotations
- Responsive font sizes in legends

---

## Dark Mode Implementation

**Session State Management**
```python
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

def get_colors():
    """Returns color dict based on st.session_state.dark_mode"""
    return colors_dark if st.session_state.dark_mode else colors_light
```

**CSS Injection**
- Single `st.markdown(<style>)` block at app startup
- Uses theme-aware variables throughout
- Colors are computed in Python, injected into CSS
- Theme toggle triggers `st.rerun()` with updated colors

**Persistence**
- Session state preserved during user interaction
- Sidebar theme button always visible
- Switching modes applies instantly to all components

---

## Typography Scale

### Headings
| Level | Font | Size | Weight | Usage |
|-------|------|------|--------|-------|
| H1 | Crimson Pro italic + Inter | clamp(2rem, 4vw, 3.2rem) | 900 | Hero title |
| H2 | Inter | clamp(1.5rem, 3vw, 2rem) | 800 | Section titles |
| H3 | Inter | 13px | 700 | Input section titles |

### Body Text
| Purpose | Font | Size | Weight |
|---------|------|------|--------|
| Body | Inter | 1rem | 400-500 |
| Caption | Inter | 12-13px | 500 |
| Label | Courier New | 11-12px | 600 |
| Monospace | Courier New | 12px | 400 |

### Responsive Type Scaling
- Headlines use `clamp()` for fluid scaling
- No fixed pixel sizes for body text on mobile
- Minimum font size: 11px (technical labels)
- Maximum line-length: 900px (readability)

---

## Accessibility Features

### Color Contrast
- Text on backgrounds: ≥7:1 WCAG AAA
- Accent colors: Tested against colorblindness simulators
- Semantic color usage (green=good, red=caution, etc.)

### Interactive Elements
- Minimum touch target: 44x44px (WCAG Level AAA)
- Clear focus states (border-color on interactive elements)
- Tab-accessible form inputs
- Descriptive hover tooltips on complex controls

### Content Structure
- Semantic HTML hierarchy (h1 → h2 → h3)
- Alt text on charts (via Plotly's text annotations)
- Description text in expandable sections
- Clear data table headers

---

## Performance Optimizations

### CSS Delivery
- Single stylesheet, computed at startup
- CSS variables and template substitution (Python f-strings)
- No external stylesheet dependencies
- Inline styles for theme-specific properties

### Font Loading
- Google Fonts API (Inter + Crimson Pro)
- Cached by browser for subsequent loads
- Fallback fonts specified (system fonts)

### Chart Optimization
- Cached data generation (`@st.cache_data`)
- Responsive height (450-520px) to avoid reflow
- Unified hover to reduce DOM updates

---

## Mobile-First Design Notes

### Sidebar on Mobile
- Full-width on screens <600px (Streamlit default)
- Touch-friendly slider spacing
- Large tap targets for selectboxes

### Hero on Mobile
- Headline scales aggressively down: 3.2rem → 1.4rem
- Subheading remains readable: 1rem → 0.9rem
- Decorative element scales: 500px → 300px
- Removed large padding for screen real estate

### Metric Cards on Mobile
- Single column layout (100% width)
- Reduced padding: 1.5rem → 1.2rem
- Font sizes remain readable via `clamp()`

### Charts on Mobile
- Full-width, responsive height
- Touch-friendly legend (horizontal, bottom)
- Simplified annotations to avoid overlap

---

## Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| CSS Grid | ✓ | ✓ | ✓ | ✓ |
| Flexbox | ✓ | ✓ | ✓ | ✓ |
| CSS Variables | ✓ | ✓ | ✓ | ✓ |
| clamp() | ✓ | ✓ | ✓ | ✓ |
| backdrop-filter | ✓ | ✓ | ✓ | ✓ |
| radial-gradient | ✓ | ✓ | ✓ | ✓ |
| Plotly | ✓ | ✓ | ✓ | ✓ |

---

## Future Enhancements

### Phase 2: Advanced Responsiveness
- Hamburger menu sidebar for mobile (<480px)
- Swipe-enabled chart navigation
- Gesture controls for sliders on touch devices

### Phase 3: Customization
- User preference persistence (localStorage)
- Custom color theme builder
- Font size adjustment (accessibility)

### Phase 4: Data Visualization
- Sensitivity analysis chart (3D surface)
- Scenario comparison overlay
- Export charts as PNG/SVG

---

## File References

- **Implementation:** `/app.py` (Streamlit application)
- **Styling:** Inline CSS in app.py (lines ~93-410)
- **Colors:** Constants in app.py (lines ~36-50)
- **Responsive:** CSS @media queries (lines ~380-410)

---

## Contact & Questions

For design system questions or updates, contact the development team.

**Version History:**
- v1.0 (May 2026): Initial dark-mode redesign, mobile responsiveness, dark/light toggle
