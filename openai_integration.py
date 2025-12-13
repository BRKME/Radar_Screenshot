"""
OpenAI Integration для AI комментариев к скриншотам
Version: 1.0.0
Генерирует краткие комментарии и определяет сентимент (Bullish/Bearish/Neutral)
"""

import os
import logging
import base64
from openai import OpenAI

logger = logging.getLogger(__name__)

# OpenAI API Key
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Инициализация клиента
client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("✓ OpenAI client initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize OpenAI client: {e}")
        client = None
else:
    logger.warning("⚠️ OPENAI_API_KEY not found - AI comments disabled")


# Промпты для разных типов источников - Alpha Take Style
SOURCE_PROMPTS = {
    "fear_greed": """You are a professional crypto market analyst writing for a US-based institutional audience.

Analyze this Fear & Greed Index screenshot and provide an Alpha Take.

Rules:
- Write 2-4 sentences in clear, professional American English
- Explain why this level matters NOW and potential market behavior
- Use probabilistic language (historically, often, tends to, may)
- NO price targets, NO trading calls, NO hype, NO emojis
- Focus on context and historical patterns

Format your response as:
ALPHA_TAKE: [your 2-4 sentence analysis]

Example: "Extended fear zones have historically coincided with defensive positioning and lower volumes, often setting the stage for short-term relief moves if macro conditions stabilize. This environment favors patience and selectivity rather than aggressive risk-taking."
""",
    
    "altcoin_season": """You are a professional crypto market analyst writing for a US-based institutional audience.

Analyze this Altcoin Season Index screenshot and provide an Alpha Take.

Rules:
- Write 2-4 sentences in clear, professional American English
- Explain what the current reading means for market rotation and positioning
- Use probabilistic language (historically, often, tends to, may)
- NO price targets, NO trading calls, NO hype, NO emojis
- Focus on capital flows and regime shifts

Format your response as:
ALPHA_TAKE: [your 2-4 sentence analysis]

Example: "Readings below 25 indicate capital is rotating into Bitcoin, often reflecting risk-off sentiment within crypto. Historically, sustained Bitcoin dominance has preceded either broader market weakness or accumulation phases before the next alt cycle."
""",
    
    "btc_dominance": """You are a professional crypto market analyst writing for a US-based institutional audience.

Analyze this Bitcoin Dominance screenshot and provide an Alpha Take.

Rules:
- Write 2-4 sentences in clear, professional American English  
- Explain what current dominance means for market structure
- Use probabilistic language (historically, often, tends to, may)
- NO price targets, NO trading calls, NO hype, NO emojis
- Focus on capital rotation and risk appetite

Format your response as:
ALPHA_TAKE: [your 2-4 sentence analysis]

Example: "Bitcoin dominance near 60% typically signals risk-off behavior within crypto, with capital flowing into the perceived safety of BTC. This environment often persists until macro clarity improves or BTC itself establishes a clearer trend."
""",
    
    "eth_etf": """You are a professional crypto market analyst writing for a US-based institutional audience.

Analyze this Ethereum ETF flows screenshot and provide an Alpha Take.

Rules:
- Write 2-4 sentences in clear, professional American English
- Explain what the flow trends indicate about institutional demand
- Use probabilistic language (historically, often, tends to, may)
- NO price targets, NO trading calls, NO hype, NO emojis
- Focus on flow patterns and demand signals

Format your response as:
ALPHA_TAKE: [your 2-4 sentence analysis]

Example: "Mixed daily flows with negative monthly performance suggest institutions remain cautious on ETH exposure. This consolidation pattern often precedes either a catalyst-driven shift or extended sideways action until fundamentals re-rate."
""",
    
    "btc_etf": """You are a professional crypto market analyst writing for a US-based institutional audience.

Analyze this Bitcoin ETF flows screenshot and provide an Alpha Take.

Rules:
- Write 2-4 sentences in clear, professional American English
- Explain what the flow trends signal about institutional appetite
- Use probabilistic language (historically, often, tends to, may)
- NO price targets, NO trading calls, NO hype, NO emojis
- Focus on demand dynamics and flow sustainability

Format your response as:
ALPHA_TAKE: [your 2-4 sentence analysis]

Example: "Sustained positive inflows after a period of outflows typically signal renewed institutional interest, though the magnitude matters more than direction alone. If this trend continues alongside improving macro conditions, it could support a more constructive setup."
""",
    
    "top_gainers": """You are a professional crypto market analyst writing for a US-based institutional audience.

Analyze this Top Gainers screenshot and provide an Alpha Take.

Rules:
- Write 2-4 sentences in clear, professional American English
- Explain what the gaining tokens reveal about market themes and risk appetite
- Use probabilistic language (historically, often, tends to, may)
- NO price targets, NO trading calls, NO hype, NO emojis
- Focus on rotation patterns and sector strength

Format your response as:
ALPHA_TAKE: [your 2-4 sentence analysis]

Example: "Multiple double-digit gainers across infrastructure tokens suggest rotation into fundamental-driven narratives rather than pure speculation. This pattern often emerges when risk appetite is improving but not yet fully extended, favoring selective positioning over broad exposure."
""",
    
    "token_unlocks": """You are a professional crypto market analyst writing for a US-based institutional audience.

Analyze this Token Unlocks screenshot and provide an Alpha Take.

Rules:
- Write 2-4 sentences in clear, professional American English
- Explain the potential impact of upcoming unlocks on supply dynamics
- Use probabilistic language (historically, often, tends to, may)
- NO price targets, NO trading calls, NO hype, NO emojis
- Focus on supply pressure and market absorption

Format your response as:
ALPHA_TAKE: [your 2-4 sentence analysis]

Example: "Upcoming cliff unlocks totaling $98M are significant but manageable given current market depth. Historically, well-telegraphed unlocks see selling pressure frontrun, with actual unlock dates often marking local lows if broader market conditions hold."
""",
    
    "heatmap": """You are a professional crypto market analyst writing for a US-based institutional audience.

Analyze this Crypto Market Heatmap and provide an Alpha Take.

Rules:
- Write 2-4 sentences in clear, professional American English
- Explain what the overall performance pattern reveals about market structure
- Use probabilistic language (historically, often, tends to, may)
- NO price targets, NO trading calls, NO hype, NO emojis
- Focus on breadth, rotation, and risk distribution

Format your response as:
ALPHA_TAKE: [your 2-4 sentence analysis]

Example: "Broad-based weakness across mid-caps while large-caps hold suggests defensive positioning and liquidity contraction. This setup often persists until either catalysts emerge or capitulation creates asymmetric entry points in quality names."
"""
}


