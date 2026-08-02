import Head from 'next/head'
import React from 'react'

interface SEOHeadProps {
  seo?: {
    title_template?: string
    meta_description_template?: string
    keywords?: string[]
    open_graph?: { og_title?: string; og_description?: string; og_type?: string; og_image?: string }
    json_ld?: Record<string, any>
    faq_schema?: Record<string, any>
  }
  fallbackTitle: string
  fallbackDescription?: string
  path?: string
}

/**
 * Renders <title>/meta/Open Graph/JSON-LD from the blueprint's `seo` block
 * (populated by apps/api's SEOOptimizer). Falls back to sensible defaults
 * derived from the store name/description if a store hasn't been optimized
 * yet, so every page always ships valid, non-empty SEO metadata.
 */
export function SEOHead({ seo, fallbackTitle, fallbackDescription, path }: SEOHeadProps) {
  const title = seo?.title_template || fallbackTitle
  const description = seo?.meta_description_template || fallbackDescription || fallbackTitle
  const og = seo?.open_graph

  return (
    <Head>
      <title>{title}</title>
      <meta name="description" content={description} />
      {seo?.keywords && seo.keywords.length > 0 && (
        <meta name="keywords" content={seo.keywords.join(', ')} />
      )}

      <meta property="og:title" content={og?.og_title || title} />
      <meta property="og:description" content={og?.og_description || description} />
      <meta property="og:type" content={og?.og_type || 'website'} />
      {path && <meta property="og:url" content={path} />}

      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={og?.og_title || title} />
      <meta name="twitter:description" content={og?.og_description || description} />

      {seo?.json_ld && (
        <script
          type="application/ld+json"
          // eslint-disable-next-line react/no-danger
          dangerouslySetInnerHTML={{ __html: JSON.stringify(seo.json_ld) }}
        />
      )}
      {seo?.faq_schema && (
        <script
          type="application/ld+json"
          // eslint-disable-next-line react/no-danger
          dangerouslySetInnerHTML={{ __html: JSON.stringify(seo.faq_schema) }}
        />
      )}
    </Head>
  )
}
