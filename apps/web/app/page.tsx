"use client";

import Link from 'next/link';
import { Button, Container, Heading, Section, Text } from '@ai-commerce/ui';

function CheckIcon() {
  return (
    <svg className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
  );
}

function XIcon() {
  return (
    <svg className="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-white text-gray-900">
      {/* Hero */}
      <Section className="bg-gradient-to-br from-slate-900 to-slate-800 text-white py-24">
        <Container className="text-center">
          <span className="inline-block rounded-full bg-blue-600/20 px-4 py-1 text-sm font-medium text-blue-300">
            v1.0.0-beta
          </span>
          <Heading level={1} className="mx-auto mt-6 max-w-4xl text-5xl font-extrabold leading-tight">
            Lancez une boutique e-commerce prête à vendre en 5 minutes.
          </Heading>
          <Text variant="lead" className="mx-auto mt-6 max-w-2xl text-lg text-slate-300">
            Zéro code. Zéro agence. Zéro blanc sur la page. AI Commerce OS génère votre marque, votre produit,
            votre contenu et votre export Shopify en quelques clics.
          </Text>
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              href="/admin"
              className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-8 py-4 text-lg font-semibold text-white hover:bg-blue-700"
            >
              Commencer gratuitement
            </Link>
            <Link
              href="#demo"
              className="inline-flex items-center justify-center rounded-lg border border-slate-500 bg-transparent px-8 py-4 text-lg font-semibold text-white hover:bg-slate-700"
            >
              Voir la démo
            </Link>
          </div>
          <p className="mt-4 text-sm text-slate-400">Carte bancaire non requise. 3 boutiques offertes.</p>
        </Container>
      </Section>

      {/* Demo */}
      <Section id="demo" className="py-20">
        <Container>
          <Heading level={2} className="text-center text-3xl font-bold">
            De l&apos;idée à la boutique en 3 étapes
          </Heading>
          <div className="mt-12 grid gap-8 md:grid-cols-3">
            {[
              {
                step: '1',
                title: 'Décrivez votre projet',
                desc: 'Choisissez un nom, une catégorie et un objectif. Pas de code, pas de brief agence.',
              },
              {
                step: '2',
                title: 'L&apos;IA génère tout',
                desc: 'Marque, produit, fournisseur, contenu, CTA, FAQ, identité visuelle. Prêt à publier.',
              },
              {
                step: '3',
                title: 'Exportez vers Shopify',
                desc: 'Téléchargez le fichier JSON compatible Shopify et importez-le en 1 clic.',
              },
            ].map((item) => (
              <div key={item.step} className="rounded-2xl border border-slate-200 bg-slate-50 p-8">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-600 text-xl font-bold text-white">
                  {item.step}
                </div>
                <Heading level={3} className="mt-4 text-xl font-semibold">
                  {item.title}
                </Heading>
                <Text className="mt-2 text-slate-600">{item.desc}</Text>
              </div>
            ))}
          </div>
        </Container>
      </Section>

      {/* Why */}
      <Section className="bg-slate-50 py-20">
        <Container>
          <Heading level={2} className="text-center text-3xl font-bold">
            Pourquoi AI Commerce OS ?
          </Heading>
          <div className="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {[
              { title: '10× plus rapide', desc: 'Générez une boutique complète en minutes, pas en semaines.' },
              { title: '20× moins cher', desc: 'Ne payez pas 5 000 € à une agence pour un premier site.' },
              { title: 'Optimisé conversion', desc: 'Moteur d&apos;optimisation, CTA et readiness score intégrés.' },
              { title: 'Export Shopify', desc: 'Passez de l&apos;idée à la mise en ligne en 1 clic.' },
              { title: 'Pas de code', desc: 'Une interface simple pour entrepreneurs et créateurs.' },
              { title: 'Scénarios par vertical', desc: 'Fitness, cuisine, tech, luxe : des modèles adaptés.' },
            ].map((item) => (
              <div key={item.title} className="rounded-xl bg-white p-6 shadow-sm">
                <Heading level={3} className="text-lg font-semibold">{item.title}</Heading>
                <Text className="mt-2 text-slate-600">{item.desc}</Text>
              </div>
            ))}
          </div>
        </Container>
      </Section>

      {/* Comparison */}
      <Section className="py-20">
        <Container>
          <Heading level={2} className="text-center text-3xl font-bold">
            Pourquoi ne pas utiliser Shopify + ChatGPT ?
          </Heading>
          <Text className="mx-auto mt-4 max-w-2xl text-center text-slate-600">
            Shopify est une caisse. ChatGPT est un correcteur. Aucun ne crée une boutique complète.
          </Text>
          <div className="mt-12 overflow-hidden rounded-2xl border border-slate-200 shadow-sm">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-100">
                <tr>
                  <th className="p-4 font-semibold">Ce que vous obtenez</th>
                  <th className="p-4 font-semibold">Shopify seul</th>
                  <th className="p-4 font-semibold">Shopify + ChatGPT</th>
                  <th className="p-4 font-semibold text-blue-700">AI Commerce OS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {(
                  [
                    ['Marque', false, false, true],
                    ['Produit + fournisseur', false, false, true],
                    ['Page d&apos;accueil', true, true, true],
                    ['Textes optimisés conversion', false, 'partiel', true],
                    ['CTA + FAQ générés', false, 'partiel', true],
                    ['Identité visuelle', false, false, true],
                    ['Export Shopify 1 clic', true, false, true],
                    ['Readiness score', false, false, true],
                  ] as Array<[string, boolean | 'partiel', boolean | 'partiel', boolean]>
                ).map(([label, shopify, chatgpt, aicos]) => (
                  <tr key={label} className="bg-white">
                    <td className="p-4 font-medium">{label}</td>
                    <td className="p-4">{shopify === 'partiel' ? 'Partiel' : shopify ? <CheckIcon /> : <XIcon />}</td>
                    <td className="p-4">{chatgpt === 'partiel' ? 'Partiel' : chatgpt ? <CheckIcon /> : <XIcon />}</td>
                    <td className="p-4">{aicos ? <CheckIcon /> : <XIcon />}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Container>
      </Section>

      {/* Pricing */}
      <Section id="pricing" className="bg-slate-50 py-20">
        <Container>
          <Heading level={2} className="text-center text-3xl font-bold">
            Tarifs
          </Heading>
          <Text className="mx-auto mt-4 max-w-2xl text-center text-slate-600">
            Commencez gratuitement. Passez à un plan payant quand vous êtes prêt à publier.
          </Text>
          <div className="mt-12 grid gap-8 md:grid-cols-3">
            {[
              {
                name: 'Free',
                price: '0 €',
                period: '/mois',
                desc: 'Pour tester et créer vos premières boutiques.',
                features: ['3 boutiques', '1 export Shopify', '5 générations', 'Support communautaire'],
                cta: 'Commencer gratuitement',
                primary: false,
              },
              {
                name: 'Pro',
                price: '49 €',
                period: '/mois',
                desc: 'Pour les créateurs et entrepreneurs sérieux.',
                features: ['25 boutiques', '25 exports Shopify', '500 crédits IA', 'Support email'],
                cta: 'Choisir Pro',
                primary: true,
              },
              {
                name: 'Agency',
                price: '149 €',
                period: '/mois',
                desc: 'Pour les agences qui génèrent des boutiques en volume.',
                features: ['100 boutiques', 'Exports illimités', '2 000 crédits IA', 'Multi-utilisateurs'],
                cta: 'Choisir Agency',
                primary: false,
              },
            ].map((plan) => (
              <div
                key={plan.name}
                className={`rounded-2xl p-8 ${plan.primary ? 'border-2 border-blue-600 bg-white shadow-lg' : 'border border-slate-200 bg-white'}`}
              >
                <Heading level={3} className="text-2xl font-bold">{plan.name}</Heading>
                <div className="mt-4 flex items-baseline">
                  <span className="text-4xl font-extrabold">{plan.price}</span>
                  <span className="ml-1 text-slate-500">{plan.period}</span>
                </div>
                <Text className="mt-2 text-slate-600">{plan.desc}</Text>
                <ul className="mt-6 space-y-3">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-center gap-3 text-slate-700">
                      <CheckIcon />
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  href="/admin"
                  className={`mt-8 block w-full rounded-lg py-3 text-center font-semibold ${
                    plan.primary
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'border border-slate-300 text-slate-800 hover:bg-slate-100'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </Container>
      </Section>

      {/* FAQ */}
      <Section className="py-20">
        <Container className="max-w-3xl">
          <Heading level={2} className="text-center text-3xl font-bold">
            Questions fréquentes
          </Heading>
          <div className="mt-12 space-y-6">
            {[
              {
                q: 'Dois-je savoir coder ?',
                a: 'Non. L&apos;interface admin est conçue pour les entrepreneurs et créateurs, pas pour les développeurs.',
              },
              {
                q: 'Puis-je exporter ma boutique vers Shopify ?',
                a: 'Oui. Nous générons un fichier JSON compatible Shopify que vous pouvez importer en quelques clics.',
              },
              {
                q: 'Combien de temps prend une génération ?',
                a: 'Entre 10 secondes (mode rule-based) et 30 secondes (avec IA), selon la complexité.',
              },
              {
                q: 'Puis-je vraiment lancer une boutique avec le plan Free ?',
                a: 'Oui. Vous pouvez créer 3 boutiques et exporter 1 boutique vers Shopify. Idéal pour valider une idée.',
              },
              {
                q: 'Qui est derrière AI Commerce OS ?',
                a: 'Une équipe de builders passionnés par l&apos;e-commerce et l&apos;IA, avec pour mission de rendre le lancement de boutiques accessible à tous.',
              },
            ].map((item) => (
              <div key={item.q} className="rounded-xl border border-slate-200 p-6">
                <Heading level={3} className="text-lg font-semibold">{item.q}</Heading>
                <Text className="mt-2 text-slate-600">{item.a}</Text>
              </div>
            ))}
          </div>
        </Container>
      </Section>

      {/* CTA */}
      <Section className="bg-slate-900 py-20 text-white">
        <Container className="text-center">
          <Heading level={2} className="text-3xl font-bold">
            Prêt à lancer votre première boutique ?
          </Heading>
          <Text className="mx-auto mt-4 max-w-2xl text-lg text-slate-300">
            Rejoignez la bêta gratuite. Créez 3 boutiques sans carte bancaire.
          </Text>
          <div className="mt-10">
            <Link
              href="/admin"
              className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-10 py-4 text-lg font-semibold text-white hover:bg-blue-700"
            >
              Créer ma boutique gratuitement
            </Link>
          </div>
          <p className="mt-4 text-sm text-slate-400">Aucune carte bancaire requise. Annulation à tout moment.</p>
        </Container>
      </Section>
    </main>
  );
}
