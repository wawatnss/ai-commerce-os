"""
Identity Engine

Generates mission, vision, and brand identity elements.
"""

import hashlib
import random
from typing import Dict, Any, List, Optional
from .base import BaseBrandEngine, EngineResult
from ..prompts.templates import prompt_library


MISSION_TEMPLATES: Dict[str, List[str]] = {
    "fitness": [
        "{brand_name} exists to fuel every athlete's ambition with {product_name} engineered for strength, endurance and unwavering confidence.",
        "We believe movement is power. {brand_name} designs {product_name} that push limits and celebrate progress, one rep at a time.",
        "For the ones who rise before dawn and train after dark, {brand_name} builds {product_name} that never quit.",
        "Our mission is simple: give every body the {product_name} it deserves to perform, recover and conquer new goals.",
        "At {brand_name}, sweat is sacred. We craft {product_name} that honor the effort behind every personal best.",
    ],
    "cuisine": [
        "{brand_name} brings people together around {product_name} that turn everyday cooking into a delicious ritual.",
        "We exist to sharpen the joy of cooking. {brand_name} offers {product_name} made for curious hands and hungry hearts.",
        "Flavor starts with the right tools. {brand_name} creates {product_name} that help home cooks make meals worth sharing.",
        "Our kitchen is your kitchen. {brand_name} designs {product_name} for people who believe that good food is good living.",
        "Cooking is an act of love. {brand_name} provides {product_name} that let that love shine in every dish.",
    ],
    "beauty": [
        "{brand_name} believes radiant skin should feel effortless. Our {product_name} are made for the rituals that make you glow.",
        "We create {product_name} that treat your skin with the same care you treat the people you love.",
        "Beauty is personal. {brand_name} formulates {product_name} that adapt to your skin, your mood, your moment.",
        "At {brand_name}, every drop of {product_name} is a promise to protect, nourish and illuminate your natural radiance.",
        "Our mission is to make self-care feel like a gift. {brand_name} offers {product_name} that turn routine into renewal.",
    ],
    "tech": [
        "{brand_name} exists to make the future feel simple. We design {product_name} that remove friction from everyday life.",
        "Technology should serve people, not the other way around. {brand_name} builds {product_name} that quietly make your day better.",
        "We are the tinkerers, the builders and the optimists. {brand_name} creates {product_name} that connect what matters.",
        "Our mission is to put powerful tools in calm hands. {brand_name} makes {product_name} that feel inevitable once you use them.",
        "At {brand_name}, innovation is only useful if it feels effortless. That is the standard behind every {product_name} we build.",
    ],
    "outdoor": [
        "{brand_name} exists to get more people outside. Our {product_name} are built for dirt, wind, rain and the stories that follow.",
        "The best memories happen far from Wi-Fi. {brand_name} creates {product_name} for explorers who pack light and dream big.",
        "We believe nature is the ultimate playground. {brand_name} makes {product_name} that help you stay longer and go further.",
        "Every trail starts with a single step. {brand_name} provides {product_name} worthy of the journey you are planning.",
        "Adventure does not wait for perfect conditions. {brand_name} designs {product_name} that do not either.",
    ],
    "home": [
        "{brand_name} exists to make home feel like a sigh of relief. Our {product_name} turn rooms into sanctuaries.",
        "We design {product_name} for the small, daily rituals that make a space truly yours.",
        "Home is where the story begins. {brand_name} creates {product_name} that become the quiet backdrop to your best days.",
        "Comfort should never be boring. {brand_name} makes {product_name} that balance softness, style and purpose.",
        "Our mission is to bring thoughtfulness home. {brand_name} offers {product_name} that make everyday living feel considered.",
    ],
    "animals": [
        "{brand_name} exists because pets deserve joy. We create {product_name} that keep tails wagging and purrs rumbling.",
        "Pets are family. {brand_name} designs {product_name} that honor the unconditional love they give us every day.",
        "We believe happy pets make happy homes. {brand_name} builds {product_name} for the four-legged members of the household.",
        "Every dog walk and cat nap matters. {brand_name} makes {product_name} that make those moments even better.",
        "At {brand_name}, our mission is to care for the companions who never stop caring for us. Our {product_name} do exactly that.",
    ],
    "baby": [
        "{brand_name} exists to protect the smallest moments. We create {product_name} that give parents one less thing to worry about.",
        "Every parent deserves confidence. {brand_name} designs {product_name} that make the early days a little softer.",
        "We believe safety and sweetness should go hand in hand. {brand_name} makes {product_name} for the people who hold tomorrow.",
        "Tiny hands, big love. {brand_name} provides {product_name} that support the beautiful chaos of growing families.",
        "Our mission is simple: help parents breathe easier. {brand_name} offers {product_name} built on care, calm and trust.",
    ],
    "gaming": [
        "{brand_name} exists to give players the edge. We create {product_name} that turn split-second reactions into victories.",
        "Gaming is passion, precision and play. {brand_name} designs {product_name} for competitors who refuse to settle.",
        "We believe the right gear changes the game. {brand_name} makes {product_name} that keep up with your fastest reflexes.",
        "Every frame matters. {brand_name} builds {product_name} that help you perform when the match is on the line.",
        "At {brand_name}, victory is built on details. Our {product_name} are made for the players who notice all of them.",
    ],
    "travel": [
        "{brand_name} exists to make every departure smoother. We create {product_name} for the travelers who chase horizons.",
        "Wanderlust deserves better gear. {brand_name} designs {product_name} that keep up with passport stamps and spontaneous plans.",
        "We believe the world gets bigger with the right bag. {brand_name} makes {product_name} for journeys planned and unplanned.",
        "Travel is the only thing you buy that makes you richer. {brand_name} provides {product_name} that protect that investment.",
        "At {brand_name}, every product is an invitation. Our {product_name} are made for people who say yes to the next trip.",
    ],
}

