import React from 'react'

interface HeroSectionProps {
  section: any
  trustBadges?: string[]
  productHref?: string
}

export function HeroSection({ section, trustBadges = [], productHref }: HeroSectionProps) {
  const content = section.content || {}

  return (
    <section className="hero">
      <div className="hero__inner">
        <h1 className="hero__headline">{content.headline}</h1>
        <p className="hero__subheadline">{content.subheadline}</p>

        <div className="hero__actions">
          <a href={productHref || '#'} className="btn btn-primary">
            {content.cta || 'Shop Now'}
          </a>
          <a href="#story" className="btn btn-secondary">
            Learn more
          </a>
        </div>

        {trustBadges.length > 0 && (
          <div className="hero__trust-row">
            {trustBadges.slice(0, 4).map((badge) => (
              <span key={badge}>
                <CheckIcon /> {badge}
              </span>
            ))}
          </div>
        )}
      </div>
    </section>
  )
}

function CheckIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M2 7.5L5.5 11L12 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
