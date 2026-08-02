'use client';

import { useState } from 'react';
import { Button } from '@ai-commerce/ui';
import type { ReadinessReport } from '@/lib/api';

interface ShopifyActionsProps {
  storeId: string;
  report: ReadinessReport;
}

export function ShopifyActions({ storeId, report }: ShopifyActionsProps) {
  const [fixing, setFixing] = useState(false);

  async function handleAutofix() {
    setFixing(true);
    try {
      const response = await fetch(`/api/v1/stores/${storeId}/shopify-autofix`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`Auto-fix failed: ${response.statusText}`);
      }
      window.location.reload();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Erreur inconnue');
      setFixing(false);
    }
  }

  function handleExport() {
    window.open(`/api/v1/stores/${storeId}/export/shopify`, '_blank');
  }

  return (
    <div className="space-y-4">
      {!report.is_ready && (
        <Button
          onClick={handleAutofix}
          disabled={fixing}
          className="w-full"
        >
          {fixing ? 'Correction en cours...' : 'Corriger automatiquement ce qui peut l\'être'}
        </Button>
      )}

      <div className="flex gap-3">
        <Button
          onClick={handleExport}
          disabled={!report.is_ready}
          className="flex-1 bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-50"
        >
          Exporter vers Shopify
        </Button>
        <a
          href={`${process.env.NEXT_PUBLIC_STORE_RENDERER_URL}/store-preview/${storeId}`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex flex-1 items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Voir la boutique
        </a>
      </div>
    </div>
  );
}
