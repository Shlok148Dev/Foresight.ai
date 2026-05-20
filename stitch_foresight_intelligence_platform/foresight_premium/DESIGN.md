---
name: Foresight Premium
colors:
  surface: '#0f1419'
  surface-dim: '#0f1419'
  surface-bright: '#353a3f'
  surface-container-lowest: '#0a0f14'
  surface-container-low: '#171c21'
  surface-container: '#1b2025'
  surface-container-high: '#252a30'
  surface-container-highest: '#30353b'
  on-surface: '#dee3ea'
  on-surface-variant: '#bacac7'
  inverse-surface: '#dee3ea'
  inverse-on-surface: '#2c3136'
  outline: '#859492'
  outline-variant: '#3b4948'
  surface-tint: '#34dcd3'
  primary: '#49e9e0'
  on-primary: '#003734'
  primary-container: '#0ecdc4'
  on-primary-container: '#00524e'
  inverse-primary: '#006a65'
  secondary: '#c0c4e8'
  on-secondary: '#2a2f4a'
  secondary-container: '#454a67'
  on-secondary-container: '#b5badd'
  tertiary: '#ffc8a0'
  on-tertiary: '#4e2600'
  tertiary-container: '#ffa254'
  on-tertiary-container: '#713a00'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#5df9ef'
  primary-fixed-dim: '#34dcd3'
  on-primary-fixed: '#00201e'
  on-primary-fixed-variant: '#00504c'
  secondary-fixed: '#dee1ff'
  secondary-fixed-dim: '#c0c4e8'
  on-secondary-fixed: '#151a34'
  on-secondary-fixed-variant: '#404562'
  tertiary-fixed: '#ffdcc4'
  tertiary-fixed-dim: '#ffb77f'
  on-tertiary-fixed: '#2f1500'
  on-tertiary-fixed-variant: '#6f3800'
  background: '#0f1419'
  on-background: '#dee3ea'
  surface-variant: '#30353b'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '600'
    lineHeight: 44px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  xxl: 64px
  container-max: 1280px
  gutter: 24px
---

## Brand & Style

The brand identity centers on "Predictive Intelligence"—conveying a sense of forward-looking clarity and high-stakes precision. This design system targets analysts, executives, and trend-watchers who require a focused, high-signal environment.

The aesthetic follows a **Sleek Dark Mode** style with **Minimalist** and **Glassmorphic** influences. It prioritizes high-contrast content against a deep, expansive background to reduce cognitive load while emphasizing critical data points. The interface should feel expensive, technical, and authoritative, evoking the atmosphere of a command center for the future.

## Colors

This design system utilizes a high-contrast dark palette designed for long-form data consumption. 

- **Primary Teal (#0ECDC4):** Used exclusively for high-intent actions, active states, and critical trend indicators. It acts as the "light" in the dark environment.
- **Surface Layering:** The Deep Blue (#0F1419) serves as the canvas, while the Surface (#1A1F3A) provides structural containment for grouped information.
- **Typography Contrast:** Text Primary (#E0E7FF) ensures maximum legibility for data, while Text Secondary (#A0AEC0) handles metadata and supportive labels to maintain visual hierarchy.

## Typography

The system uses **Inter** exclusively to lean into its technical and systematic qualities. 

Headlines utilize tighter letter-spacing and heavier weights to create a strong presence. Body text is optimized for readability with generous line heights. For utility elements like trend categories or data labels, use the `label-caps` style to differentiate from narrative content. On mobile devices, Headline XL scales down significantly to prevent awkward word wrapping while maintaining its bold character.

## Layout & Spacing

The design system employs a **12-column fluid grid** for desktop and a **4-column grid** for mobile. 

The rhythm is dictated by an **8px base unit**. All margins and paddings must be multiples of 8. 
- **Desktop:** 24px gutters with 40px outer margins.
- **Tablet:** 16px gutters with 24px outer margins.
- **Mobile:** 16px gutters with 16px outer margins.

The layout philosophy emphasizes "Information Density" without "Visual Noise," using white space (or "dark space") to separate distinct trend modules rather than relying solely on lines.

## Elevation & Depth

Hierarchy is achieved through **Tonal Layering** and **Subtle Shadows**. 

1.  **Level 0 (Base):** Deep Blue (#0F1419) for the main viewport.
2.  **Level 1 (Cards):** Surface (#1A1F3A) with a 1px border (#2D3748). This creates a crisp definition against the base.
3.  **Level 2 (Modals/Popovers):** Surface (#1A1F3A) with a more pronounced shadow (0px 10px 30px rgba(0,0,0,0.5)) and a slightly lighter border to simulate physical proximity to the user.

Shadows should be dark and diffused, avoiding high-opacity blacks. Glassmorphism may be applied to navigation bars and sidebars using a backdrop filter (blur: 12px) and 80% opacity on the surface color.

## Shapes

The shape language is modern and approachable yet structured. 

- **Cards/Containers:** Use a 12px radius (`rounded-lg`) to soften the professional tone.
- **Buttons/Inputs:** Use an 8px radius for a more precise, functional appearance.
- **Pills/Chips/Tags:** Use a 20px radius (full pill) to distinguish them from interactive buttons.

This variation in corner radii helps users subconsciously categorize elements: large containers are structural, medium elements are functional, and fully rounded elements are informational.

## Components

### Buttons
- **Primary:** Background #0ECDC4, Text #0F1419, 8px radius.
- **Secondary:** Transparent background, 1px Border #2D3748, Text #E0E7FF.
- **Interactions:** Hover state triggers a `scale(1.02)` and a slight brightness increase. Active state triggers `scale(0.98)`. All transitions are set to `200ms ease-in-out`.

### Input Fields
- **Default:** Background #1A1F3A, 1px Border #2D3748, Text #E0E7FF, 8px radius.
- **Focus:** 1px Border #0ECDC4 with a subtle teal outer glow (0px 0px 8px rgba(14, 205, 196, 0.3)).

### Cards
- **Style:** Background #1A1F3A, 1px Border #2D3748, 12px radius. 
- **Hover:** Cards should elevate slightly with `scale(1.01)` and the border-color should shift to #A0AEC0 to indicate interactivity.

### Chips & Pills
- Used for trend categories and tags.
- Background #2D3748, Text #A0AEC0, 20px radius, Typography `body-sm`.

### Trends & Data Viz
- Use Primary Teal for positive trends/forecasts. 
- Charts should use a gradient stroke of Teal to Transparent for a "glow" effect.
- Grid lines in charts must use Border color (#2D3748) at 50% opacity.