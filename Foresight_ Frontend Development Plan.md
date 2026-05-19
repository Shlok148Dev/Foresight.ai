# Foresight: Frontend Development Plan

## Premium Design System & Implementation Guide

---

## Part 1: Design Philosophy

### Core Principles

**1. Intelligence Over Clutter**
- Every pixel serves a purpose
- Information hierarchy is crystal clear
- No decorative elements
- Minimal but powerful

**2. Dark Mode Premium**
- Background: #0A0A14 (near black with blue tint)
- Accent: #6C63FF (purple for primary actions)
- Secondary: #00D4AA (teal for highlights)
- Text: #FFFFFF (white for primary), #A0AEC0 (gray for secondary)

**3. Organic Shapes**
- Border radius: 12-20px (never sharp corners)
- Smooth transitions: 200-300ms
- Flowing curves, not geometric
- Natural feel, premium aesthetic

**4. Motion & Animation**
- Micro-interactions on every element
- Smooth 60fps animations
- Purpose-driven (not gratuitous)
- Accessible (respects prefers-reduced-motion)

**5. Data Visualization**
- Charts are beautiful AND informative
- Animated transitions between states
- Color-coded by meaning (not arbitrary)
- Responsive to user interaction

---

## Part 2: Color Palette

### Primary Colors

```css
--color-bg-primary: #0A0A14;      /* Main background */
--color-bg-secondary: #0F1419;    /* Cards, elevated surfaces */
--color-bg-tertiary: #1A1F3A;     /* Hover states */

--color-accent-primary: #6C63FF;   /* Purple - primary actions */
--color-accent-secondary: #00D4AA; /* Teal - highlights, success */
--color-accent-tertiary: #FF6B9D;  /* Pink - warnings, alerts */

--color-text-primary: #FFFFFF;     /* Main text */
--color-text-secondary: #A0AEC0;   /* Secondary text */
--color-text-tertiary: #718096;    /* Tertiary text */

--color-border: #2A3050;           /* Borders */
--color-border-hover: #00D4AA;     /* Hover state borders */
```

### Semantic Colors

```css
/* Status Colors */
--color-success: #10B981;
--color-warning: #F59E0B;
--color-error: #EF4444;
--color-info: #3B82F6;

/* Spread Stage Colors */
--color-embryonic: #6C63FF;    /* Purple */
--color-emerging: #00D4AA;     /* Teal */
--color-accelerating: #F59E0B; /* Amber */
--color-peaking: #EF4444;      /* Red */
--color-declining: #6B7280;    /* Gray */
```

---

## Part 3: Typography

### Font Family
- **Primary:** Inter (Google Fonts)
- **Monospace:** Fira Code (for code, metrics)

### Font Sizes & Weights

```css
/* Display */
--font-display-lg: 48px / 1.2 / 700;  /* Hero headlines */
--font-display-md: 36px / 1.25 / 700; /* Section titles */
--font-display-sm: 28px / 1.3 / 600;  /* Subsection titles */

/* Heading */
--font-heading-lg: 24px / 1.35 / 600; /* Page titles */
--font-heading-md: 20px / 1.4 / 600;  /* Card titles */
--font-heading-sm: 16px / 1.5 / 600;  /* Small titles */

/* Body */
--font-body-lg: 16px / 1.6 / 400;     /* Main text */
--font-body-md: 14px / 1.6 / 400;     /* Secondary text */
--font-body-sm: 12px / 1.5 / 400;     /* Tertiary text */

/* Caption */
--font-caption: 11px / 1.4 / 500;     /* Labels, badges */
```

---

## Part 4: Component Library

### Button Component

```tsx
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'tertiary' | 'ghost'
  size: 'sm' | 'md' | 'lg'
  state: 'default' | 'hover' | 'active' | 'disabled'
  icon?: React.ReactNode
  children: React.ReactNode
}

// Variants
Primary:    bg-[#6C63FF] text-white hover:opacity-90
Secondary:  bg-[#1A1F3A] border-[#2A3050] text-[#00D4AA]
Tertiary:   bg-transparent text-[#00D4AA]
Ghost:      bg-transparent text-[#A0AEC0]

// Sizes
sm:  px-3 py-1.5 text-sm
md:  px-4 py-2 text-base
lg:  px-6 py-3 text-lg

// Animation
Transition: 200ms ease-out
Hover:     scale(1.02), opacity(0.9)
Active:    scale(0.98)
```

