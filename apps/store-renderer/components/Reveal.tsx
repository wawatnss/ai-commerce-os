import React, { useEffect, useRef, useState, ReactNode } from 'react'

interface RevealProps {
  children: ReactNode
  as?: keyof JSX.IntrinsicElements
  delay?: number
}

/**
 * Lightweight, dependency-free "fade in on scroll" wrapper.
 * - Uses IntersectionObserver (native, no library).
 * - Falls back to always-visible if IntersectionObserver isn't available
 *   or if the user prefers reduced motion, so content is never hidden.
 */
export function Reveal({ children, as = 'div', delay = 0 }: RevealProps) {
  const ref = useRef<HTMLElement | null>(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const node = ref.current
    if (!node) return

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (prefersReducedMotion || typeof IntersectionObserver === 'undefined') {
      setVisible(true)
      return
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setVisible(true)
            observer.disconnect()
          }
        })
      },
      { threshold: 0.15 }
    )

    observer.observe(node)
    return () => observer.disconnect()
  }, [])

  const Tag = as as any

  return (
    <Tag
      ref={ref}
      className={`reveal${visible ? ' is-visible' : ''}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </Tag>
  )
}
