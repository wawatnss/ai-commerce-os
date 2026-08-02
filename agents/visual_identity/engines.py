"""Visual Identity Engine."""

import hashlib
import re
from typing import Any, Dict, List

from .schemas import (
    BrandAssetPack,
    BrandingPack,
    Color,
    IconSet,
    ImagePrompt,
    MarketingAssetPrompts,
    ProductAssetPrompts,
    StoreAssetPrompts,
    Typography,
)


CATEGORY_PALETTES: Dict[str, List[Color]] = {
    "fitness": [
        Color(name="Primary", hex="#2563EB", usage="CTA, headers, trust"),
        Color(name="Secondary", hex="#10B981", usage="Success, benefits"),
        Color(name="Accent", hex="#F59E0B", usage="Highlights, urgency"),
        Color(name="Dark", hex="#1F2937", usage="Text"),
        Color(name="Light", hex="#F3F4F6", usage="Backgrounds"),
    ],
    "cuisine": [
        Color(name="Primary", hex="#D97706", usage="Appetite, CTA"),
        Color(name="Secondary", hex="#65A30D", usage="Freshness"),
        Color(name="Accent", hex="#B91C1C", usage="Sales, urgency"),
        Color(name="Dark", hex="#451A03", usage="Text"),
        Color(name="Light", hex="#FFFBEB", usage="Backgrounds"),
    ],
    "beauty": [
        Color(name="Primary", hex="#EC4899", usage="Elegance, CTA"),
        Color(name="Secondary", hex="#8B5CF6", usage="Premium accents"),
        Color(name="Accent", hex="#FCD34D", usage="Glow, rewards"),
        Color(name="Dark", hex="#4B1D3F", usage="Text"),
        Color(name="Light", hex="#FFF1F2", usage="Backgrounds"),
    ],
    "tech": [
        Color(name="Primary", hex="#3B82F6", usage="Trust, CTA"),
        Color(name="Secondary", hex="#06B6D4", usage="Innovation"),
        Color(name="Accent", hex="#22C55E", usage="Success"),
        Color(name="Dark", hex="#0F172A", usage="Text"),
        Color(name="Light", hex="#F8FAFC", usage="Backgrounds"),
    ],
    "outdoor": [
        Color(name="Primary", hex="#059669", usage="Nature, CTA"),
        Color(name="Secondary", hex="#D97706", usage="Sun, energy"),
        Color(name="Accent", hex="#0EA5E9", usage="Sky, water"),
        Color(name="Dark", hex="#064E3B", usage="Text"),
        Color(name="Light", hex="#ECFDF5", usage="Backgrounds"),
    ],
    "home": [
        Color(name="Primary", hex="#7C3AED", usage="Comfort, CTA"),
        Color(name="Secondary", hex="#14B8A6", usage="Calm"),
        Color(name="Accent", hex="#F59E0B", usage="Warmth"),
        Color(name="Dark", hex="#1F2937", usage="Text"),
        Color(name="Light", hex="#F5F3FF", usage="Backgrounds"),
    ],
    "animals": [
        Color(name="Primary", hex="#E11D48", usage="Playful, CTA"),
        Color(name="Secondary", hex="#0EA5E9", usage="Trust"),
        Color(name="Accent", hex="#FBBF24", usage="Energy"),
        Color(name="Dark", hex="#4338CA", usage="Text"),
        Color(name="Light", hex="#FEF2F2", usage="Backgrounds"),
    ],
    "baby": [
        Color(name="Primary", hex="#0EA5E9", usage="Soft, CTA"),
        Color(name="Secondary", hex="#F472B6", usage="Care"),
        Color(name="Accent", hex="#FDE047", usage="Gentle joy"),
        Color(name="Dark", hex="#475569", usage="Text"),
        Color(name="Light", hex="#F0F9FF", usage="Backgrounds"),
    ],
    "gaming": [
        Color(name="Primary", hex="#7F1D1D", usage="Power, CTA"),
        Color(name="Secondary", hex="#A855F7", usage="Neon"),
        Color(name="Accent", hex="#22D3EE", usage="Energy"),
        Color(name="Dark", hex="#111827", usage="Text"),
        Color(name="Light", hex="#F5F3FF", usage="Backgrounds"),
    ],
    "travel": [
        Color(name="Primary", hex="#0EA5E9", usage="Sky, CTA"),
        Color(name="Secondary", hex="#F59E0B", usage="Sun, adventure"),
        Color(name="Accent", hex="#10B981", usage="Landscapes"),
        Color(name="Dark", hex="#1E3A8A", usage="Text"),
        Color(name="Light", hex="#F0F9FF", usage="Backgrounds"),
    ],
}

