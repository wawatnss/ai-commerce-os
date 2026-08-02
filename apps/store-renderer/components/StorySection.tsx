import React from 'react'
import { Reveal } from './Reveal'

interface StorySectionProps {
  storeName: string
  description?: string
  tagline?: string
  benefits?: string[]
}

export function StorySection({ storeName, description, tagline, benefits = [] }: StorySectionProps) {
  if (!description && benefits.length === 0) return null

  return (
    <section className="section" id="story">
      <div className="container">
        <Reveal>
          <div className="section-header" style={{ maxWidth: '720px' }}>
            <span className="eyebrow">Our Story</span>
            <h2 className="section-title">{tagline || `Why ${storeName}?`}</h2>
            {description && <p className="section-subtitle">{description}</p>}
          </div>
        </Reveal>

        {benefits.length > 0 && (
          <div className="grid grid-2" style={{ maxWidth: '760px', margin: '0 auto' }}>
            {benefits.map((benefit, index) => (
              <Reveal key={index} delay={index * 80}>
                <div className="card" style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                  <CheckBadge />
                  <span>{benefit}</span>
                </div>
              </Reveal>
            ))}
          </div>
        )}
      </div>
    </section>
  )
}

function CheckBadge() {
  return (
    <svg width="22" height="22" viewBox="0 0 22 22" fill="none" aria-hidden="true" style={{ flexShrink: 0 }}>
      <circle cx="11" cy="11" r="11" fill="var(--color-secondary)" />
      <path d="M6 11.5L9.2 14.5L16 7.5" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
