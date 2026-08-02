/** @type {import('next').NextConfig} */
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const nextConfig = {
  reactStrictMode: true,
  basePath: process.env.ADMIN_BASE_PATH || '',
  output: 'standalone',
  poweredByHeader: false,
  transpilePackages: ['@ai-commerce/ui', '@ai-commerce/types', '@ai-commerce/shared'],
  images: {
    domains: ['localhost'],
  },
  env: {
    NEXT_PUBLIC_API_URL: API_URL,
    NEXT_PUBLIC_STORE_RENDERER_URL: process.env.NEXT_PUBLIC_STORE_RENDERER_URL || 'http://localhost:3002',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${API_URL}/api/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