VISION_TEMPLATES: Dict[str, List[str]] = {
    "fitness": [
        "To become the most trusted fitness companion for athletes at every level.",
        "A world where everyone has the tools to move with strength and confidence.",
        "The first name people think of when they decide to become stronger.",
    ],
    "cuisine": [
        "To inspire a new generation of home cooks who cook with heart.",
        "A kitchen in every home where great food and great memories are made.",
        "The brand that turns everyday cooking into a creative adventure.",
    ],
    "beauty": [
        "To redefine beauty as a feeling of confidence that comes from within.",
        "A world where skincare is simple, honest and truly personal.",
        "The most loved beauty brand for people who choose quality over hype.",
    ],
    "tech": [
        "To build technology that feels invisible, helpful and human.",
        "A future where the best tools are also the simplest to use.",
        "The brand that makes advanced technology feel approachable for everyone.",
    ],
    "outdoor": [
        "To inspire deeper, longer, more meaningful time outside.",
        "A world where more people choose the trail over the screen.",
        "The outdoor brand built by explorers, for explorers.",
    ],
    "home": [
        "To make thoughtful design a standard in every home.",
        "A world where the objects we live with bring us daily joy.",
        "The home brand that turns ordinary spaces into personal sanctuaries.",
    ],
    "animals": [
        "To make every pet feel celebrated, comfortable and loved.",
        "A world where pet care is as thoughtful as pet love.",
        "The pet brand that families trust for wagging tails and happy naps.",
    ],
    "baby": [
        "To become the brand every parent reaches for on day one.",
        "A world where baby care is gentle, reliable and beautifully simple.",
        "The trusted name in products that help families grow with confidence.",
    ],
    "gaming": [
        "To equip every player with the precision they need to perform.",
        "A community where the right gear turns passion into achievement.",
        "The gaming brand that pros and dreamers choose first.",
    ],
    "travel": [
        "To make travel lighter, freer and more joyful for everyone.",
        "A world where the journey is as well-prepared as the destination.",
        "The travel brand that adventurers never leave behind.",
    ],
}

VALUES_BANKS: Dict[str, List[str]] = {
    "fitness": ["performance", "discipline", "progress", "resilience"],
    "cuisine": ["flavor", "craft", "sharing", "freshness"],
    "beauty": ["care", "transparency", "radiance", "self-love"],
    "tech": ["simplicity", "innovation", "reliability", "humanity"],
    "outdoor": ["adventure", "durability", "respect for nature", "freedom"],
    "home": ["comfort", "thoughtfulness", "style", "warmth"],
    "animals": ["joy", "trust", "companionship", "care"],
    "baby": ["safety", "gentleness", "trust", "simplicity"],
    "gaming": ["precision", "passion", "competition", "play"],
    "travel": ["freedom", "curiosity", "preparedness", "discovery"],
}


