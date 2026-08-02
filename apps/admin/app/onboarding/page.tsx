import Link from 'next/link';
import { Heading, Text } from '@ai-commerce/ui';
import { AdminShell } from '@/components/AdminShell';

const steps = [
  {
    title: '1. Créer votre compte',
    desc: 'Inscrivez-vous avec votre email et un mot de passe sécurisé. Vous recevrez un token JWT pour accéder à l\'API.',
  },
  {
    title: '2. Choisir un produit',
    desc: 'Renseignez le nom de votre boutique, la catégorie (fitness, cuisine, tech...) et votre objectif (ventes, image de marque).',
  },
  {
    title: '3. Générer la boutique',
    desc: 'Le moteur IA crée la marque, le produit, le contenu, les CTA, la FAQ et l\'identité visuelle.',
  },
  {
    title: '4. Vérifier la qualité',
    desc: 'Consultez le rapport Qualité IA et le Readiness score. Utilisez l\'autofix Shopify si nécessaire.',
  },
  {
    title: '5. Exporter',
    desc: 'Téléchargez l\'export Shopify ou le blueprint JSON pour l\'intégrer à votre CMS.',
  },
];

export default function OnboardingPage() {
  return (
    <AdminShell>
      <div className="mb-8">
        <Heading level={1}>Bienvenue dans AI Commerce OS</Heading>
        <Text className="mt-1 text-gray-600">
          Voici les 5 étapes pour créer votre première boutique en moins de 2 minutes.
        </Text>
      </div>

      <div className="space-y-4">
        {steps.map((step) => (
          <div key={step.title} className="rounded-xl border border-gray-200 bg-white p-6">
            <Heading level={2} className="text-lg font-semibold">
              {step.title}
            </Heading>
            <Text className="mt-2 text-gray-600">{step.desc}</Text>
          </div>
        ))}
      </div>

      <div className="mt-8 text-center">
        <Link
          href="/brands/new"
          className="inline-flex items-center justify-center rounded-md bg-blue-600 px-6 py-3 text-sm font-medium text-white hover:bg-blue-700"
        >
          Créer ma première boutique
        </Link>
      </div>
    </AdminShell>
  );
}
