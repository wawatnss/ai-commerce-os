import Head from 'next/head'
import Link from 'next/link'
import type { NextPage } from 'next'

const HomePage: NextPage = () => {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Store Renderer</h1>
      <p>Access store previews at: <code>/store-preview/[store_id]</code></p>
      <p>
        Want to see the whole platform in action? Try the{' '}
        <Link href="/demo">end-to-end demo</Link>.
      </p>
    </div>
  )
}

export default HomePage
