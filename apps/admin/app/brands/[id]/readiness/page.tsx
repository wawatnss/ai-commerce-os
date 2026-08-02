import Link from 'next/link';
import { Heading, Text } from '@ai-commerce/ui';
import { AdminShell } from '@/components/AdminShell';
import { ReadinessReport } from '@/components/ReadinessReport';
import { API_URL } from '@/lib/api';

interface PageProps {
  params: { id: string };
}

export default async function BrandReadinessPage({ params }: PageProps) {
  const storeId = params.id;
  let report;
  let error;

  try {
    const response = await fetch(`${API_URL}/api/v1/stores/${storeId}/readiness`, {
      cache: 'no-store',
    });
    if (!response.ok) {
      throw new Error(`Failed to load readiness: ${response.statusText}`);
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
          Publication Readiness
        </Heading>
        <Text className="mt-1 text-gray-600">
          Vérifiez ce qui est prêt et ce qu&apos;il reste à configurer avant la mise en ligne.
        </Text>

        {error && (
          <div className="mt-6 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {report && (
          <div className="mt-6">
            <ReadinessReport report={report} />
            <div className="mt-4 flex gap-3">
              <a
                href={`${process.env.NEXT_PUBLIC_STORE_RENDERER_URL}/store-preview/${storeId}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex flex-1 items-center justify-center rounded-md bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
              >
                Voir la boutique
              </a>
              <a
                href={`${process.env.NEXT_PUBLIC_STORE_RENDERER_URL}/store-analysis/${storeId}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex flex-1 items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Voir l&apos;analyse
              </a>
            </div>
          </div>
        )}
      </div>
    </AdminShell>
  );
}
