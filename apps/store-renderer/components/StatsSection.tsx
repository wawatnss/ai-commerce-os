import React from 'react'
import { Reveal } from './Reveal'

interface StatsSectionProps {
  policies?: {
    shipping_policy?: { free_shipping_threshold?: number; shipping_times?: { standard?: string } }
    refund_policy?: { days?: number }
  }
  reviewsModule?: { average_rating?: number | null; review_count?: number }
}

/**
 * Derives a small "why trust us" stats strip purely from data already
 * present on the blueprint (policies, reviews_module) - never invents
 * numbers. Sections with no backing data are simply omitted.
 */
export function StatsSection({ policies, reviewsModule }: StatsSectionProps) {
  const stats: { value: string; label: string }[] = []

  if (policies?.shipping_policy?.shipping_times?.standard) {
    stats.push({ value: policies.shipping_policy.shipping_times.standard, label: 'Shipping time' })
  }
  if (policies?.refund_policy?.days) {
    stats.push({ value: `${policies.refund_policy.days}-Day`, label: 'Return window' })
  }
  if (reviewsModule?.average_rating != null) {
    stats.push({ value: `${reviewsModule.average_rating.toFixed(1)}\u2605`, label: 'Average rating' })
  }
  if (policies?.shipping_policy?.free_shipping_threshold) {
    stats.push({ value: `$${policies.shipping_policy.free_shipping_threshold}+`, label: 'Free shipping' })
  }

  if (stats.length === 0) return null

  return (
    <section className="section-tight">
      <div className="container">
        <Reveal>
          <div className="stats-strip">
            {stats.map((stat) => (
              <div key={stat.label}>
                <div className="stats-strip__value">{stat.value}</div>
                <div className="stats-strip__label">{stat.label}</div>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  )
}
