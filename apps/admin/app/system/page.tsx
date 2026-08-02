import Link from 'next/link';
import { Heading, Text } from '@ai-commerce/ui';
import { AdminShell } from '@/components/AdminShell';
import { fetchSystemStatus } from '@/lib/api';

function StatusBadge({ status }: { status: string }) {
  const ok = status === 'ok' || status === 'healthy';
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
        ok ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
      }`}
    >
      {status}
    </span>
  );
}

export default async function SystemPage() {
  const status = await fetchSystemStatus();

  return (
    <AdminShell>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <Heading level={1}>System Status</Heading>
          <Text className="mt-1 text-gray-600">
            Santé de l&apos;API, de la base de données, de Redis et des temps de réponse.
          </Text>
        </div>
        <Link href="/" className="text-sm text-blue-600 hover:underline">
          &larr; Tableau de bord
        </Link>
      </div>

      {status ? (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-xl border border-gray-200 bg-white p-5">
              <Text className="text-sm text-gray-500">API</Text>
              <div className="mt-2 flex items-center gap-2">
                <StatusBadge status={status.health.status} />
                <span className="text-sm text-gray-700">{status.health.app} v{status.health.version}</span>
              </div>
            </div>
            <div className="rounded-xl border border-gray-200 bg-white p-5">
              <Text className="text-sm text-gray-500">PostgreSQL</Text>
              <div className="mt-2">
                <StatusBadge status={status.health.database.status} />
              </div>
            </div>
            <div className="rounded-xl border border-gray-200 bg-white p-5">
              <Text className="text-sm text-gray-500">Redis</Text>
              <div className="mt-2">
                <StatusBadge status={status.health.redis.status} />
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <Heading level={2} className="text-lg font-semibold">
              Temps de génération moyens
            </Heading>
            <div className="mt-4 space-y-2">
              {Object.entries(status.metrics).slice(0, 10).map(([key, m]) => (
                <div key={key} className="flex items-center justify-between rounded-md bg-gray-50 px-4 py-2 text-sm">
                  <span className="font-medium text-gray-700">{key}</span>
                  <span className="text-gray-600">
                    {m.count} req — avg {m.avg_ms}ms — errors {m.errors}
                  </span>
                </div>
              ))}
              {Object.keys(status.metrics).length === 0 && (
                <Text className="text-sm text-gray-500">Aucune métrique encore collectée.</Text>
              )}
            </div>
          </div>

          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <Heading level={2} className="text-lg font-semibold">
              Environnement
            </Heading>
            <div className="mt-4 grid gap-4 sm:grid-cols-3">
              <div className="text-sm">
                <span className="font-medium text-gray-700">Debug :</span>{' '}
                <span className={status.environment.debug ? 'text-red-600' : 'text-green-600'}>
                  {status.environment.debug ? 'OUI' : 'NON'}
                </span>
              </div>
              <div className="text-sm">
                <span className="font-medium text-gray-700">Log level :</span>{' '}
                {status.environment.log_level}
              </div>
              <div className="text-sm">
                <span className="font-medium text-gray-700">Rate limit :</span>{' '}
                {status.environment.rate_limit_per_minute} req/min
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="rounded-xl border border-red-200 bg-red-50 p-8 text-center">
          <Heading level={2} className="text-lg font-semibold text-red-900">
            API inaccessible
          </Heading>
          <Text className="mt-2 text-red-700">
            Vérifiez que le conteneur FastAPI est démarré et que NEXT_PUBLIC_API_URL est correct.
          </Text>
        </div>
      )}
    </AdminShell>
  );
}
