"""FAQ Engine."""

from typing import Any, Dict, List

from .schemas import FAQItem, FAQSet


QUESTION_BANKS: Dict[str, List[Dict[str, str]]] = {
    "fitness": [
        {"q": "Are the resistance bands suitable for beginners?", "a": "Yes, the set includes light, medium and heavy bands for every level.", "c": "product"},
        {"q": "Can I wash the bands?", "a": "Wipe them with a damp cloth; do not machine wash.", "c": "care"},
        {"q": "How long does delivery take?", "a": "Standard delivery is 5-7 business days; express is 2-3.", "c": "shipping"},
        {"q": "What if the band snaps?", "a": "Contact us within 30 days for a free replacement.", "c": "returns"},
        {"q": "Do you offer workout guides?", "a": "Yes, a digital guide is included with every order.", "c": "product"},
    ],
    "cuisine": [
        {"q": "Are the knives dishwasher safe?", "a": "Hand washing is recommended to keep the edge sharp.", "c": "care"},
        {"q": "What material is the blade?", "a": "High-carbon stainless steel for long-lasting sharpness.", "c": "product"},
        {"q": "How long is the warranty?", "a": "We offer a 2-year warranty against manufacturing defects.", "c": "warranty"},
        {"q": "Can I return the set if unused?", "a": "Yes, unused sets in original packaging can be returned within 30 days.", "c": "returns"},
        {"q": "Do you ship internationally?", "a": "Yes, we ship to most countries; customs fees may apply.", "c": "shipping"},
    ],
    "beauty": [
        {"q": "Is the serum cruelty-free?", "a": "Yes, our products are certified cruelty-free and vegan.", "c": "product"},
        {"q": "How should I store the serum?", "a": "Keep it in a cool, dry place away from direct sunlight.", "c": "care"},
        {"q": "When will I see results?", "a": "Most users notice improvements after 2-3 weeks of daily use.", "c": "product"},
        {"q": "Can I use it with other products?", "a": "Yes, but patch test first when mixing active ingredients.", "c": "care"},
        {"q": "What is your return policy?", "a": "You can return unopened products within 30 days.", "c": "returns"},
    ],
    "tech": [
        {"q": "Is the hub compatible with iOS and Android?", "a": "Yes, it works with both via Bluetooth and Wi-Fi.", "c": "product"},
        {"q": "What is the range?", "a": "The hub has a 30-meter open-space range.", "c": "product"},
        {"q": "How often are software updates released?", "a": "Updates are released quarterly and installed automatically.", "c": "warranty"},
        {"q": "Can I return it if it doesn't fit my setup?", "a": "Yes, returns are accepted within 30 days.", "c": "returns"},
        {"q": "Does it come with a warranty?", "a": "Yes, a 1-year limited warranty is included.", "c": "warranty"},
    ],
    "outdoor": [
        {"q": "Is the tent waterproof?", "a": "Yes, it has a 3000mm hydrostatic head rating.", "c": "product"},
        {"q": "How many people can it fit?", "a": "The tent comfortably fits 2 adults and their gear.", "c": "product"},
        {"q": "What is the packed weight?", "a": "It weighs 2.1 kg including poles and pegs.", "c": "shipping"},
        {"q": "Can I return it after one trip?", "a": "Yes, if it is clean and in original condition within 30 days.", "c": "returns"},
        {"q": "Does it include a repair kit?", "a": "A small repair patch kit is included.", "c": "warranty"},
    ],
    "home": [
        {"q": "Is the lamp dimmable?", "a": "Yes, it has 3 brightness levels and a warm-to-cool slider.", "c": "product"},
        {"q": "What bulb type does it use?", "a": "It uses an integrated LED with a 25,000-hour lifespan.", "c": "product"},
        {"q": "How do I clean the shade?", "a": "Use a soft dry cloth; do not use water on the fabric shade.", "c": "care"},
        {"q": "Can I return it if the color doesn't match?", "a": "Yes, returns are accepted within 30 days.", "c": "returns"},
        {"q": "Does it work with smart assistants?", "a": "Yes, it is compatible with Alexa and Google Home.", "c": "product"},
    ],
    "animals": [
        {"q": "What size pet is the bed for?", "a": "It fits dogs and cats up to 15 kg.", "c": "product"},
        {"q": "Is the cover machine washable?", "a": "Yes, the cover is removable and washable at 30°C.", "c": "care"},
        {"q": "What filling is used?", "a": "It uses recycled polyester filling.", "c": "product"},
        {"q": "How long does delivery take?", "a": "Standard delivery is 5-7 business days.", "c": "shipping"},
        {"q": "Can I return it if my pet doesn't use it?", "a": "Yes, returns are accepted within 30 days in original condition.", "c": "returns"},
    ],
    "baby": [
        {"q": "Is the monitor Wi-Fi or radio?", "a": "It uses an encrypted 2.4 GHz radio connection.", "c": "product"},
        {"q": "What is the battery life?", "a": "The parent unit lasts up to 12 hours on a full charge.", "c": "product"},
        {"q": "Is it safe near the crib?", "a": "Yes, it meets all baby-safe distance and emission standards.", "c": "safety"},
        {"q": "Can I return it unopened?", "a": "Yes, unopened products can be returned within 30 days.", "c": "returns"},
        {"q": "Does it have a warranty?", "a": "Yes, a 1-year warranty is included.", "c": "warranty"},
    ],
    "gaming": [
        {"q": "Is the controller compatible with PC?", "a": "Yes, it works with PC, PlayStation and Switch.", "c": "product"},
        {"q": "Does it have programmable buttons?", "a": "Yes, 4 back buttons can be remapped.", "c": "product"},
        {"q": "What is the latency?", "a": "Wired latency is under 1 ms; wireless is under 4 ms.", "c": "product"},
        {"q": "Can I return it if it doesn't fit my hands?", "a": "Yes, returns are accepted within 30 days.", "c": "returns"},
        {"q": "Does it come with a carrying case?", "a": "A basic travel case is included.", "c": "shipping"},
    ],
    "travel": [
        {"q": "Is the backpack carry-on size?", "a": "Yes, it fits most airline carry-on dimensions.", "c": "product"},
        {"q": "How many liters is it?", "a": "It has a 40-liter capacity.", "c": "product"},
        {"q": "Is it water-resistant?", "a": "Yes, the outer shell is water-resistant.", "c": "product"},
        {"q": "What if the strap breaks?", "a": "Contact us for a free repair or replacement within the warranty period.", "c": "warranty"},
        {"q": "Can I return it after a trip?", "a": "Yes, if it is clean and in original condition within 30 days.", "c": "returns"},
    ],
}


