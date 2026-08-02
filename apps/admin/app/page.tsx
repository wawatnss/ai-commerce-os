import Link from 'next/link';
import { Button, Heading, Text } from '@ai-commerce/ui';
import { AdminShell } from '@/components/AdminShell';
import { BrandCard } from '@/components/BrandCard';
import { fetchStores, fetchDashboardStats } from '@/lib/api';

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5">
      <Text className="text-sm text-gray-500">{label}</Text>
      <div className="mt-1 text-2xl font-bold text-gray-900">{value}</div>
    </div>
  );
}

export default async function DashboardPage() {
  let brands;
  let stats;
  let error: string | null = null;

  try {
    brands = await fetchStores();
  } catch (err) {
    error = err instanceof Error ? err.message : 'Erreur inconnue';
    brands = { items: [], total: 0, page: 1, page_size: 50 };
  }

  try {
    stats = await fetchDashboardStats();
  } catch {
    stats = null;
  }

  return (
    <AdminShell>
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <Heading level={1}>Tableau de bord</Heading>
          <Text className="mt-1 text-gray-600">
            Vue d&apos;ensemble de l&apos;activité et des boutiques générées.
          </Text>
        </div>
        <div className="flex gap-3">
          <Link
            href="/quality"
            className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Qualité IA
          </Link>
          <Link
            href="/system"
            className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Système
          </Link>
          <Link href="/brands/new" className="inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700">
            Créer une nouvelle marque
          </Link>
        </div>
      </div>

      {error && (
        <div className="mb-6 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {stats && (
        <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Boutiques générées" value={stats.total_stores} />
          <StatCard label="Score moyen" value={stats.average_validation_score} />
          <StatCard label="Générations IA" value={stats.ai_usage_count} />
          <StatCard label="Plan le plus courant" value="Free" />
        </div>
      )}

      {stats && stats.recent_stores.length > 0 && (
        <div className="mb-8 rounded-xl border border-gray-200 bg-white p-6">
          <Heading level={2} className="text-lg font-semibold">
            Dernières générations
          </Heading>
          <ul className="mt-4 space-y-3">
            {stats.recent_stores.map((store) => (
              <li key={store.id} className="flex items-center justify-between rounded-md bg-gray-50 px-4 py-3 text-sm">
                <span className="font-medium text-gray-900">{store.store_name}</span>
                <div className="flex items-center gap-4 text-gray-600">
                  <span>Score: {store.validation_score}</span>
                  <span>{new Date(store.created_at).toLocaleDateString()}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <Heading level={2} className="mb-4 text-lg font-semibold">
        Mes Marques
      </Heading>

      {brands.items.length === 0 ? (
        <div className="rounded-xl border-2 border-dashed border-gray-300 bg-white p-12 text-center">
          <Heading level={2} className="text-xl font-semibold">
            Aucune marque pour l&apos;instant
          </Heading>
          <Text className="mt-2 text-gray-600">
            Commencez par créer votre première boutique en quelques clics.
          </Text>
          <div className="mt-6 flex flex-wrap justify-center gap-4 text-sm text-gray-500">
            <span className="rounded-full bg-gray-100 px-3 py-1">Nike Style</span>
            <span className="rounded-full bg-gray-100 px-3 py-1">Apple Style</span>
            <span className="rounded-full bg-gray-100 px-3 py-1">Outdoor</span>
            <span className="rounded-full bg-gray-100 px-3 py-1">Minimal</span>
            <span className="rounded-full bg-gray-100 px-3 py-1">Luxury</span>
          </div>
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {brands.items.map((brand) => (
            <BrandCard key={brand.id} brand={brand} />
          ))}
        </div>
      )}
    </AdminShell>
  );
}
