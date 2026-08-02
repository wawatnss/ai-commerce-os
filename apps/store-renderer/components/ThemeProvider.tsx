import React, { createContext, useContext, ReactNode } from 'react'
import { themeToCssVars, StoreTheme } from '@/lib/theme'

interface ThemeContextType {
  theme: StoreTheme
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ theme, children }: { theme: StoreTheme; children: ReactNode }) {
  return (
    <ThemeContext.Provider value={{ theme }}>
      {/* CSS custom properties bridge: every component below can rely on
          var(--color-primary) etc. from styles/globals.css instead of
          re-computing inline styles from the theme object. */}
      <div style={themeToCssVars(theme)}>{children}</div>
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context.theme
}