CATEGORY_TYPOGRAPHY: Dict[str, Typography] = {
    "fitness": Typography(heading="Oswald", body="Inter", accent="Bebas Neue", note="Bold, high energy"),
    "cuisine": Typography(heading="Playfair Display", body="Lato", accent="Pacifico", note="Appetizing and warm"),
    "beauty": Typography(heading="Bodoni Moda", body="Montserrat", accent="Great Vibes", note="Elegant and premium"),
    "tech": Typography(heading="Space Grotesk", body="Inter", accent="JetBrains Mono", note="Clean and futuristic"),
    "outdoor": Typography(heading="Rubik", body="Nunito", accent="Kalam", note="Rugged and friendly"),
    "home": Typography(heading="Canela", body="Söhne", accent="DM Sans", note="Comfortable and modern"),
    "animals": Typography(heading="Quicksand", body="Nunito", accent="Fredoka One", note="Friendly and rounded"),
    "baby": Typography(heading="Poppins", body="Nunito", accent="Quicksand", note="Soft and safe"),
    "gaming": Typography(heading="Rajdhani", body="Roboto", accent="Orbitron", note="Sharp and dynamic"),
    "travel": Typography(heading="Cormorant Garamond", body="Open Sans", accent="Satisfy", note="Dreamy and readable"),
}

STYLE_BANKS: Dict[str, List[str]] = {
    "fitness": ["dynamic", "energetic", "high contrast", "sporty", "gritty", "powerful"],
    "cuisine": ["appetizing", "warm lighting", "rustic props", "food photography", "editorial", "lifestyle"],
    "beauty": ["soft focus", "glow", "minimal", "luxury", "editorial", "pastel"],
    "tech": ["clean", "futuristic", "minimal", "isometric", "holographic", "sleek"],
    "outdoor": ["natural light", "adventure", "earthy", "wide angle", "documentary", "cinematic"],
    "home": ["cozy", "interior", "modern decor", "warm light", "scandinavian", "editorial"],
    "animals": ["playful", "cute", "warm", "lifestyle", "candid", "friendly"],
    "baby": ["soft", "gentle", "pastel", "safe", "airy", "tender"],
    "gaming": ["neon", "dark", "high energy", "competitive", "cyberpunk", "retro"],
    "travel": ["dreamy", "wanderlust", "golden hour", "panoramic", "documentary", "ethereal"],
}

LIGHTING_BANKS: Dict[str, List[str]] = {
    "fitness": ["dramatic side light", "gym fluorescent", "backlit silhouette", "high-key"],
    "cuisine": ["soft window light", "warm tungsten", "natural daylight", "moody chiaroscuro"],
    "beauty": ["ring light", "soft diffused", "backlit glow", "studio softbox"],
    "tech": ["cool blue rim light", "clean white studio", "neon accent", "gradient glow"],
    "outdoor": ["golden hour sun", "overcast even", "dawn mist", "midday clarity"],
    "home": ["warm lamplight", "morning window", "cozy ambient", "sunset glow"],
    "animals": ["natural daylight", "soft indoor", "golden hour", "flash-free"],
    "baby": ["soft diffused", "window light", "warm ambient", "pastel glow"],
    "gaming": ["neon RGB", "dark with accent", "screen glow", "high contrast"],
    "travel": ["golden hour", "blue hour", "harsh sun", "misty morning"],
}

COMPOSITION_BANKS: Dict[str, List[str]] = {
    "fitness": ["centered subject", "diagonal energy", "rule of thirds", "low angle"],
    "cuisine": ["overhead flat lay", "45-degree angle", "macro detail", "table setting"],
    "beauty": ["tight crop", "off-center subject", "mirror reflection", "layered props"],
    "tech": ["floating product", "hero shot", "angled detail", "grid layout"],
    "outdoor": ["wide landscape", "subject in environment", "leading lines", "foreground interest"],
    "home": ["room vignette", "detail with context", "styled shelf", "wide interior"],
    "animals": ["subject at eye level", "action moment", "cozy close-up", "environmental"],
    "baby": ["soft close-up", "parent hands", "nursery context", "gentle portrait"],
    "gaming": ["controller in hand", "screen reflection", "dynamic pose", "product hero"],
    "travel": ["wide scenic", "person in frame", "detail with backdrop", "overhead map"],
}

