# Store Renderer

Next.js application that renders store blueprints into navigable e-commerce stores.

## Development

```bash
cd apps/store-renderer
npm install
npm run dev
```

The renderer will be available at http://localhost:3002 (apps/web already uses
3000 and apps/admin uses 3001, see docker/docker-compose.yml).

## Preview Store

Access a store preview at:
```
http://localhost:3002/store-preview/{store_id}
```

The renderer fetches the store blueprint from the API at http://localhost:8000/api/v1/stores/{store_id}

## Demo Mode (Phase 7.5)

Visit `http://localhost:3002/demo` and click **Generate Demo Store** to run
the whole platform pipeline end-to-end (Trend -> Product -> Supplier -> Brand
-> Store -> Preview) without any external API. See [PHASE7_5_REPORT.md](../../PHASE7_5_REPORT.md)
at the repo root for details.

## Conversion Analysis (Phase 8)

Visit `http://localhost:3002/store-analysis/{store_id}` to see a store's
conversion, SEO, UX, trust and persuasion scores, plus every recommended
action from the Conversion Optimization Engine. Click **Run Optimization**
to (re)apply it and persist the improved blueprint. A "View Conversion
Analysis" link is also available on every `/store-preview/{store_id}` page.
See [PHASE8_REPORT.md](../../PHASE8_REPORT.md) at the repo root for details.

## Components

- **StorePreview**: Main component that renders the complete store
- **ThemeProvider**: Applies the theme from the store blueprint
- **Header**: Dynamic navigation header
- **Footer**: Dynamic footer
- **HeroSection**: Hero section with CTA
- **FeaturesSection**: Features grid
- **TestimonialsSection**: Customer testimonials

## Dynamic Rendering

All components are fully dynamic and use data from the store blueprint:
- Colors and typography from theme
- Navigation structure from blueprint
- Homepage sections from blueprint
- Footer content from blueprint
