"""Analyzer prompts for user and query analysis."""

USER_ANALYSIS_PROMPT = """Analyze this person's photo and extract the following information.
Look carefully at their physical characteristics and any visible clothing.

Extract:
1. Body shape: slim / average / athletic / plus-size
2. Skin tone: fair / medium / tan / dark
3. Apparent gender: male / female / neutral
4. Current outfit style (if visible): describe briefly

Return ONLY a valid JSON object with no additional text:
{
    "body_shape": "...",
    "skin_tone": "...",
    "gender": "...",
    "current_style": "..."
}
"""

QUERY_ANALYSIS_PROMPT = """
You are a fashion and costume query analysis engine.

Your task is to extract structured clothing-related requirements from any user request,
including normal fashion, themed outfits, costumes, cosplay, uniforms, cultural wear,
or event-specific clothing.

User request:
{query}

IMPORTANT RULES:

1. Extract only information explicitly mentioned or clearly implied.
2. Do NOT hallucinate missing details.
3. If a field is not mentioned, return "not specified".
4. If multiple values are strongly implied, choose the most dominant one.
5. Always interpret special-event outfits (e.g., Halloween costume, cosplay, Christmas outfit)
   as valid clothing requests.
6. The "query" field in the output must exactly match the original user request.
7. Return ONLY valid JSON. No explanations. No markdown. No extra text.

----------------------------------------
FIELD DEFINITIONS
----------------------------------------

1. style:
General aesthetic or theme of the outfit.
Examples:
casual, formal, vintage, streetwear, minimalist, bohemian, preppy,
athletic, business, elegant, chic, edgy, sporty,
costume, cosplay, fantasy, historical, cultural, uniform, other

If the request is for a character or themed costume
(e.g., vampire, superhero, anime character),
set style = "costume" unless a clearer aesthetic is specified.

2. occasion:
The purpose or event where the outfit will be worn.
Examples:
work, party, date, travel, daily, wedding, interview,
gym, beach, festival, halloween, christmas,
themed-event, performance, cosplay-event, other

If the request is for a specific holiday or event,
use the closest matching category.

3. weather:
hot, cold, mild, rainy, snowy, not specified

Infer ONLY if clearly implied (e.g., "winter coat" → cold).

4. items:
List specific clothing items mentioned.
Examples:
dress, jeans, blazer, suit, shirt, t-shirt, hoodie,
skirt, shorts, trousers, coat, jacket,
sneakers, boots, heels, sandals,
costume, mask, cape, uniform, other

Return empty list if none mentioned.

5. colors:
List explicitly mentioned colors only.
If vague (e.g., "dark colors", "bright"), keep the phrase.

Return empty list if none mentioned.

6. budget:
luxury, premium, mid-range, affordable, budget, not specified

Only extract if clearly stated (e.g., "cheap", "high-end designer").

----------------------------------------
OUTPUT FORMAT (STRICT JSON ONLY)
----------------------------------------

{{
    "query": "{query}",
    "style": "...",
    "occasion": "...",
    "weather": "...",
    "items": [...],
    "colors": [...],
    "budget": "..."
}}
"""

# QUERY_ANALYSIS_PROMPT = """Analyze this fashion request and extract the key requirements.

# User request: {query}

# Extract:
# 1. Desired style: casual / formal / vintage / streetwear / minimalist / bohemian / preppy / athletic / other
# 2. Occasion: work / party / date / travel / daily / wedding / interview / gym / beach / other
# 3. Weather hints: hot / cold / mild / rainy / not specified
# 4. Specific items mentioned: list any specific garment types (e.g., dress, jeans, blazer)
# 5. Color preferences: any colors mentioned
# 6. Budget hints: luxury / affordable / not specified

# Return ONLY a valid JSON object with no additional text:
# {{
#     "style": "...",
#     "occasion": "...",
#     "weather": "...",
#     "items": [...],
#     "colors": [...],
#     "budget": "..."
# }}
# """

SEARCH_KEYWORDS_PROMPT = """Based on the user profile and their fashion request, generate SEPARATE search keywords for TOPS and BOTTOMS.

User Profile:
- Body shape: {body_shape}
- Skin tone: {skin_tone}
- Gender: {gender}

Fashion Request:
- Style: {style}
- Occasion: {occasion}
- Weather: {weather}
- Specific items: {items}
- Color preferences: {colors}

Original Query: {query}

Generate SEPARATE keyword combinations for:
1. TOPS (shirts, t-shirts, blouses, sweaters, jackets, etc.) - 3-4 keywords
2. BOTTOMS (pants, jeans, shorts, skirts, etc.) - 3-4 keywords

IMPORTANT:
- Each keyword MUST include the gender prefix (e.g., "men", "women")
- Each keyword for TOPS must include a top-specific term (shirt, t-shirt, blouse, jacket, etc.)
- Each keyword for BOTTOMS must include a bottom-specific term (pants, jeans, shorts, skirt, etc.)
- Consider colors that complement the user's skin tone
- Consider styles that flatter the user's body shape

Return ONLY a valid JSON object with no additional text:
{{
    "tops_keywords": [
        "men casual linen shirt summer",
        "men beach shirt lightweight",
        ...
    ],
    "bottoms_keywords": [
        "men khaki shorts casual",
        "men beach shorts swim",
        ...
    ],
    "recommended_colors": ["color1", "color2"],
    "reasoning": "brief explanation of why these keywords were chosen"
}}
"""

GARMENT_CLASSIFICATION_PROMPT = """Analyze this garment image and classify it.

Determine:
1. Category: Is this garment for the upper body (tops), lower body (bottoms), or a full-body piece (one-pieces)?
   - tops: shirts, t-shirts, blouses, sweaters, jackets, coats, vests
   - bottoms: pants, jeans, shorts, skirts
   - one-pieces: dresses, jumpsuits, rompers, overalls

2. Photo type: Is this a model photo (worn by a person) or a flat-lay (product shot on plain background)?
   - model: garment is being worn by a person
   - flat-lay: garment is laid flat or on a mannequin/hanger

Return ONLY a valid JSON object with no additional text:
{
    "category": "tops" | "bottoms" | "one-pieces",
    "photo_type": "model" | "flat-lay",
    "description": "brief description of the garment"
}
"""
