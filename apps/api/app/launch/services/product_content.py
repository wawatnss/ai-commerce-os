"""Category-aware product content banks for Sprint 4.6."""

import hashlib
from typing import Dict, List


BENEFIT_BANKS: Dict[str, List[str]] = {
    "fitness": [
        "{product} adapts to every strength level",
        "Train anywhere with {product}",
        "{brand} {product} is built for daily sweat",
        "Recover faster with {product}",
        "Lightweight {product} that travels with you",
        "{product} holds up to heavy use",
        "Feel the difference in your first workout",
        "{brand} {product} fits in any gym bag",
    ],
    "cuisine": [
        "{product} makes prep feel effortless",
        "Cook like a chef with {product}",
        "{product} keeps its edge meal after meal",
        "Balanced weight for all-day comfort",
        "{brand} {product} is a joy to hold",
        "Cleanup is quick with {product}",
        "{product} turns simple ingredients into masterpieces",
        "Built for the way real kitchens work",
    ],
    "beauty": [
        "{product} reveals your natural glow",
        "Gentle enough for morning and night",
        "{product} absorbs in seconds",
        "Visible results in two weeks",
        "{brand} {product} feels like a ritual",
        "Hydration that lasts all day",
        "{product} works with every skin type",
        "A little {product} goes a long way",
    ],
    "tech": [
        "{product} connects in seconds",
        "Control everything from one app",
        "{product} runs whisper quiet",
        "Designed for the way you live today",
        "{brand} {product} keeps getting smarter",
        "Setup is effortless with {product}",
        "One {product}, endless possibilities",
        "Privacy-first, always",
    ],
    "outdoor": [
        "{product} shrugs off rain and wind",
        "Pack it fast, trust it for years",
        "{product} is ready at dawn",
        "Light on your back, tough on the trail",
        "{brand} {product} breathes with you",
        "Built for unexpected weather",
        "{product} makes every summit sweeter",
        "Adventure-tested by real explorers",
    ],
    "home": [
        "{product} makes every evening softer",
        "Designed for small spaces and big moments",
        "{product} warms the whole room",
        "A quiet statement in any corner",
        "{brand} {product} lasts for years",
        "Soft light that follows your mood",
        "{product} feels as good as it looks",
        "Thoughtful details in every inch",
    ],
    "animals": [
        "{product} keeps your pet cozy for hours",
        "Tough enough for playful paws",
        "{product} is gentle on joints",
        "Easy to clean after messy days",
        "{brand} {product} becomes their favorite spot",
        "Safe materials you can trust",
        "{product} holds its shape wash after wash",
        "Made for naps, zoomies and everything between",
    ],
    "baby": [
        "{product} gives parents peace of mind",
        "Soft enough for the most sensitive skin",
        "{product} is easy to use one-handed",
        "Sleep-ready in seconds",
        "{brand} {product} is pediatrician trusted",
        "Quiet alerts that do not wake the baby",
        "{product} grows with your little one",
        "Simple setup at 2 a.m.",
    ],
    "gaming": [
        "{product} responds before you blink",
        "Comfort that lasts through long sessions",
        "{product} gives you the edge",
        "Programmable for your playstyle",
        "{brand} {product} is tournament tested",
        "Zero-lag when it matters",
        "{product} feels like an extension of your hands",
        "Built for wins, designed for comfort",
    ],
    "travel": [
        "{product} fits more than you think",
        "Light enough to forget it is there",
        "{product} glides through airports",
        "Pockets for everything you need",
        "{brand} {product} survives baggage handlers",
        "Weather-ready for any destination",
        "{product} makes packing feel simple",
        "Carry-on approved on most airlines",
    ],
}

FEATURE_BANKS: Dict[str, List[str]] = {
    "fitness": [
        "Adjustable resistance levels",
        "Sweat-resistant grip",
        "Portable carrying case",
        "Anti-snap construction",
        "Non-slip textured surface",
        "Full-body exercise guide included",
        "Stackable for progression",
        "Eco-friendly natural latex",
    ],
    "cuisine": [
        "High-carbon steel blade",
        "Ergonomic walnut handle",
        "Full tang construction",
        "Edge guard included",
        "Dishwasher-safe bolster",
        "Precision-forged balance",
        "Rust-resistant finish",
        "Professional-grade sharpness",
    ],
    "beauty": [
        "Hyaluronic acid complex",
        "Cruelty-free and vegan",
        "Airless pump bottle",
        "Dermatologist tested",
        "No synthetic fragrances",
        "pH-balanced formula",
        "Recyclable glass packaging",
        "Slow-release actives",
    ],
    "tech": [
        "Wi-Fi and Bluetooth 5.0",
        "Voice assistant compatible",
        "Encrypted local processing",
        "Energy-efficient standby",
        "Over-the-air updates",
        "Dual-band connectivity",
        "Compact minimal design",
        "One-tap automation",
    ],
    "outdoor": [
        "Waterproof 3000mm coating",
        "Ultralight aluminum poles",
        "Reflective guy lines",
        "Mesh ventilation panels",
        "Color-coded assembly",
        "Packable to shoebox size",
        "Reinforced stress points",
        "UV-resistant fabric",
    ],
    "home": [
        "Dimmable touch control",
        "Warm-to-cool spectrum",
        "Smart home compatible",
        "Energy-saving LED",
        "Cordless rechargeable base",
        "Memory preset scene",
        "Minimalist fabric shade",
        "Whisper-quiet motor",
    ],
    "animals": [
        "Removable machine-washable cover",
        "Memory foam core",
        "Non-toxic pet-safe fabric",
        "Raised sides for nesting",
        "Water-resistant base",
        "Anti-slip bottom",
        "Odor-resistant treatment",
        "Reversible two-tone design",
    ],
    "baby": [
        "Encrypted 2.4 GHz wireless",
        "Two-way audio talkback",
        "Room temperature sensor",
        "Night vision without glow",
        "Up to 12-hour battery",
        "Secure wall-mount base",
        "Feeding timer reminder",
        "Soft lullaby player",
    ],
    "gaming": [
        "Remappable back buttons",
        "Hair-trigger mode",
        "Adjustable thumbstick tension",
        "Low-latency wireless dongle",
        "Textured anti-slip grips",
        "RGB accent lighting",
        "40-hour rechargeable battery",
        "Cross-platform compatibility",
    ],
    "travel": [
        "40-liter clamshell opening",
        "360-degree spinner wheels",
        "TSA-approved combination lock",
        "Expandable zip section",
        "Padded laptop compartment",
        "Water-resistant shell",
        "Compression straps inside",
        "RFID-blocking pocket",
    ],
}


def _pick_index(key: str, options: List[str]) -> int:
    h = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)
    return h % len(options)


def get_product_content(category: str, brand: str, product: str) -> dict:
    """Return category-specific benefits and features for a product page."""
    category = category.lower().strip()
    if category not in BENEFIT_BANKS:
        category = "tech"

    benefits = []
    for i in range(4):
        key = f"{brand}:{product}:benefit:{i}"
        template = BENEFIT_BANKS[category][_pick_index(key, BENEFIT_BANKS[category])]
        benefits.append(template.format(brand=brand, product=product))

    features = []
    for i in range(4):
        key = f"{brand}:{product}:feature:{i}"
        template = FEATURE_BANKS[category][_pick_index(key, FEATURE_BANKS[category])]
        features.append(template.format(brand=brand, product=product))

    return {
        "benefits": benefits,
        "features": features,
    }
