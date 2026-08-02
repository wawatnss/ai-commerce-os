import React from 'react'
import { Reveal } from './Reveal'

interface TrustBadgesProps {
  badges: string[]
  title?: string
}

export function TrustBadges({ badges, title = 'Shop With Confidence' }: TrustBadgesProps) {
  if (!badges || badges.length === 0) return null

  return (
    <section className="section-tight" id="trust">
      <div className="container">
        <div className="section-header" style={{ marginBottom: 'var(--space-3)' }}>
          <h2 className="section-title" style={{ fontSize: '1.5rem' }}>{title}</h2>
        </div>
        <Reveal>
          <div className="trust-badges">
            {badges.map((badge) => (
              <span key={badge} className="trust-badge">
                <ShieldIcon /> {badge}
              </span>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  )
}

function ShieldIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 2l8 3v6c0 5-3.4 9.4-8 11-4.6-1.6-8-6-8-11V5l8-3z" fill="var(--color-secondary)" />
    </svg>
  )
}
