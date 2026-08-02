import { Heading, Text } from '@ai-commerce/ui';
import { AdminShell } from '@/components/AdminShell';

const faqItems = [
  {
    q: 'Puis-je exporter vers Shopify ?',
    a: 'Oui. Ouvrez une boutique, puis cliquez sur Exporter → Shopify. Le fichier JSON est compatible avec les imports Shopify.',
  },
  {
    q: 'Combien de boutiques puis-je générer ?',
    a: 'Le plan Free permet 3 boutiques. Passez au plan Pro (25) ou Business (illimité) pour plus.',
  },
  {
    q: 'Mes clés API sont-elles sécurisées ?',
    a: 'Les clés OpenAI/Anthropic sont passées en variables d\'environnement et ne sont jamais exposées côté client.',
  },
  {
    q: 'Où sont stockées mes boutiques ?',
    a: 'Dans la base PostgreSQL configurée via DATABASE_URL. Les backups peuvent être faits avec docker/backup.sh.',
  },
  {
    q: 'Puis-je modifier le mot de passe ?',
    a: 'Oui. Allez dans Profil → Changer le mot de passe ou utilisez le endpoint /api/v1/auth/me/password.',
  },
  {
    q: 'Que faire si la génération échoue ?',
    a: 'Vérifiez le System Status (DB, Redis, clés API) et consultez les logs du conteneur api.',
  },
];

export default function FaqPage() {
  return (
    <AdminShell>
      <div className="mb-8">
        <Heading level={1}>FAQ</Heading>
        <Text className="mt-1 text-gray-600">
          Questions fréquentes sur l&apos;utilisation de la plateforme.
        </Text>
      </div>

      <div className="space-y-4">
        {faqItems.map((item, index) => (
          <div key={index} className="rounded-xl border border-gray-200 bg-white p-6">
            <Heading level={2} className="text-lg font-semibold">
              {item.q}
            </Heading>
            <Text className="mt-2 text-gray-600">{item.a}</Text>
          </div>
        ))}
      </div>
    </AdminShell>
  );
}