### Card Component

```tsx
interface CardProps {
  variant: 'default' | 'elevated' | 'outlined'
  interactive?: boolean
  children: React.ReactNode
}

// Styles
Default:   bg-[#0F1419] border-[#2A3050] rounded-[16px]
Elevated:  bg-[#1A1F3A] shadow-lg rounded-[16px]
Outlined:  bg-transparent border-[#2A3050] rounded-[16px]

// Interactive
Hover:     border-[#00D4AA] shadow-glow
Active:    scale(0.98)

// Animation
Transition: 300ms ease-out
Shadow:    0 0 20px rgba(0, 212, 170, 0.1)
```

### Signal Card (Custom)

```tsx
interface SignalCardProps {
  signal: Signal
  onSave: () => void
  onExpand: () => void
}

// Layout
┌─────────────────────────────────┐
│ [Icon] Title                    │
│ Description                     │
│ Platform | Community | Velocity │
│ [Badge] Confidence [Arc]        │
│ [Action Prompt]                 │
│ [Save] [Expand]                 │
└─────────────────────────────────┘

// Animations
Mount:     fadeIn (300ms) + slideUp (300ms)
Hover:     pulse ring + border glow
Click:     scale(0.98) + expand
```

### Chart Component (D3 + Recharts)

```tsx
interface ChartProps {
  data: ChartData[]
  type: 'line' | 'area' | 'bar' | 'pie'
  interactive: boolean
  animated: boolean
}

// Styling
Lines:     gradient from #6C63FF to #00D4AA
Areas:     gradient fill with opacity
Bars:      solid color with hover highlight
Tooltips:  dark background, teal border

// Animations
Load:      draw animation (1s)
Hover:     highlight + tooltip fade-in
Update:    smooth transition (500ms)
```

---

## Part 5: Page Designs

### Feed Mode

**Purpose:** Personalized signal stream for discovery

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│ Header: Foresight | Search | Notifications | Profile│
├──────────┬──────────────────────────────────────────┤
│ Sidebar: │ Feed Mode                               │
│ Domains  │ [For You] [New] [High Velocity] [Watch] │
│ (5)      │                                          │
│          │ ┌────────────────────────────────────┐  │
│          │ │ Signal Card 1                      │  │
│          │ │ Title, Description, Metrics        │  │
│          │ │ [Track] [Insights] [Related]       │  │
│          │ └────────────────────────────────────┘  │
│          │                                          │
│          │ ┌────────────────────────────────────┐  │
│          │ │ Signal Card 2                      │  │
│          │ │ Title, Description, Metrics        │  │
│          │ │ [Track] [Insights] [Related]       │  │
│          │ └────────────────────────────────────┘  │
│          │                                          │
│          │ [Load More]                             │
└──────────┴──────────────────────────────────────────┘
```

**Key Features:**
- Real-time signal stream
- Personalized ranking (ML model)
- Save signals to watchlist
- View related signals
- Filter by domain, platform, velocity

**Animations:**
- Cards fade in as they load
- Pulse ring on hover
- Smooth scroll
- Real-time updates (WebSocket)

---

### Search Mode

**Purpose:** Discover signals before they trend

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│ Header: Foresight | Search | Notifications | Profile│
├──────────┬──────────────────────────────────────────┤
│ Sidebar: │ Search Mode                             │
│ Search   │ [Search Bar] [Autocomplete]              │
│ Compare  │                                          │
│ Alerts   │ Search Results:                          │
│ Saved    │                                          │
│ Settings │ ┌──────────────────────────────────┐    │
│          │ │ Signal Timeline (24h Velocity)   │    │
│          │ │ [Line Chart]                     │    │
│          │ └──────────────────────────────────┘    │
│          │                                          │
│          │ ┌──────────────────────────────────┐    │
│          │ │ Platform Breakdown               │    │
│          │ │ [Pie Chart]                      │    │
│          │ └──────────────────────────────────┘    │
│          │                                          │
│          │ ┌──────────────────────────────────┐    │
│          │ │ Top Communities                  │    │
│          │ │ [List with metrics]              │    │
│          │ └──────────────────────────────────┘    │
│          │                                          │
│          │ ┌──────────────────────────────────┐    │
│          │ │ 7-Day Forecast                   │    │
│          │ │ [Area Chart]                     │    │
│          │ └──────────────────────────────────┘    │
└──────────┴──────────────────────────────────────────┘
```