def _normalize_category(category: str) -> str:
    return category.lower().strip() if category else "tech"


def _pick_index(key: str, options: List[str]) -> int:
    h = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)
    return h % len(options)


def _personality_from_vibe(vibe: str) -> str:
    vibe = (vibe or "").lower()
    if "luxury" in vibe or "premium" in vibe or "elegant" in vibe:
        return "refined"
    if "playful" in vibe or "fun" in vibe or "joy" in vibe:
        return "playful"
    if "adventure" in vibe or "wild" in vibe or "bold" in vibe:
        return "adventurous"
    if "calm" in vibe or "gentle" in vibe or "caring" in vibe:
        return "gentle"
    if "future" in vibe or "modern" in vibe or "tech" in vibe:
        return "futuristic"
    return "confident"


class IdentityEngine(BaseBrandEngine):
    """Engine for generating brand identity (mission, vision, values)."""
    
    async def generate(self, context: Dict[str, Any]) -> EngineResult:
        """Generate brand identity."""
        try:
            template = prompt_library.get_template("mission_vision")
            if not template:
                return EngineResult(
                    engine_name=self.engine_name,
                    success=False,
                    data={},
                    confidence=0,
                    metadata={"error": "Template not found"}
                )
            
            config = prompt_library.get_template_config("mission_vision") or {}
            
            prompt = prompt_library.render_template(
                "mission_vision",
                category=context.get("category", "product"),
                brand_name=context.get("brand_name", "Brand"),
                product_name=context.get("product_name", "Product"),
                target_audience=context.get("target_audience", "general consumers"),
                unique_value=context.get("unique_value", "quality")
            )
            
            if self.ai_provider:
                result = await self.ai_provider.generate(
                    prompt=prompt,
                    temperature=config.get("temperature", 0.7),
                    max_tokens=config.get("max_tokens", 400)
                )
                
                return EngineResult(
                    engine_name=self.engine_name,
                    success=True,
                    data={"raw_result": result, "identity": self._parse_identity(result)},
                    confidence=75,
                    metadata={"template_version": template.version}
                )
            else:
                return self._mock_generate(context)
                
        except Exception as e:
            return EngineResult(
                engine_name=self.engine_name,
                success=False,
                data={},
                confidence=0,
                metadata={"error": str(e)}
            )
    
    def _parse_identity(self, result: str) -> Dict[str, Any]:
        """Parse AI result into identity."""
        return {"raw": result}
    
    def _mock_generate(self, context: Dict[str, Any]) -> EngineResult:
        """Mock generation with diverse, category-aware mission/vision."""
        brand_name = context.get("brand_name", "Brand")
        product_name = context.get("product_name", "Product")
        category = _normalize_category(context.get("category", "tech"))
        vibe = context.get("vibe", "")
        audience = context.get("target_audience", "everyone")
        personality = _personality_from_vibe(vibe)
        
        # Include audience and personality in the selection key for extra variety
        selection_key = f"{brand_name}:{product_name}:{audience}:{personality}"
        
        missions = MISSION_TEMPLATES.get(category, MISSION_TEMPLATES["tech"])
        mission = missions[_pick_index(selection_key, missions)]
        
        visions = VISION_TEMPLATES.get(category, VISION_TEMPLATES["tech"])
        vision = visions[_pick_index(selection_key + ":vision", visions)]
        
        values = VALUES_BANKS.get(category, VALUES_BANKS["tech"])
        values = values[:3] + [personality] if personality != "confident" else values
        
        return EngineResult(
            engine_name=self.engine_name,
            success=True,
            data={
                "identity": {
                    "mission": mission.format(brand_name=brand_name, product_name=product_name),
                    "vision": vision,
                    "values": values,
                    "personality": personality,
                }
            },
            confidence=60,
            metadata={"method": "mock"}
        )
