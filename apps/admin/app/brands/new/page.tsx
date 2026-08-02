'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button, Card, Heading, Input, Text } from '@ai-commerce/ui';
import { AdminShell } from '@/components/AdminShell';
import { ReadinessReport } from '@/components/ReadinessReport';
import type { ReadinessReport as ReadinessReportType } from '@/lib/api';

interface LaunchStep {
  key: string;
  label: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  detail?: string;
}

const CATEGORIES = [
  'electronics',
  'fashion',
  'home-goods',
  'beauty',
  'fitness',
  'outdoor',
  'food',
  'toys',
  'luxury',
];

const OBJECTIVES = [
  { value: 'sales', label: 'Maximiser les ventes / la marge' },
  { value: 'awareness', label: 'Construire la notoriété' },
  { value: 'speed', label: 'Lancer le plus vite possible' },
];

const BUDGETS = [
  { value: 'starter', label: 'Starter (< 2 000 €)' },
  { value: 'growth', label: 'Growth (2 000 - 10 000 €)' },
  { value: 'scale', label: 'Scale (> 10 000 €)' },
];

export default function NewBrandPage() {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    name: '',
    category: 'beauty',
    objective: 'sales',
    budget: 'growth',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<{
    success: boolean;
    storeId?: number;
    storeName?: string;
    steps: LaunchStep[];
    readiness?: ReadinessReportType;
    shopify_readiness?: ReadinessReportType;
    error?: string;
  } | null>(null);

  async function handleSubmit() {
    setIsSubmitting(true);
    try {
      const response = await fetch('/api/launch/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: form.name,
          category: form.category,
          objective: form.objective,
          budget: form.budget,
        }),
      });
      const data = await response.json();
      setResult({
        success: data.success,
        storeId: data.store_id,
        storeName: data.store_name,
        steps: data.steps,
        readiness: data.readiness,
        shopify_readiness: data.shopify_readiness,
        error: data.error,
      });
    } catch (err) {
      setResult({ success: false, steps: [], error: err instanceof Error ? err.message : 'Erreur inconnue' });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AdminShell>
      <div className="mx-auto max-w-2xl">
        <Link href="/" className="text-sm text-blue-600 hover:underline">
          &larr; Retour à Mes Marques
        </Link>
        <Heading level={1} className="mt-4 text-2xl font-bold">
          Créer une nouvelle marque
        </Heading>
        <Text className="mt-1 text-gray-600">
          Décrivez votre projet et laissez le moteur construire la boutique.
        </Text>

        <Card className="mt-8">
          {!result ? (
            <div className="space-y-6">
              {step === 1 && (
                <div className="space-y-4">
                  <label className="block text-sm font-medium text-gray-700">
                    Nom de la marque / produit
                    <Input
                      value={form.name}
                      onChange={(e) => setForm({ ...form, name: e.target.value })}
                      placeholder="Ex: Nova Skincare Serum"
                      className="mt-1"
                    />
                  </label>
                  <div className="flex justify-end">
                    <Button
                      disabled={form.name.length < 2 || isSubmitting}
                      onClick={() => setStep(2)}
                    >
                      Continuer
                    </Button>
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="space-y-4">
                  <label className="block text-sm font-medium text-gray-700">
                    Catégorie
                    <select
                      value={form.category}
                      onChange={(e) => setForm({ ...form, category: e.target.value })}
                      className="mt-1 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                    >
                      {CATEGORIES.map((c) => (
                        <option key={c} value={c}>
                          {c.charAt(0).toUpperCase() + c.slice(1)}
                        </option>
                      ))}
                    </select>
                  </label>
                  <div className="flex justify-between">
                    <Button variant="outline" onClick={() => setStep(1)}>
                      Retour
                    </Button>
                    <Button onClick={() => setStep(3)}>Continuer</Button>
                  </div>
                </div>
              )}

              {step === 3 && (
                <div className="space-y-4">
                  <label className="block text-sm font-medium text-gray-700">
                    Objectif principal
                    <select
                      value={form.objective}
                      onChange={(e) => setForm({ ...form, objective: e.target.value })}
                      className="mt-1 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                    >
                      {OBJECTIVES.map((o) => (
                        <option key={o.value} value={o.value}>
                          {o.label}
                        </option>
                      ))}
                    </select>
                  </label>
                  <div className="flex justify-between">
                    <Button variant="outline" onClick={() => setStep(2)}>
                      Retour
                    </Button>
                    <Button onClick={() => setStep(4)}>Continuer</Button>
                  </div>
                </div>
              )}

              {step === 4 && (
                <div className="space-y-4">
                  <label className="block text-sm font-medium text-gray-700">
                    Budget de lancement
                    <select
                      value={form.budget}
                      onChange={(e) => setForm({ ...form, budget: e.target.value })}
                      className="mt-1 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                    >
                      {BUDGETS.map((b) => (
                        <option key={b.value} value={b.value}>
                          {b.label}
                        </option>
                      ))}
                    </select>
                  </label>
                  <div className="flex justify-between">
                    <Button variant="outline" onClick={() => setStep(3)}>
                      Retour
                    </Button>
                    <Button
                      onClick={handleSubmit}
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? 'Création...' : 'Créer la marque'}
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              {result.error ? (
                <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
                  {result.error}
                </div>
              ) : (
                <>
                  <div className="text-center">
                    <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-green-100 text-green-700">
                      ✓
                    </div>
                    <Heading level={2} className="mt-4 text-lg font-semibold">
                      {result.storeName || 'Marque créée'}
                    </Heading>
                    <Text className="text-gray-600">Votre boutique est prête.</Text>
                  </div>

                  <div className="space-y-2">
                    {result.steps.map((s) => (
                      <div
                        key={s.key}
                        className="flex items-center justify-between rounded-md border border-gray-200 bg-gray-50 px-4 py-3 text-sm"
                      >
                        <span>{s.label}</span>
                        <StatusBadge status={s.status} />
                      </div>
                    ))}
                  </div>

                  {result.readiness && <ReadinessReport report={result.readiness} />}

                  {result.shopify_readiness && (
                    <div className="rounded-lg border border-purple-200 bg-purple-50 p-4">
                      <div className="mb-2 flex items-center justify-between">
                        <Heading level={3} className="text-base font-semibold text-purple-900">
                          Shopify Readiness
                        </Heading>
                        <span className="text-xl font-bold text-purple-900">
                          {result.shopify_readiness.overall_score} / 100
                        </span>
                      </div>
                      {result.shopify_readiness.is_ready ? (
                        <Text className="text-sm text-purple-700">
                          Boutique prête pour l&apos;import Shopify.
                        </Text>
                      ) : (
                        <Text className="text-sm text-purple-700">
                          Quelques vérifications restent nécessaires avant l&apos;export.
                        </Text>
                      )}
                    </div>
                  )}

                  <div className="flex flex-col gap-3 sm:flex-row">
                    <a
                      href={`${process.env.NEXT_PUBLIC_STORE_RENDERER_URL}/store-preview/${result.storeId}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex flex-1 items-center justify-center rounded-md bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
                    >
                      Voir la boutique
                    </a>
                    <a
                      href={`${process.env.NEXT_PUBLIC_STORE_RENDERER_URL}/store-analysis/${result.storeId}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex flex-1 items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
                    >
                      Voir l&apos;analyse
                    </a>
                  </div>
                </>
              )}
            </div>
          )}
        </Card>
      </div>
    </AdminShell>
  );
}

function StatusBadge({ status }: { status: LaunchStep['status'] }) {
  const styles = {
    pending: 'bg-gray-100 text-gray-600',
    running: 'bg-blue-100 text-blue-700',
    completed: 'bg-green-100 text-green-700',
    failed: 'bg-red-100 text-red-700',
  };
  const labels = {
    pending: 'En attente',
    running: 'En cours',
    completed: 'Terminé',
    failed: 'Échec',
  };
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${styles[status]}`}>
      {labels[status]}
    </span>
  );
}
