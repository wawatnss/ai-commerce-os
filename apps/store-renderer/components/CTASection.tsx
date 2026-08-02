import React from 'react'
import { Reveal } from './Reveal'

interface CTASectionProps {
  headline: string
  cta: string
  href?: string
}

export function CTASection({ headline, cta, href = '#' }: CTASectionProps) {
  return (
    <section className="section-tight">
      <Reveal>
        <div className="cta-banner">
          <h2 style={{ fontSize: 'clamp(1.5rem, 1.3rem + 1vw, 2rem)', marginBottom: 'var(--space-2)' }}>
            {headline}
          </h2>
          <a href={href} className="btn btn-primary">
            {cta}
          </a>
        </div>
      </Reveal>
    </section>
  )
}
