"""Email templates."""
from dataclasses import dataclass


@dataclass
class Template:
    subject: str
    text: str
    html: str


def welcome_email(email: str) -> Template:
    return Template(
        subject="Bienvenue sur AI Commerce OS",
        text=f"""Bonjour,

Bienvenue sur AI Commerce OS. Votre compte {email} est maintenant actif.

Commencez par créer votre première boutique : https://admin.ai-commerce.com/onboarding

L'équipe AI Commerce OS""",
        html=f"""<p>Bonjour,</p>
<p>Bienvenue sur <strong>AI Commerce OS</strong>. Votre compte {email} est maintenant actif.</p>
<p><a href="https://admin.ai-commerce.com/onboarding">Créer votre première boutique</a></p>
<p>L'équipe AI Commerce OS</p>""",
    )


def verification_email(email: str, token: str, base_url: str = "https://admin.ai-commerce.com") -> Template:
    link = f"{base_url}/verify-email?token={token}"
    return Template(
        subject="Vérifiez votre adresse email",
        text=f"""Bonjour,

Veuillez vérifier votre adresse email en cliquant sur le lien suivant :
{link}

Si vous n'avez pas demandé cette vérification, ignorez cet email.

L'équipe AI Commerce OS""",
        html=f"""<p>Bonjour,</p>
<p>Veuillez vérifier votre adresse email en cliquant sur le lien suivant :</p>
<p><a href="{link}">{link}</a></p>
<p>Si vous n'avez pas demandé cette vérification, ignorez cet email.</p>
<p>L'équipe AI Commerce OS</p>""",
    )


def password_reset_email(email: str, token: str, base_url: str = "https://admin.ai-commerce.com") -> Template:
    link = f"{base_url}/reset-password?token={token}"
    return Template(
        subject="Réinitialisation de votre mot de passe",
        text=f"""Bonjour,

Vous avez demandé une réinitialisation de mot de passe. Cliquez sur le lien suivant :
{link}

Ce lien est valable 15 minutes.

L'équipe AI Commerce OS""",
        html=f"""<p>Bonjour,</p>
<p>Vous avez demandé une réinitialisation de mot de passe.</p>
<p><a href="{link}">Réinitialiser mon mot de passe</a></p>
<p>Ce lien est valable 15 minutes.</p>
<p>L'équipe AI Commerce OS</p>""",
    )