BACKGROUND_BANKS: Dict[str, List[str]] = {
    "fitness": ["gym floor", "outdoor track", "gradient smoke", "solid color"],
    "cuisine": ["marble counter", "wooden table", "rustic kitchen", "solid color"],
    "beauty": ["soft gradient", "marble surface", "bathroom shelf", "solid color"],
    "tech": ["dark gradient", "glass surface", "abstract circuit", "solid color"],
    "outdoor": ["mountain vista", "forest trail", "campsite", "solid color"],
    "home": ["living room corner", "bedroom nightstand", "cozy shelf", "solid color"],
    "animals": ["cozy blanket", "outdoor grass", "home floor", "solid color"],
    "baby": ["nursery crib", "soft blanket", "pastel wall", "solid color"],
    "gaming": ["dark room", "neon city", "abstract grid", "solid color"],
    "travel": ["airport gate", "beach horizon", "mountain ridge", "solid color"],
}

ANGLE_BANKS: Dict[str, List[str]] = {
    "fitness": ["eye level", "low angle", "overhead"],
    "cuisine": ["overhead", "45 degrees", "eye level"],
    "beauty": ["eye level", "close-up", "slightly above"],
    "tech": ["slightly above", "eye level", "angled"],
    "outdoor": ["wide", "eye level", "low angle"],
    "home": ["eye level", "wide", "detail"],
    "animals": ["eye level", "low angle", "candid"],
    "baby": ["soft above", "eye level", "close-up"],
    "gaming": ["dynamic angle", "eye level", "overhead"],
    "travel": ["wide", "eye level", "overhead"],
}

# Subject line per image kind; each prompt family will wrap it differently.
SUBJECT_BANKS: Dict[str, str] = {
    "hero_banner": "{aspect} {category} hero banner for {brand} featuring {product}",
    "category_banner": "{aspect} {category} collection banner for {brand} with {product}",
    "newsletter_banner": "{aspect} newsletter header for {brand} announcing {product}",
    "product_hero": "{aspect} product hero of {product} by {brand}",
    "lifestyle": "{category} lifestyle scene with {product} from {brand}",
    "packshot": "{aspect} packshot of {product} by {brand} on white",
    "mockup": "{aspect} mockup of {product} by {brand} in context",
    "instagram_post": "{aspect} Instagram post for {brand} with {product}",
    "tiktok_cover": "{aspect} TikTok cover for {brand} with {product}",
    "pinterest": "{aspect} Pinterest pin for {brand} showing {product}",
    "facebook_cover": "{aspect} Facebook cover for {brand} with {product}",
    "email_header": "{aspect} email header for {brand} with {product}",
}

# 8 prompt families. Each template orders details differently to avoid shared starts.
FAMILY_TEMPLATES: Dict[str, str] = {
    "storytelling": "Imagine a small story around {subject}. The light is {lighting}, the mood is {tone}, the setting is {background}. Styled {style}, composed as {composition}, seen from a {angle} angle. {extra}",
    "studio": "Clean studio frame of {subject}. {lighting} on a {background}, {style} treatment, {composition} from a {angle} angle. {extra}",
    "lifestyle": "Candid lifestyle moment of {subject}. Natural {lighting}, {style} vibe, {background}, composed as {composition}, shot {angle}. {extra}",
    "editorial": "Editorial {subject}. {style} aesthetic, {lighting} on {background}, arranged in {composition}, {angle} perspective. {extra}",
    "minimal": "Ultra-minimal {subject}. Only essential shapes, {lighting}, {background}, {style} restraint, {composition}, {angle}. {extra}",
    "luxury": "Luxury campaign still of {subject}. {style} opulence, {lighting}, {background}, composed as {composition}, {angle}. {extra}",
    "premium": "Premium product showcase of {subject}. {style} finish, {lighting}, {background}, {composition}, {angle} view. {extra}",
    "cinematic": "Cinematic wide frame of {subject}. {style} drama, {lighting}, {background}, {composition}, {angle} angle. {extra}",
}

FAMILY_ORDER: List[str] = ["storytelling", "studio", "lifestyle", "editorial", "minimal", "luxury", "premium", "cinematic"]


def _normalize_category(category: str) -> str:
    category = category.lower().strip() if category else "tech"
    mapping = {
        "home-goods": "home",
        "maison": "home",
        "cuisine": "cuisine",
        "nourriture": "cuisine",
        "food": "cuisine",
        "animaux": "animals",
        "pets": "animals",
        "bebe": "baby",
        "voyage": "travel",
        "gaming": "gaming",
    }
    return mapping.get(category, category)


