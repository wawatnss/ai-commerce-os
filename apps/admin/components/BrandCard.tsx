import { Card, Badge, Heading, Text } from '@ai-commerce/ui';
import Link from 'next/link';
import { STORE_RENDERER_URL } from '@/lib/api';
import type { StoreListItem } from '@/lib/api';

interface BrandCardProps {
  brand: StoreListItem;
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

function getScoreColor(score: number) {
  if (score >= 80) return 'success' as const;
  if (score >= 60) return 'info' as const;
  return 'warning' as const;
}

export function BrandCard({ brand }: BrandCardProps) {
  const readiness = brand.readiness;
  const shopify = brand.shopify_readiness;
  const score = readiness?.overall_score ?? brand.validation_score ?? 0;

  const report = brand.blueprint_json?.conversion_report;

  return (
    <Card className="flex h-full flex-col">
      <div className="mb-4 flex items-start justify-between">
        <div>
          <Heading level={3} className="text-lg font-semibold">
            {brand.store_name}
          </Heading>
          {brand.tagline ? (
            <Text className="mt-1 text-sm text-gray-600">{brand.tagline}</Text>
          ) : (
            <Text className="mt-1 text-sm text-gray-600 line-clamp-2">{brand.store_description}</Text>
          )}
        </div>
        <div className="text-right">
          <Badge variant={getScoreColor(score)}>{Math.round(score)}</Badge>
          <Text className="mt-1 text-xs text-gray-500">
            {readiness?.is_ready ? 'Prêt' : 'En cours'}
          </Text>
        </div>
      </div>

      <div className="mb-4 grid grid-cols-2 gap-3 text-sm text-gray-600">
        <div>
          <span className="block text-xs text-gray-400">SEO</span>
          {Math.round(report?.seo_score ?? 0)}
        </div>
        <div>
          <span className="block text-xs text-gray-400">UX</span>
          {Math.round(report?.ux_score ?? 0)}
        </div>
        <div>
          <span className="block text-xs text-gray-400">Trust</span>
          {Math.round(report?.trust_score ?? 0)}
        </div>
        <div>
          <span className="block text-xs text-gray-400">Créée</span>
          {formatDate(brand.created_at)}
        </div>
      </div>

      {shopify && (
        <div className="mb-4 rounded-md border border-purple-100 bg-purple-50 px-3 py-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-purple-900">Shopify Readiness</span>
            <span className="font-semibold text-purple-900">
              {Math.round(shopify.overall_score)} / 100
            </span>
          </div>
        </div>
      )}

      <div className="mt-auto grid grid-cols-2 gap-2">
        <a
          href={`${STORE_RENDERER_URL}/store-preview/${brand.id}`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Voir la boutique
        </a>
        <Link
          href={`/brands/${brand.id}/shopify`}
          className="inline-flex items-center justify-center rounded-md border border-purple-600 bg-white px-3 py-2 text-sm font-medium text-purple-700 hover:bg-purple-50"
        >
          Exporter
        </Link>
      </div>
    </Card>
  );
}
