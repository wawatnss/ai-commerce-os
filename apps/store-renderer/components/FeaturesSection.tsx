import React from 'react'
import { Reveal } from './Reveal'

interface FeaturesSectionProps {
  section: any
}

const ICONS = [
  (
    <svg key="star" width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 2l2.9 6.6 7.1.6-5.4 4.7 1.7 7-6.3-3.9L5.7 21l1.7-7-5.4-4.7 7.1-.6L12 2z" fill="currentColor" />
    </svg>
  ),
  (
    <svg key="shield" width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 2l8 3v6c0 5-3.4 9.4-8 11-4.6-1.6-8-6-8-11V5l8-3z" fill="currentColor" />
    </svg>
  ),
  (
    <svg key="heart" width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M12 21s-7.5-4.6-10-9.3C.4 8 2.4 4 6.4 4c2 0 3.7 1.1 5.6 3 1.9-1.9 3.6-3 5.6-3 4 0 6 4 4.4 7.7C19.5 16.4 12 21 12 21z"
        fill="currentColor"
      />
    </svg>
  ),
]

export function FeaturesSection({ section }: FeaturesSectionProps) {
  const content = section.content || {}
  const features = content.features || []

  return (
    <section className="section" id="features">
      <div className="container">
        <div className="section-header">
          <span className="eyebrow">Why Choose Us</span>
          <h2 className="section-title">{section.title}</h2>
        </div>
        <div className="grid grid-3">
          {features.map((feature: string, index: number) => (
            <Reveal key={index} delay={index * 80}>
              <div className="card card-hover feature-card">
                <div className="feature-card__icon">{ICONS[index % ICONS.length]}</div>
                <h3 style={{ fontSize: '1.1rem' }}>{feature}</h3>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
