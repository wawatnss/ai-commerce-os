import { Heading, Text } from '@ai-commerce/ui';
import type { ReadinessReport as ReadinessReportType } from '@/lib/api';

interface ReadinessReportProps {
  report: ReadinessReportType;
  title?: string;
  subtitle?: string;
}

export function ReadinessReport({
  report,
  title = 'Publication Readiness',
  subtitle,
}: ReadinessReportProps) {
  const statusIcon = {
    pass: '✓',
    partial: '◐',
    fail: '✗',
  };
  const statusClass = {
    pass: 'text-green-600',
    partial: 'text-yellow-600',
    fail: 'text-red-600',
  };

  const defaultSubtitle = report.is_ready
    ? 'Prêt pour la publication'
    : 'Actions requises avant publication';

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <Heading level={3} className="text-base font-semibold">
            {title}
          </Heading>
          <Text className="text-sm text-gray-500">{subtitle ?? defaultSubtitle}</Text>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-gray-900">{report.overall_score} / 100</div>
          <div className="text-xs text-gray-500">Score global</div>
        </div>
      </div>

      <div className="space-y-2">
        {report.checks.map((check) => (
          <div key={check.key} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <span className={statusClass[check.status]}>{statusIcon[check.status]}</span>
              <span>{check.label}</span>
            </div>
            <span className="text-gray-500">
              {check.score}/{check.max_score}
            </span>
          </div>
        ))}
      </div>

      {report.remaining_actions.length > 0 && (
        <div className="mt-5 border-t border-gray-100 pt-4">
          <Heading level={4} className="text-sm font-semibold">
            Actions restantes
          </Heading>
          <ul className="mt-2 space-y-1.5 text-sm text-gray-600">
            {report.remaining_actions.map((action, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-yellow-600">⚠</span>
                {action}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
