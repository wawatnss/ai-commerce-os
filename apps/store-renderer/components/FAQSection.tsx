import React from 'react'

interface FAQItem {
  question: string
  answer: string
}

interface FAQSectionProps {
  items: FAQItem[]
}

export function FAQSection({ items }: FAQSectionProps) {
  if (!items || items.length === 0) return null

  return (
    <section className="section section-alt" id="faq">
      <div className="container">
        <div className="section-header">
          <span className="eyebrow">FAQ</span>
          <h2 className="section-title">Frequently Asked Questions</h2>
        </div>
        <div className="faq">
          {items.map((item, index) => (
            <details key={index} className="faq-item" open={index === 0}>
              <summary>{item.question}</summary>
              <p>{item.answer}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  )
}