def _pick_index(key: str, options: List[str]) -> int:
    h = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)
    return h % len(options)


class VisualIdentityEngine:
    """Generate a complete Brand Asset Pack from a blueprint."""

    def run(self, blueprint: Dict[str, Any]) -> BrandAssetPack:
        category = _normalize_category(blueprint.get("product_page", {}).get("category"))
        brand = blueprint.get("store_name", "Brand")
        product = blueprint.get("product_page", {}).get("product_name") or brand
        tone = self._detect_tone(blueprint)
        palette = self._build_palette(blueprint, category)
        primary = palette[0].hex
        secondary = palette[1].hex
        typography = CATEGORY_TYPOGRAPHY.get(category, CATEGORY_TYPOGRAPHY["tech"])

        return BrandAssetPack(
            branding=BrandingPack(
                logo_svg=self._logo_svg(brand, primary, secondary),
                favicon_svg=self._favicon_svg(brand, primary),
                palette=palette,
                icons=IconSet(
                    style="outline" if category in ("tech", "home") else "filled",
                    recommended=self._icons(category),
                ),
                typography=typography,
            ),
            store=StoreAssetPrompts(
                hero_banner=self._prompt("hero_banner", brand, product, category, tone, palette),
                category_banner=self._prompt("category_banner", brand, product, category, tone, palette),
                newsletter_banner=self._prompt("newsletter_banner", brand, product, category, tone, palette),
            ),
            product=ProductAssetPrompts(
                product_hero=self._prompt("product_hero", brand, product, category, tone, palette),
                lifestyle=self._prompt("lifestyle", brand, product, category, tone, palette),
                packshot=self._prompt("packshot", brand, product, category, tone, palette),
                mockup=self._prompt("mockup", brand, product, category, tone, palette),
            ),
            marketing=MarketingAssetPrompts(
                instagram_post=self._prompt("instagram_post", brand, product, category, tone, palette),
                tiktok_cover=self._prompt("tiktok_cover", brand, product, category, tone, palette),
                pinterest=self._prompt("pinterest", brand, product, category, tone, palette),
                facebook_cover=self._prompt("facebook_cover", brand, product, category, tone, palette),
                email_header=self._prompt("email_header", brand, product, category, tone, palette),
            ),
            source_palette=f"theme+{category}" if blueprint.get("theme") else f"category:{category}",
        )

    def _build_palette(self, blueprint: Dict[str, Any], category: str) -> List[Color]:
        theme = blueprint.get("theme", {})
        if theme.get("primary_color") and theme.get("secondary_color"):
            return [
                Color(name="Primary", hex=theme["primary_color"], usage="CTA, headers, trust"),
                Color(name="Secondary", hex=theme["secondary_color"], usage="Benefits, accents"),
                Color(name="Accent", hex=theme.get("accent_color", "#F59E0B"), usage="Highlights, urgency"),
                Color(name="Dark", hex=theme.get("text_color", "#1F2937"), usage="Text"),
                Color(name="Light", hex=theme.get("background_color", "#FFFFFF"), usage="Backgrounds"),
            ]
        return CATEGORY_PALETTES.get(category, CATEGORY_PALETTES["tech"])

    def _detect_tone(self, blueprint: Dict[str, Any]) -> str:
        desc = blueprint.get("store_description", "")
        if any(w in desc.lower() for w in ["premium", "elegant", "luxury"]):
            return "premium"
        if any(w in desc.lower() for w in ["fun", "playful", "joy"]):
            return "playful"
        if any(w in desc.lower() for w in ["adventure", "outdoor", "explore"]):
            return "adventurous"
        if any(w in desc.lower() for w in ["safe", "gentle", "care"]):
            return "caring"
        return "confident"

    def _icons(self, category: str) -> List[str]:
        icon_map = {
            "fitness": ["dumbbell", "heart-pulse", "trophy", "flame"],
            "cuisine": ["chef-hat", "utensils", "leaf", "coffee"],
            "beauty": ["sparkles", "flower", "droplet", "heart"],
            "tech": ["cpu", "wifi", "shield", "zap"],
            "outdoor": ["mountain", "tree", "tent", "sun"],
            "home": ["lamp", "sofa", "home", "star"],
            "animals": ["paw", "bone", "heart", "fish"],
            "baby": ["baby", "moon", "heart", "star"],
            "gaming": ["gamepad", "zap", "trophy", "target"],
            "travel": ["plane", "map", "sun", "compass"],
        }
        return icon_map.get(category, ["star", "heart", "zap"])

    def _slug(self, text: str) -> str:
        return re.sub(r"[^a-z0-9]", "-", text.lower())[:20].strip("-")

    def _initials(self, text: str) -> str:
        words = re.findall(r"[A-Z]", text.title())
        return "".join(words[:2]) if words else text[:2].upper()

    def _logo_svg(self, brand: str, primary: str, secondary: str) -> str:
        initials = self._initials(brand)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120" role="img" aria-label="{brand} logo">'
            f'<rect x="10" y="10" width="100" height="100" rx="24" fill="{primary}"/>'
            f'<text x="60" y="74" font-family="Inter, sans-serif" font-size="40" font-weight="700" fill="{secondary}" text-anchor="middle">{initials}</text>'
            f'</svg>'
        )

    def _favicon_svg(self, brand: str, primary: str) -> str:
        initials = self._initials(brand)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">'
            f'<rect width="64" height="64" rx="14" fill="{primary}"/>'
            f'<text x="32" y="42" font-family="Inter, sans-serif" font-size="26" font-weight="700" fill="#FFFFFF" text-anchor="middle">{initials[:1]}</text>'
            f'</svg>'
        )

    def _select_family(self, category: str, tone: str, brand: str, product: str) -> str:
        """Pick a prompt family based on tone and category."""
        tone_map = {
            "premium": "luxury",
            "playful": "lifestyle",
            "adventurous": "cinematic",
            "caring": "storytelling",
            "confident": "premium",
        }
        base = tone_map.get(tone, "premium")
        # Add a stable but varied per-brand/product offset
        key = f"{brand}:{product}:{category}"
        offset = _pick_index(key, FAMILY_ORDER)
        family_index = (FAMILY_ORDER.index(base) + offset) % len(FAMILY_ORDER)
        return FAMILY_ORDER[family_index]

    def _prompt(self, kind: str, brand: str, product: str, category: str, tone: str, palette: List[Color]) -> ImagePrompt:
        colors = ", ".join([c.hex for c in palette[:3]])
        aspect = {
            "hero_banner": "16:9",
            "category_banner": "16:9",
            "newsletter_banner": "3:1",
            "product_hero": "1:1",
            "lifestyle": "4:3",
            "packshot": "1:1",
            "mockup": "4:3",
            "instagram_post": "1:1",
            "tiktok_cover": "9:16",
            "pinterest": "2:3",
            "facebook_cover": "16:9",
            "email_header": "3:1",
        }[kind]

        style = self._pick(category, "style", STYLE_BANKS[category])
        lighting = self._pick(category, "lighting", LIGHTING_BANKS[category])
        composition = self._pick(category, "composition", COMPOSITION_BANKS[category])
        background = self._pick(category, "background", BACKGROUND_BANKS[category])
        angle = self._pick(category, "angle", ANGLE_BANKS[category])

        family = self._select_family(category, tone, brand, product)
        subject = SUBJECT_BANKS[kind].format(
            brand=brand,
            product=product,
            category=category,
            tone=tone,
            aspect=aspect,
        )

        extra_map = {
            "hero_banner": f"Color palette: {colors}. High-end brand imagery.",
            "product_hero": f"Color palette: {colors}. Sharp, commercial quality.",
            "instagram_post": f"Color palette: {colors}. Social-first, thumb-stopping.",
            "tiktok_cover": f"Color palette: {colors}. Bold typography-safe space.",
            "facebook_cover": f"Color palette: {colors}. Wide, cinematic brand feel.",
        }
        extra = extra_map.get(kind, f"Color palette: {colors}.")

        template = FAMILY_TEMPLATES[family]
        prompt_text = template.format(
            subject=subject,
            tone=tone,
            style=style,
            lighting=lighting,
            composition=composition,
            background=background,
            angle=angle,
            extra=extra,
        )

        style_tags = [family, style, lighting, composition, background, angle]
        return ImagePrompt(
            name=kind,
            prompt=prompt_text,
            negative_prompt="blurry, distorted text, watermark, low quality, inconsistent style, off-brand colors, noisy background, bad anatomy, duplicate elements",
            aspect_ratio=aspect,
            style_tags=style_tags,
        )

    def _pick(self, category: str, label: str, bank: List[str]) -> str:
        key = f"{category}:{label}"
        return bank[_pick_index(key, bank)]
