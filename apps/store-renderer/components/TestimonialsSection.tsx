import React from 'react'
import { Reveal } from './Reveal'

interface TestimonialsSectionProps {
  section: any
  reviewsModule?: {
    average_rating?: number | null
    review_count?: number
    is_simulated?: boolean
  }
}

export function TestimonialsSection({ section, reviewsModule }: TestimonialsSectionProps) {
  const content = section.content || {}
  const hasRating = reviewsModule?.average_rating != null

  return (
    <section className="section section-alt" id="reviews">
      <div className="container">
        <div className="section-header">
          <span className="eyebrow">Social Proof</span>
          <h2 className="section-title">{section.title}</h2>
        </div>

        <Reveal>
          <div className="testimonial-card card">
            <p className="testimonial-card__quote">&ldquo;{content.testimonial}&rdquo;</p>
            <div className="stars" aria-label={`${content.rating || 5} out of 5 stars`}>
              {'\u2605'.repeat(content.rating || 5)}
            </div>
          </div>
        </Reveal>

        {hasRating && (
          <div className="stats-strip mt-4">
            <div>
              <div className="stats-strip__value">{reviewsModule!.average_rating!.toFixed(1)}\u2605</div>
              <div className="stats-strip__label">
                Average rating{reviewsModule?.is_simulated ? ' (demo)' : ''}
              </div>
            </div>
            <div>
              <div className="stats-strip__value">{reviewsModule?.review_count ?? 0}</div>
              <div className="stats-strip__label">Customer reviews</div>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}
