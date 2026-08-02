import React from 'react'

interface FooterColumn {
  title: string
  links?: { label: string; link: string }[]
}

interface FooterProps {
  footer: {
    columns?: FooterColumn[]
    copyright?: string
    social_links?: Record<string, boolean>
  }
  storeName?: string
}

const SOCIAL_LABELS: Record<string, string> = {
  instagram: 'Instagram',
  facebook: 'Facebook',
  twitter: 'Twitter',
}

export function Footer({ footer, storeName }: FooterProps) {
  const columns = footer.columns || []
  const socials = Object.entries(footer.social_links || {}).filter(([, enabled]) => enabled)

  return (
    <footer className="site-footer">
      <div className="container">
        <div className="site-footer__grid">
          <div>
            {storeName && <div className="site-footer__brand">{storeName}</div>}
            {socials.length > 0 && (
              <ul style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
                {socials.map(([key]) => (
                  <li key={key}>
                    <a href="#" aria-label={SOCIAL_LABELS[key] || key} style={{ marginBottom: 0 }}>
                      {SOCIAL_LABELS[key] || key}
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {columns.map((column, index) => (
            <div key={index}>
              <h3>{column.title}</h3>
              <ul>
                {column.links?.map((link, linkIndex) => (
                  <li key={linkIndex}>
                    <a href={link.link}>{link.label}</a>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          <div>
            <h3>We Accept</h3>
            <div className="payment-icons">
              {['Visa', 'Mastercard', 'PayPal', 'Apple Pay'].map((method) => (
                <span key={method}>{method}</span>
              ))}
            </div>
          </div>
        </div>

        <div className="site-footer__bottom">
          <span>{footer.copyright}</span>
          <span>Secured checkout &middot; SSL encrypted</span>
        </div>
      </div>
    </footer>
  )
}