**Key Features:**
- Full-text + semantic search
- Autocomplete suggestions
- Signal timeline (24h velocity)
- Platform breakdown (pie chart)
- Top communities (list)
- 7-day forecast (area chart)
- Compare up to 5 signals

**Animations:**
- Chart animations on load
- Smooth transitions between searches
- Hover tooltips
- Animated metrics counters

---

### Dashboard Mode

**Purpose:** Team workspace for signal tracking

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│ Header: Foresight | Dashboard | Notifications | Pro │
├──────────┬──────────────────────────────────────────┤
│ Sidebar: │ Dashboard                               │
│ My Radar │ Welcome back, [User]                    │
│ Domains  │                                          │
│ Saved    │ ┌────────────────────────────────────┐  │
│ Team     │ │ My Radar (Top 5 Signals)           │  │
│ Reports  │ │ [Signal Card 1] [Signal Card 2]... │  │
│          │ └────────────────────────────────────┘  │
│          │                                          │
│          │ ┌────────────────────────────────────┐  │
│          │ │ Accuracy Tracking                  │  │
│          │ │ [Line Chart: Simulation vs Reality]│  │
│          │ │ Overall Accuracy: 84% ↑ 6%        │  │
│          │ └────────────────────────────────────┘  │
│          │                                          │
│          │ ┌────────────────────────────────────┐  │
│          │ │ Team Signal Board                  │  │
│          │ │ [Shared signals with team members] │  │
│          │ └────────────────────────────────────┘  │
└──────────┴──────────────────────────────────────────┘
```

**Key Features:**
- Personalized radar (top 5 signals)
- Accuracy tracking (simulation vs reality)
- Team collaboration (shared board)
- Domain management
- Report generation
- Team member management

**Animations:**
- Cards fade in on load
- Accuracy chart animated transitions
- Real-time team updates
- Smooth page transitions

---

### Simulation Replay

**Purpose:** Visualize how signals spread

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│ Header: Simulation Replay | Share | Menu            │
├──────────┬──────────────────────────────────────────┤
│ Sidebar: │ [Force-Directed Graph]                  │
│ Spread   │ Community nodes with signal flow         │
│ Path     │ Animated edges showing propagation       │
│ (8 steps)│ Particle effects                         │
│          │                                          │
│ Metrics: │ [Timeline Scrubber]                     │
│ Virality │ ├─ Step 1 ── Step 2 ── ... ── Step 8 ─┤
│ Decay    │                                          │
│ ETA      │ Right Panel:                             │
│          │ ├─ Virality Coefficient: 2.47           │
│          │ ├─ Decay Probability: 0.23              │
│          │ ├─ Mainstream ETA: 2h 47m               │
│          │ └─ [View Full Metrics]                  │
└──────────┴──────────────────────────────────────────┘
```

**Key Features:**
- Force-directed graph (D3.js)
- Community nodes (sized by influence)
- Signal flow animation
- Timeline scrubber (playback control)
- Metrics dashboard
- Export to PNG/SVG

**Animations:**
- Graph physics simulation
- Signal propagation animation
- Node highlighting on hover
- Smooth timeline scrubbing

---

## Part 6: Animation System

### Framer Motion Presets

```tsx
// Fade In
const fadeIn = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  transition: { duration: 0.3 }
}

// Slide Up
const slideUp = {
  initial: { y: 20, opacity: 0 },
  animate: { y: 0, opacity: 1 },
  transition: { duration: 0.4, ease: 'easeOut' }
}

// Scale In
const scaleIn = {
  initial: { scale: 0.95, opacity: 0 },
  animate: { scale: 1, opacity: 1 },
  transition: { duration: 0.3 }
}

// Pulse
const pulse = {
  animate: {
    scale: [1, 1.05, 1],
    opacity: [1, 0.8, 1]
  },
  transition: { duration: 2, repeat: Infinity }
}

// Glow
const glow = {
  animate: {
    boxShadow: [
      '0 0 0 0 rgba(0, 212, 170, 0)',
      '0 0 0 10px rgba(0, 212, 170, 0.1)',
      '0 0 0 0 rgba(0, 212, 170, 0)'
    ]
  },
  transition: { duration: 2, repeat: Infinity }
}

// Chart Draw
const chartDraw = {
  initial: { pathLength: 0, opacity: 0 },
  animate: { pathLength: 1, opacity: 1 },
  transition: { duration: 1, ease: 'easeInOut' }
}
```

