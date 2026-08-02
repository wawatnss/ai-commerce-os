import React from 'react'
import Link from 'next/link'
import { ThemeProvider } from './ThemeProvider'
import { Header } from './Header'
import { Footer } from './Footer'
import { HeroSection } from './HeroSection'
import { FeaturesSection } from './FeaturesSection'
import { TestimonialsSection } from './TestimonialsSection'
import { TrustBadges } from './TrustBadges'
import { StatsSection } from './StatsSection'
import { StorySection } from './StorySection'
import { FAQSection } from './FAQSection'
import { CTASection } from './CTASection'
import { SEOHead } from './SEOHead'

interface StorePreviewProps {
  storeData: any
}

export function StorePreview({ storeData }: StorePreviewProps) {
  const blueprint = storeData.blueprint_json || storeData
  const theme = blueprint.theme || {}
  const homepage = blueprint.homepage || []
  const navigation = blueprint.navigation || {}
  const footer = blueprint.footer || {}
  const trustBadges: string[] = blueprint.trust_badges || []
  const reviewsModule = blueprint.reviews_module
  const productHref = storeData.id ? `/store-preview/${storeData.id}/product` : undefined

  return (
    <ThemeProvider theme={theme}>
      <SEOHead
        seo={blueprint.seo}
        fallbackTitle={`${blueprint.store_name || 'Store'} | ${blueprint.tagline || 'Shop Now'}`}
        fallbackDescription={blueprint.store_description}
      />

      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      {storeData.id && (
        <Link
          href={`/store-analysis/${storeData.id}`}
          style={{
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            zIndex: 50,
            backgroundColor: 'var(--color-text)',
            color: '#FFFFFF',
            padding: '10px 18px',
            borderRadius: '999px',
            fontSize: '13px',
            fontWeight: 'bold',
            boxShadow: 'var(--shadow-md)',
          }}
        >
          View Conversion Analysis
        </Link>
      )}

      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Header navigation={navigation} storeName={blueprint.store_name} />

        <main id="main-content" style={{ flex: 1 }}>
          {homepage.map((section: any, index: number) => {
            switch (section.section_type) {
              case 'hero':
                return (
                  <HeroSection
                    key={index}
                    section={section}
                    trustBadges={trustBadges}
                    productHref={productHref}
                  />
                )
              case 'features':
                return <FeaturesSection key={index} section={section} />
              case 'testimonials':
                return <TestimonialsSection key={index} section={section} reviewsModule={reviewsModule} />
              default:
                // "trust" sections are rendered once, below, via <TrustBadges>
                // using blueprint.trust_badges directly (avoids duplication).
                return null
            }
          })}

          <StorySection
            storeName={blueprint.store_name}
            description={blueprint.store_description}
            tagline={blueprint.tagline}
            benefits={blueprint.product_page?.benefits}
          />

          <StatsSection policies={blueprint.policies} reviewsModule={reviewsModule} />

          <TrustBadges badges={trustBadges} />

          <FAQSection items={blueprint.faq} />

          <CTASection
            headline={`Ready to try ${blueprint.store_name || 'us'}?`}
            cta={homepage.find((s: any) => s.section_type === 'hero')?.content?.cta || 'Shop Now'}
            href={productHref}
          />
        </main>

        <Footer footer={footer} storeName={blueprint.store_name} />
      </div>
    </ThemeProvider>
  )
}
