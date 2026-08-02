import type { CSSProperties } from 'react'

export interface StoreTheme {
  primary_color?: string
  secondary_color?: string
  accent_color?: string
  background_color?: string
  text_color?: string
  border_radius?: string
  font_family?: string
  spacing?: string
  animations_enabled?: boolean
  dark_mode_enabled?: boolean
}

/**
 * Converts a store's theme (produced by apps/api's ThemeEngine) into CSS
 * custom properties. This is the bridge between the dynamic, per-store
 * theme data and the static premium design system in styles/globals.css:
 * components use `var(--color-primary)` etc. instead of repeating inline
 * styles, so the same CSS can be cached/shared across every store.
 */
export function themeToCssVars(theme: StoreTheme): CSSProperties {
  return {
    '--color-primary': theme.primary_color || '#2563EB',
    '--color-secondary': theme.secondary_color || '#10B981',
    '--color-accent': theme.accent_color || '#F59E0B',
    '--color-bg': theme.background_color || '#FFFFFF',
    '--color-text': theme.text_color || '#1F2937',
    '--radius': theme.border_radius || '12px',
    '--font-sans': theme.font_family ? `${theme.font_family}, var(--font-fallback)` : 'var(--font-fallback)',
    '--motion-enabled': theme.animations_enabled === false ? '0' : '1',
  } as CSSProperties
}