---

## Part 7: Responsive Design

### Breakpoints

```css
/* Mobile First */
--breakpoint-xs: 0px;      /* Default */
--breakpoint-sm: 640px;    /* Small devices */
--breakpoint-md: 768px;    /* Tablets */
--breakpoint-lg: 1024px;   /* Desktops */
--breakpoint-xl: 1280px;   /* Large desktops */
--breakpoint-2xl: 1536px;  /* Extra large */
```

### Mobile Optimizations

**Feed Mode (Mobile):**
- Full-width cards
- Vertical scroll (no sidebar)
- Bottom navigation bar
- Swipe gestures for navigation
- Touch-friendly buttons (44px min)

**Search Mode (Mobile):**
- Full-width search bar
- Stacked charts (vertical)
- Collapsible sections
- Simplified comparison (2 signals max)

**Dashboard Mode (Mobile):**
- Collapsed sidebar (hamburger menu)
- Stacked cards
- Scrollable radar
- Simplified team board

---

## Part 8: Implementation Roadmap

### Week 1: Foundation
- [ ] Design system in Tailwind CSS 4
- [ ] Component library (Button, Card, Input, Modal)
- [ ] Animation system (Framer Motion presets)
- [ ] Responsive grid system
- [ ] Color tokens & typography

### Week 2: Pages
- [ ] Feed Mode page
- [ ] Search Mode page
- [ ] Dashboard Mode page
- [ ] Simulation Replay page
- [ ] Navigation & routing

### Week 3: Interactivity
- [ ] Real-time updates (WebSocket)
- [ ] Chart animations (D3 + Recharts)
- [ ] Micro-interactions
- [ ] Form validation
- [ ] Error states

### Week 4: Polish
- [ ] Performance optimization
- [ ] Accessibility (WCAG 2.1 AA)
- [ ] Mobile responsiveness
- [ ] Browser testing
- [ ] Storybook documentation

---

## Part 9: Performance Targets

### Core Web Vitals

| Metric | Target | Current |
|---|---|---|
| **First Contentful Paint (FCP)** | < 1.5s | - |
| **Largest Contentful Paint (LCP)** | < 2.5s | - |
| **Cumulative Layout Shift (CLS)** | < 0.1 | - |
| **Interaction to Next Paint (INP)** | < 200ms | - |
| **Time to Interactive (TTI)** | < 3.5s | - |

### Optimization Strategies

1. **Code Splitting**
   - Route-based splitting (Next.js)
   - Component lazy loading
   - Chart library dynamic import

2. **Image Optimization**
   - WebP format with fallbacks
   - Responsive images (srcset)
   - Lazy loading (intersection observer)

3. **Caching**
   - Browser caching (1 year for assets)
   - CDN caching (5 minutes for content)
   - Redis caching (API responses)

4. **Bundle Size**
   - Tree-shaking unused code
   - Minification & compression
   - Target: < 200KB gzipped

---

## Part 10: Accessibility

### WCAG 2.1 AA Compliance

**Color Contrast**
- Text: 4.5:1 minimum
- Large text (18px+): 3:1 minimum
- UI components: 3:1 minimum

**Keyboard Navigation**
- All interactive elements focusable
- Tab order logical
- Focus indicators visible
- Escape key closes modals

**Screen Readers**
- Semantic HTML (nav, main, section)
- ARIA labels for icons
- Form labels associated
- Live regions for updates

**Motion**
- Respects prefers-reduced-motion
- No auto-playing animations
- Pause/play controls for videos

---

## Conclusion

This frontend development plan provides:

✅ **Complete design system** (colors, typography, components)
✅ **Detailed page designs** (Feed, Search, Dashboard, Replay)
✅ **Animation system** (Framer Motion presets)
✅ **Responsive design** (mobile-first approach)
✅ **Performance targets** (Core Web Vitals)
✅ **Accessibility standards** (WCAG 2.1 AA)
✅ **Implementation roadmap** (4-week build plan)

**Your frontend team can follow this guide exactly to build a world-class UI that makes Foresight feel premium, powerful, and delightful.**
