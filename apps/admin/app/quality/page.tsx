import Link from 'next/link';
import { Heading, Text } from '@ai-commerce/ui';
import { AdminShell } from '@/components/AdminShell';
import { fetchValidationReport } from '@/lib/api';

function ScoreCard({ label, value, color }: { label: string; value: number; color?: string }) {
  const barColor = color || (value >= 90 ? 'bg-green-500' : value >= 70 ? 'bg-blue-500' : 'bg-yellow-500');
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5">
      <Text className="text-sm text-gray-500">{label}</Text>
      <div className="mt-2 text-3xl font-bold text-gray-900">{value}%</div>
      <div className="mt-3 h-2 w-full rounded-full bg-gray-100">
        <div className={`h-2 rounded-full ${barColor}`} style={{ width: `${Math.min(value, 100)}%` }} />
      </div>
    </div>
  );
}

function DistributionChart({ data }: { data: { range: string; count: number }[] }) {
  const max = Math.max(1, ...data.map((d) => d.count));
  return (
    <div className="space-y-2">
      {data.map((bucket) => (
        <div key={bucket.range} className="flex items-center gap-3">
          <div className="w-20 text-sm text-gray-600">{bucket.range}%</div>
          <div className="flex-1 rounded-full bg-gray-100">
            <div
              className="h-4 rounded-full bg-indigo-500"
              style={{ width: `${(bucket.count / max) * 100}%` }}
            />
          </div>
          <div className="w-8 text-right text-sm font-medium text-gray-900">{bucket.count}</div>
        </div>
      ))}
    </div>
  );
}

export default async function QualityPage() {
  const report = await fetchValidationReport();

  return (
    <AdminShell>
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <Heading level={1}>AI Quality Report</Heading>
          <Text className="mt-1 text-gray-600">
            Visual Identity, CTA Diversity, FAQ Diversity et Brand Diversity.
          </Text>
        </div>
        <Link href="/" className="text-sm text-blue-600 hover:underline">
          &larr; Retour à Mes Marques
        </Link>
      </div>

      {report ? (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <ScoreCard label="Overall Diversity" value={report.diversity.overall_diversity_score} color="bg-purple-500" />
            <ScoreCard label="Brand Diversity" value={report.diversity.brand_diversity} />
            <ScoreCard label="Prompt Diversity" value={report.diversity.prompt_diversity} />
            <ScoreCard label="Content Diversity" value={report.diversity.content_diversity} />
            <ScoreCard label="CTA Diversity" value={report.diversity.cta_diversity} />
            <ScoreCard label="FAQ Diversity" value={report.diversity.faq_diversity} />
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-xl border border-gray-200 bg-white p-6">
              <Heading level={2} className="text-lg font-semibold">
                Averages
              </Heading>
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                {Object.entries(report.averages).map(([label, value]) => (
                  <div key={label} className="flex items-center justify-between rounded-md bg-gray-50 px-4 py-2 text-sm">
                    <span className="font-medium text-gray-700">{label}</span>
                    <span className="font-semibold text-gray-900">{value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-xl border border-gray-200 bg-white p-6">
              <Heading level={2} className="text-lg font-semibold">
                Distribution
              </Heading>
              <div className="mt-4">
                <DistributionChart data={report.diversity.distribution} />
              </div>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <div className="rounded-xl border border-gray-200 bg-white p-5 text-center">
              <Text className="text-sm text-gray-500">Average Similarity</Text>
              <div className="mt-1 text-2xl font-bold text-gray-900">{report.diversity.average_similarity}%</div>
            </div>
            <div className="rounded-xl border border-gray-200 bg-white p-5 text-center">
              <Text className="text-sm text-gray-500">Best Case</Text>
              <div className="mt-1 text-2xl font-bold text-green-600">{report.diversity.best_case}%</div>
            </div>
            <div className="rounded-xl border border-gray-200 bg-white p-5 text-center">
              <Text className="text-sm text-gray-500">Worst Case</Text>
              <div className="mt-1 text-2xl font-bold text-red-600">{report.diversity.worst_case}%</div>
            </div>
          </div>

          {report.diversity.similar_pairs && report.diversity.similar_pairs.length > 0 && (
            <div className="rounded-xl border border-yellow-200 bg-yellow-50 p-6">
              <Heading level={2} className="text-lg font-semibold text-yellow-900">
                Similar pairs
              </Heading>
              <ul className="mt-4 space-y-3 text-sm text-yellow-800">
                {report.diversity.similar_pairs.slice(0, 10).map((pair, index) => (
                  <li key={index}>
                    <span className="font-medium">{pair.store_a}</span> vs{' '}
                    <span className="font-medium">{pair.store_b}</span>
                    <span className="ml-2 text-yellow-700">(similarity {pair.similarity})</span>
                    <br />
                    Why: {pair.reason} <br />
                    Fix: {pair.recommendation}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <div className="rounded-xl border-2 border-dashed border-gray-300 bg-white p-12 text-center">
          <Heading level={2} className="text-xl font-semibold">
            Aucun rapport de validation
          </Heading>
          <Text className="mt-2 text-gray-600">
            Lancez validation/run_validation_50.py puis validation/generate_report.py pour générer le rapport.
          </Text>
        </div>
      )}
    </AdminShell>
  );
}
