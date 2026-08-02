import { GetServerSideProps } from 'next'
import { StorePreview } from '@/components/StorePreview'

interface StorePreviewPageProps {
  storeData: any
  error?: string
}

export default function StorePreviewPage({ storeData, error }: StorePreviewPageProps) {
  if (error) {
    return (
      <div className="section text-center">
        <h1>Error Loading Store</h1>
        <p className="text-muted mt-2">{error}</p>
      </div>
    )
  }

  if (!storeData) {
    return (
      <div className="section text-center">
        <h1>Store Not Found</h1>
        <p className="text-muted mt-2">The requested store could not be found.</p>
      </div>
    )
  }

  return <StorePreview storeData={storeData} />
}

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { store_id } = context.params ?? {}

  if (!store_id || typeof store_id !== 'string') {
    return {
      props: {
        error: 'Invalid store ID'
      }
    }
  }

  try {
    // Fetch store blueprint from API
    const response = await fetch(`http://localhost:8000/api/v1/stores/${store_id}`)
    
    if (!response.ok) {
      return {
        props: {
          error: `Failed to fetch store: ${response.statusText}`
        }
      }
    }

    const storeData = await response.json()

    return {
      props: {
        storeData
      }
    }
  } catch (error) {
    return {
      props: {
        error: `Error fetching store: ${error instanceof Error ? error.message : 'Unknown error'}`
      }
    }
  }
}
