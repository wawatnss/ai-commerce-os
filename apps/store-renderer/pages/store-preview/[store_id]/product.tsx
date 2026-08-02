import { useState } from 'react'
import { GetServerSideProps } from 'next'
import Link from 'next/link'
import { ThemeProvider } from '@/components/ThemeProvider'
import { Header } from '@/components/Header'
import { Footer } from '@/components/Footer'
import { FAQSection } from '@/components/FAQSection'
import { TrustBadges } from '@/components/TrustBadges'
import { SEOHead } from '@/components/SEOHead'

interface ProductPageProps {
  storeId: string
  storeData?: any
  error?: string
}

const GALLERY_VIEWS = ['Front', 'Detail', 'Lifestyle', 'Packaging']

export default function ProductPage({ storeId, storeData, error }: ProductPageProps) {
  const [activeView, setActiveView] = useState(0)

  if (error) {
    return (
      <div style={{ padding: '80px 20px', textAlign: 'center' }}>
        <h1>Unable to load product</h1>
        <p>{error}</p>
      </div>
    )
  }

  if (!storeData) {
    return (
      <div style={{ padding: '80px 20px', textAlign: 'center' }}>
        <h1>Product not found</h1>
      </div>
    )
  }

  const blueprint = storeData.blueprint_json || storeData
  const theme = blueprint.theme || {}
  const productPage = blueprint.product_page || {}
  const policies = blueprint.policies || {}
  const trustBadges: string[] = blueprint.trust_badges || []
  const reviewsModule = blueprint.reviews_module
  const faq = blueprint.faq || []
  const benefits: string[] = productPage.benefits || []
  const features: string[] = productPage.features || []
  const comparison = productPage.comparison
  const cta = productPage.cta || 'Add to Cart'
  const productName = blueprint.store_name || 'This product'

  return (
    <ThemeProvider theme={theme}>
      <SEOHead
        seo={blueprint.seo}
        fallbackTitle={`${productName} | Product Details`}
        fallbackDescription={blueprint.store_description}
      />

      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Header navigation={blueprint.navigation || {}} storeName={blueprint.store_name} />

        <main id="main-content" className="section">
          <div className="container">
            <nav aria-label="Breadcrumb" style={{ marginBottom: 'var(--space-3)' }}>
              <Link href={`/store-preview/${storeId}`} className="text-muted">
                &larr; Back to {blueprint.store_name}
              </Link>
            </nav>

            <div className="product-layout">
              <div>
                <div className="product-gallery__main" role="img" aria-label={`${productName} - ${GALLERY_VIEWS[activeView]} view`}>
                  <span>{GALLERY_VIEWS[activeView]} view</span>
                </div>
                <div className="product-gallery__thumbs" role="tablist" aria-label="Product views">
                  {GALLERY_VIEWS.map((view, index) => (
                    <button
                      key={view}
                      type="button"
                      role="tab"
                      aria-selected={activeView === index}
                      className={`product-gallery__thumb${activeView === index ? ' is-active' : ''}`}
                      style={{ background: `linear-gradient(135deg, var(--color-primary), var(--color-secondary))` }}
                      onClick={() => setActiveView(index)}
                    >
                      <span className="visually-hidden">{view}</span>
                    </button>
                  ))}
                </div>
                <p className="placeholder-note mt-2">
                  Gallery shown with placeholder artwork generated from your brand colors.
                  Connect your product catalog to show real photos.
                </p>
              </div>

              <div>
                <h1 style={{ fontSize: 'clamp(1.75rem, 1.5rem + 1vw, 2.5rem)' }}>{productName}</h1>
                {blueprint.tagline && <p className="text-muted mt-1">{blueprint.tagline}</p>}

                <div className="placeholder-note mt-3">
                  Pricing will appear here once this store is connected to a product
                  catalog (price, variants, and inventory).
                </div>

                <button type="button" className="btn btn-primary btn-block mt-3">
                  {cta}
                </button>

                {trustBadges.length > 0 && (
                  <div className="trust-badges mt-3" style={{ justifyContent: 'flex-start' }}>
                    {trustBadges.slice(0, 3).map((badge) => (
                      <span key={badge} className="trust-badge">
                        {badge}
                      </span>
                    ))}
                  </div>
                )}

                {benefits.length > 0 && (
                  <div className="mt-4">
                    <h2 style={{ fontSize: '1.15rem', marginBottom: 'var(--space-1)' }}>Why you&rsquo;ll love it</h2>
                    <ul style={{ listStyle: 'none' }}>
                      {benefits.map((benefit, index) => (
                        <li key={index} style={{ marginBottom: '8px', display: 'flex', gap: '8px' }}>
                          <span aria-hidden="true">&#10003;</span> {benefit}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {features.length > 0 && (
                  <div className="mt-4">
                    <h2 style={{ fontSize: '1.15rem', marginBottom: 'var(--space-1)' }}>Specifications</h2>
                    <ul style={{ listStyle: 'none' }}>
                      {features.map((feature, index) => (
                        <li key={index} className="text-muted" style={{ marginBottom: '6px' }}>
                          &bull; {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {policies.shipping_policy && (
                  <div className="mt-4 card">
                    <h2 style={{ fontSize: '1rem', marginBottom: '6px' }}>Shipping &amp; Returns</h2>
                    <p className="text-muted" style={{ fontSize: '0.9rem' }}>
                      Standard shipping: {policies.shipping_policy.shipping_times?.standard || '5-7 business days'}.{' '}
                      {policies.refund_policy?.days
                        ? `${policies.refund_policy.days}-day returns.`
                        : ''}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {comparison && (
              <div className="section-tight">
                <h2 className="section-title text-center">How We Compare</h2>
                <table className="comparison-table">
                  <thead>
                    <tr>
                      <th scope="col">Criteria</th>
                      <th scope="col">{blueprint.store_name}</th>
                      <th scope="col">Typical competitor</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.keys(comparison.us || {}).map((key) => (
                      <tr key={key}>
                        <td style={{ textTransform: 'capitalize' }}>{key}</td>
                        <td>{comparison.us[key]}</td>
                        <td className="text-muted">{comparison.typical_competitor?.[key]}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {reviewsModule?.average_rating != null && (
              <div className="section-tight text-center">
                <div className="stars" aria-hidden="true">
                  {'\u2605'.repeat(Math.round(reviewsModule.average_rating))}
                </div>
                <p className="text-muted">
                  {reviewsModule.average_rating.toFixed(1)} out of 5 &middot; {reviewsModule.review_count} reviews
                  {reviewsModule.is_simulated ? ' (demo data)' : ''}
                </p>
              </div>
            )}
          </div>

          <FAQSection items={faq} />
        </main>

        <Footer footer={blueprint.footer || {}} storeName={blueprint.store_name} />
      </div>
    </ThemeProvider>
  )
}

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { store_id } = context.params ?? {}

  if (!store_id || typeof store_id !== 'string') {
    return { props: { storeId: '', error: 'Invalid store ID' } }
  }

  try {
    const response = await fetch(`http://localhost:8000/api/v1/stores/${store_id}`)
    if (!response.ok) {
      return { props: { storeId: store_id, error: `Failed to fetch store: ${response.statusText}` } }
    }
    const storeData = await response.json()
    return { props: { storeId: store_id, storeData } }
  } catch (error) {
    return {
      props: {
        storeId: store_id,
        error: `Error fetching store: ${error instanceof Error ? error.message : 'Unknown error'}`,
      },
    }
  }
}