def encode_image_to_base64(image_path):
    """Конвертирует изображение в base64 для OpenAI API"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image: {e}")
        return None


def get_ai_comment(source_key, image_path):
    """
    Получает AI Alpha Take от OpenAI для скриншота
    
    Args:
        source_key: Ключ источника (fear_greed, btc_etf, etc)
        image_path: Путь к изображению скриншота
        
    Returns:
        dict: {"alpha_take": "..."}
        или None если ошибка
    """
    if not client:
        logger.warning("OpenAI client not initialized - skipping AI comment")
        return None
    
    try:
        # Получаем промпт для этого источника
        prompt = SOURCE_PROMPTS.get(source_key)
        if not prompt:
            logger.warning(f"No prompt configured for source: {source_key}")
            return None
        
        # Кодируем изображение в base64
        base64_image = encode_image_to_base64(image_path)
        if not base64_image:
            return None
        
        logger.info(f"🤖 Requesting Alpha Take from OpenAI for {source_key}...")
        
        # Вызываем OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Быстрая модель с vision
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=200,  # Увеличено для Alpha Take (2-4 предложения)
            temperature=0.7
        )
        
        # Парсим ответ
        content = response.choices[0].message.content.strip()
        logger.info(f"  OpenAI response: {content}")
        
        # Извлекаем ALPHA_TAKE
        alpha_take = None
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('ALPHA_TAKE:'):
                alpha_take = line.replace('ALPHA_TAKE:', '').strip()
                break
        
        # Валидация
        if not alpha_take:
            logger.warning(f"Could not parse Alpha Take from response")
            logger.warning(f"  Response: {content}")
            # Fallback: используем весь ответ если нет маркера
            alpha_take = content
        
        logger.info(f"  ✓ Alpha Take: {alpha_take}")
        
        return {
            "alpha_take": alpha_take
        }
        
    except Exception as e:
        logger.error(f"Error getting Alpha Take: {e}")
        import traceback
        traceback.print_exc()
        return None


def add_alpha_take_to_caption(title, hashtags, ai_result):
    """
    Добавляет Alpha Take к caption с правильным форматированием
    
    Format:
    <title>
    
    Alpha Take
    <alpha_take text>
    
    <hashtags>
    
    Args:
        title: Заголовок поста
        hashtags: Хештеги
        ai_result: Результат от get_ai_comment()
        
    Returns:
        str: Caption с Alpha Take
    """
    if not ai_result:
        # Без AI - старый формат (title + hashtags)
        return f"<b>{title}</b>\n\n{hashtags}"
    
    alpha_take = ai_result['alpha_take']
    
    # Новый формат: Title -> Alpha Take -> Alpha take text -> Hashtags
    caption = f"<b>{title}</b>\n\n"
    caption += f"<b>Alpha Take</b>\n"
    caption += f"{alpha_take}\n\n"
    caption += f"{hashtags}"
    
    return caption
