import Link from 'next/link';
import { Heading, Text } from '@ai-commerce/ui';
import { AdminShell } from '@/components/AdminShell';
import { ReadinessReport } from '@/components/ReadinessReport';
import { ShopifyActions } from '@/components/ShopifyActions';
import { API_URL } from '@/lib/api';

interface PageProps {
  params: { id: string };
}

export default async function ShopifyReadinessPage({ params }: PageProps) {
  const storeId = params.id;
  let report;
  let error;

  try {
    const response = await fetch(`${API_URL}/api/v1/stores/${storeId}/shopify-readiness`, {
      cache: 'no-store',
    });
    if (!response.ok) {
      throw new Error(`Failed to load Shopify readiness: ${response.statusText}`);
    }
    report = await response.json();
  } catch (err) {
    error = err instanceof Error ? err.message : 'Erreur inconnue';
  }

  return (
    <AdminShell>
      <div className="mx-auto max-w-2xl">
        <Link href="/" className="text-sm text-blue-600 hover:underline">
          &larr; Retour à Mes Marques
        </Link>
        <Heading level={1} className="mt-4 text-2xl font-bold">
          Shopify Readiness
        </Heading>
        <Text className="mt-1 text-gray-600">
          Vérifiez si la boutique est suffisamment complète pour être importée sur Shopify.
        </Text>

        {error && (
          <div className="mt-6 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {report && (
          <div className="mt-6 space-y-6">
            <ReadinessReport
              report={report}
              title="Shopify Readiness"
              subtitle={report.is_ready ? "Prêt pour l'import Shopify" : "Actions requises avant l'import Shopify"}
            />

            <div className="rounded-lg border border-purple-200 bg-purple-50 p-4 text-sm text-purple-800">
              <p className="font-medium">Pourquoi pas 100/100 ?</p>
              <p className="mt-1">
                Les taxes, images et connecteurs Shopify ne peuvent être entièrement automatisés.
                L&apos;auto-correction remplit les variantes, collections, navigation et taxes (placeholder).
              </p>
            </div>

            <ShopifyActions storeId={storeId} report={report} />
          </div>
        )}
      </div>
    </AdminShell>
  );
}
