# FAQ Utilisateur — AI Commerce OS v1.0.0-beta

## Général

### Qu'est-ce qu'AI Commerce OS ?

Une plateforme qui génère automatiquement des boutiques e-commerce prêtes à publier : marque, produit, contenu, CTA, FAQ, identité visuelle et export Shopify.

### Dois-je savoir coder ?

Non. Tout se passe via l'interface admin. Seuls l'installation et le déploiement techniques nécessitent un administrateur.

### Quels sont les coûts ?

- **Free** : 3 boutiques, 1 export, 5 générations
- **Pro** : 25 boutiques, 10 exports, 50 générations, 500 crédits IA
- **Business** : illimité, 5000 crédits IA

## Compte

### Je n'ai pas reçu l'email de vérification

Vérifiez vos spams. Si SMTP n'est pas encore configuré par l'administrateur, l'email ne sera pas envoyé.

### J'ai oublié mon mot de passe

Cliquez sur "Mot de passe oublié" sur la page de connexion. Un lien de réinitialisation vous sera envoyé par email.

### Puis-je supprimer mon compte ?

Oui, dans Profil > Danger zone. Cela supprime définitivement votre compte et toutes les boutiques associées.

## Génération

### Combien de temps dure une génération ?

- Sans IA : environ 10 secondes
- Avec OpenAI : 15 à 40 secondes selon la charge

### Pourquoi ma boutique a-t-elle un score faible ?

Le score dépend de :
- la cohérence du contenu
- du SEO
- de l'accessibilité
- des CTA
- de la qualité des images

Utilisez le bouton **Optimiser** et **Auto-fix Shopify** pour améliorer.

### Puis-je modifier manuellement une boutique générée ?

Oui en téléchargeant le blueprint JSON, en l'éditant, et en le réimportant. Une interface d'édition en ligne n'est pas encore disponible en bêta.

## Export

### Puis-je exporter vers Shopify ?

Oui. Ouvrez la boutique, cliquez sur **Exporter > Shopify** et téléchargez le fichier JSON.

### Puis-je exporter vers d'autres plateformes ?

Le blueprint JSON est agnostique. Vous pouvez l'adapter à WooCommerce, PrestaShop, Magento, etc.

## Limites

- Pas d'éditeur WYSIWYG en bêta.
- Les images ne sont pas générées automatiquement (seuls les prompts le sont).
- Le support de chat est limité aux plans payants.