def _normalize_category(category: str) -> str:
    category = category.lower().strip()
    mapping = {
        "home-goods": "home",
        "maison": "home",
        "cuisine": "cuisine",
        "food": "cuisine",
        "nourriture": "cuisine",
        "animals": "animals",
        "animaux": "animals",
        "pets": "animals",
        "bebe": "baby",
        "baby": "baby",
        "voyage": "travel",
        "travel": "travel",
        "gaming": "gaming",
        "games": "gaming",
        "tech": "tech",
        "electronics": "tech",
    }
    return mapping.get(category, category)


class FAQEngine:
    """Generate a diverse, category-aware FAQ."""

    def run(self, blueprint: Dict[str, Any], policies: Dict[str, Any] | None = None) -> FAQSet:
        category = _normalize_category(blueprint.get("product_page", {}).get("category", "tech"))
        brand = blueprint.get("store_name", "Brand")
        bank = QUESTION_BANKS.get(category, QUESTION_BANKS["tech"])

        # Add policy-specific answers if available
        policies = policies or blueprint.get("policies", {})
        shipping = policies.get("shipping_policy", {})
        refund = policies.get("refund_policy", {})

        items: List[FAQItem] = []
        for entry in bank:
            answer = entry["a"]
            if entry["c"] == "shipping" and shipping.get("shipping_times", {}).get("standard"):
                answer = f"{answer} ({shipping['shipping_times']['standard']})."
            if entry["c"] == "returns" and refund.get("days"):
                answer = answer.replace("within 30 days", f"within {refund['days']} days")
            items.append(FAQItem(
                question=entry["q"].replace("our products", f"{brand} products"),
                answer=answer,
                category=entry["c"],
            ))

        # Compute a simple diversity score: unique unigrams in questions vs total
        words = [w for it in items for w in it.question.lower().split()]
        diversity = round((len(set(words)) / len(words) * 100) if words else 0.0, 1)
        return FAQSet(items=items, diversity_score=diversity)
