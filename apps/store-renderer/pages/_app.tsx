import '../styles/globals.css'
import type { AppProps } from 'next/app'
import { Inter } from 'next/font/google'

// Self-hosted via next/font: no external font request, no layout shift,
// automatically preloaded and subset. Exposed as a CSS variable consumed by
// styles/globals.css (--font-fallback).
const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-fallback',
})

export default function App({ Component, pageProps }: AppProps) {
  return (
    <div className={inter.variable}>
      <Component {...pageProps} />
    </div>
  )
}
