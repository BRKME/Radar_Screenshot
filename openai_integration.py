"""
OpenAI Integration для AI комментариев к скриншотам
Version: 2.0.0 - Hashtags on top, max 2 short
Генерирует краткие комментарии и определяет сентимент (Bullish/Bearish/Neutral)

ОБНОВЛЕНО В v2.0.0:
- Хэштеги теперь ВВЕРХУ caption
- Максимум 2 хэштега
- Максимум 10 символов на хэштег (без #)
- Добавлены промпты для heatmap_blockchain и crypto_liquidations
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


# Промпты для разных типов источников - Alpha Take + Context Tag + AI Hashtags
SOURCE_PROMPTS = {
    "fear_greed": """You are a crypto market analyst. Analyze the Fear & Greed Index and explain what it means for prices.

OUTPUT FORMAT:
INDICATOR_LINE: Fear & Greed Index at [X] ([label])
ALPHA_TAKE: One clear sentence explaining: Will prices likely go UP, DOWN, or SIDEWAYS in the coming days/weeks and WHY. Use simple language. Be specific.
CONTEXT_TAG: [Strength] [Sentiment] (Strength: Low/Medium/High/Moderate/Strong, Sentiment: Neutral/Negative/Positive/Critical/Hype)
HASHTAGS: 2 short hashtags (max 10 chars each, like #Bitcoin #Crypto)

Example:
INDICATOR_LINE: Fear & Greed Index at 26 (Extreme Fear)
ALPHA_TAKE: Extreme fear usually means prices are near bottom and likely to bounce up in 1-2 weeks as scared sellers finish selling and buyers see opportunity.
CONTEXT_TAG: Strong negative
HASHTAGS: #Bitcoin #Fear
""",
    
    "altcoin_season": """You are a crypto market analyst. Analyze the Altcoin Season Index and explain what it means for prices.

OUTPUT FORMAT:
INDICATOR_LINE: Altcoin Season Index at [X]
ALPHA_TAKE: One clear sentence: Are altcoins likely to rise or fall vs Bitcoin, and why. Use simple language.
CONTEXT_TAG: [Strength] [Sentiment]
HASHTAGS: 2 short hashtags (max 10 chars each)

Example:
INDICATOR_LINE: Altcoin Season Index at 32 (Bitcoin Season)
ALPHA_TAKE: Bitcoin is sucking up all the money right now, so altcoins will likely keep falling or stay flat until Bitcoin stabilizes or crashes.
CONTEXT_TAG: Moderate negative
HASHTAGS: #Altcoins #Bitcoin
""",
    
    "btc_dominance": """You are a crypto market analyst. Analyze Bitcoin Dominance and explain what it means for prices.

OUTPUT FORMAT:
INDICATOR_LINE: Bitcoin Dominance at [X]%
ALPHA_TAKE: One clear sentence: Will altcoins rise or fall relative to Bitcoin, and why. Simple language.
CONTEXT_TAG: [Strength] [Sentiment]
HASHTAGS: 2 short hashtags (max 10 chars each)

Example:
INDICATOR_LINE: Bitcoin Dominance at 58%
ALPHA_TAKE: High dominance means investors prefer Bitcoin safety over risky altcoins, so altcoin prices will likely stay weak until dominance drops.
CONTEXT_TAG: Moderate negative
HASHTAGS: #Bitcoin #Dominance
""",
    
    "eth_etf": """You are a crypto market analyst. Analyze Ethereum ETF flows and explain what it means for ETH price.

OUTPUT FORMAT:
INDICATOR_LINE: ETH ETF net [inflow/outflow]: $[X]M
ALPHA_TAKE: One clear sentence: Will ETH price go up or down based on these flows, and why. Simple language.
CONTEXT_TAG: [Strength] [Sentiment]
HASHTAGS: 2 short hashtags (max 10 chars each)

Example:
INDICATOR_LINE: ETH ETF net outflow: -$75M
ALPHA_TAKE: Big money is pulling out of ETH, which usually means price will drop or stay weak for the next week until selling pressure eases.
CONTEXT_TAG: Strong negative
HASHTAGS: #Ethereum #ETF
""",
    
    "btc_etf": """You are a crypto market analyst. Analyze Bitcoin ETF flows and explain what it means for BTC price.

OUTPUT FORMAT:
INDICATOR_LINE: BTC ETF net [inflow/outflow]: $[X]M
ALPHA_TAKE: One clear sentence: Will BTC price go up or down based on these flows, and why. Simple language.
CONTEXT_TAG: [Strength] [Sentiment]
HASHTAGS: 2 short hashtags (max 10 chars each)

Example:
INDICATOR_LINE: BTC ETF net inflow: +$120M
ALPHA_TAKE: Big institutions are buying Bitcoin through ETFs, which usually pushes price higher over the next 1-2 weeks as demand exceeds selling.
CONTEXT_TAG: Strong positive
HASHTAGS: #Bitcoin #ETF
""",
    
    "top_gainers": """You are a crypto market analyst. Analyze Top Gainers and explain what it means for the market.

OUTPUT FORMAT:
INDICATOR_LINE: Top gainers led by [sector/theme]: [token examples]
ALPHA_TAKE: One clear sentence: What does this rally tell us about where prices are headed, and why. Simple language.
CONTEXT_TAG: [Strength] [Sentiment]
HASHTAGS: 2 short hashtags (max 10 chars each)

Example:
INDICATOR_LINE: Top gainers led by AI tokens: FET, AGIX, RNDR
ALPHA_TAKE: AI tokens pumping hard means speculative money is flowing into risky coins, which usually signals short-term gains but often leads to sharp drops within days.
CONTEXT_TAG: Moderate hype
HASHTAGS: #Crypto #Gainers
""",
    
    "heatmap": """You are a crypto market analyst. Analyze the market heatmap and explain what it means for overall crypto prices.

OUTPUT FORMAT:
INDICATOR_LINE: Market breadth: [narrow/wide], [concentrated/diversified]
ALPHA_TAKE: One clear sentence: Are most coins rising or falling, and what does this mean for prices this week. Simple language.
CONTEXT_TAG: [Strength] [Sentiment]
HASHTAGS: 2 short hashtags (max 10 chars each)

Example:
INDICATOR_LINE: Market breadth: narrow, concentrated in BTC
ALPHA_TAKE: Only Bitcoin is green while most altcoins are red, which means overall crypto prices will likely stay weak until money spreads to other coins.
CONTEXT_TAG: Moderate negative
HASHTAGS: #Crypto #Heatmap
""",

    "heatmap_blockchain": """You are a crypto market analyst. Analyze the market heatmap and explain what it means for overall crypto prices.

OUTPUT FORMAT:
INDICATOR_LINE: Market breadth: [narrow/wide], [green/red dominant]
ALPHA_TAKE: One clear sentence: Are most coins rising or falling, and what does this mean for prices this week. Simple language.
CONTEXT_TAG: [Strength] [Sentiment]
HASHTAGS: 2 short hashtags (max 10 chars each)

Example:
INDICATOR_LINE: Market breadth: wide, green dominant
ALPHA_TAKE: Most coins are in the green which signals healthy market conditions - expect continued upward momentum for the next few days.
CONTEXT_TAG: Moderate positive
HASHTAGS: #Crypto #Heatmap
""",

    "crypto_liquidations": """You are a crypto market analyst. Analyze the liquidations data and explain what it means for prices.

OUTPUT FORMAT:
INDICATOR_LINE: Liquidations: $[X]M ([long/short] dominant)
ALPHA_TAKE: One clear sentence: What do these liquidations tell us about price direction. Simple language.
CONTEXT_TAG: [Strength] [Sentiment]
HASHTAGS: 2 short hashtags (max 10 chars each)

Example:
INDICATOR_LINE: Liquidations: $150M (long dominant)
ALPHA_TAKE: Heavy long liquidations mean overleveraged bulls got wiped out - prices may stabilize or bounce as selling pressure eases.
CONTEXT_TAG: Medium negative
HASHTAGS: #Bitcoin #Trading
""",

    "trending_coins": """You are a crypto market analyst. Analyze the Trending Coins list and explain what it means for the market.

OUTPUT FORMAT:
INDICATOR_LINE: Top trending: [coin1], [coin2], [coin3]
ALPHA_TAKE: One clear sentence: What does this trending list tell us about market sentiment and where money is flowing. Simple language.
CONTEXT_TAG: [Strength] [Sentiment]
HASHTAGS: 2 short hashtags (max 10 chars each)

Example:
INDICATOR_LINE: Top trending: PEPE, SHIB, DOGE
ALPHA_TAKE: Memecoins dominating trends signals retail FOMO is back - expect volatile pumps but watch for sharp reversals within days.
CONTEXT_TAG: Moderate hype
HASHTAGS: #Crypto #Trending
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
            model="gpt-4o-mini",
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
            max_tokens=200,
            temperature=0.7
        )
        
        # Парсим ответ
        content = response.choices[0].message.content.strip()
        logger.info(f"  OpenAI response: {content}")
        
        # Извлекаем INDICATOR_LINE, ALPHA_TAKE, CONTEXT_TAG и HASHTAGS
        indicator_line = None
        alpha_take = None
        context_tag = None
        hashtags = None
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('INDICATOR_LINE:'):
                indicator_line = line.replace('INDICATOR_LINE:', '').strip()
            elif line.startswith('ALPHA_TAKE:'):
                alpha_take = line.replace('ALPHA_TAKE:', '').strip()
            elif line.startswith('CONTEXT_TAG:'):
                context_tag = line.replace('CONTEXT_TAG:', '').strip()
            elif line.startswith('HASHTAGS:'):
                hashtags = line.replace('HASHTAGS:', '').strip()
        
        # Валидация
        if not alpha_take:
            logger.warning(f"Could not parse Alpha Take from response")
            logger.warning(f"  Response: {content}")
            # Fallback: используем весь ответ если нет маркера
            alpha_take = content
        
        if indicator_line:
            logger.info(f"  ✓ Indicator Line: {indicator_line}")
        logger.info(f"  ✓ Alpha Take: {alpha_take}")
        if context_tag:
            logger.info(f"  ✓ Context Tag: {context_tag}")
        if hashtags:
            logger.info(f"  ✓ Hashtags: {hashtags}")
        
        return {
            "indicator_line": indicator_line,  # NEW!
            "alpha_take": alpha_take,
            "context_tag": context_tag,
            "hashtags": hashtags
        }
        
    except Exception as e:
        logger.error(f"Error getting Alpha Take: {e}")
        import traceback
        traceback.print_exc()
        return None


def sanitize_hashtags(hashtags, max_count=2, max_length=10):
    """
    Фильтрует хэштеги: max 2, короткие (<=10 символов без #)
    
    Args:
        hashtags: Строка с хэштегами
        max_count: Максимальное количество
        max_length: Максимальная длина (без #)
    
    Returns:
        str: Отфильтрованные хэштеги
    """
    if not hashtags:
        return ""
    
    tags = [tag.strip() for tag in hashtags.split() if tag.startswith('#')]
    
    if not tags:
        return ""
    
    # Фильтруем по длине (без #)
    valid_tags = [tag for tag in tags if len(tag) - 1 <= max_length]
    
    # Берём max_count
    result_tags = valid_tags[:max_count]
    
    return ' '.join(result_tags)


def add_alpha_take_to_caption(title, hashtags_fallback, ai_result):
    """
    Добавляет Alpha Take к caption с правильным форматированием
    
    v2.0.0: Хэштеги ВВЕРХУ, максимум 2 коротких
    
    Format:
    <hashtags>
    <title>
    <indicator_line>
    
    Alpha Take
    <alpha_take text>
    
    Context: <context_tag>
    
    Args:
        title: Заголовок поста
        hashtags_fallback: Хештеги fallback (если AI не сгенерировал)
        ai_result: Результат от get_ai_comment()
        
    Returns:
        str: Caption с Alpha Take
    """
    if not ai_result:
        # Без AI - старый формат (hashtags + title)
        clean_hashtags = sanitize_hashtags(hashtags_fallback, max_count=2, max_length=10)
        return f"{clean_hashtags}\n<b>{title}</b>"
    
    indicator_line = ai_result.get('indicator_line')
    alpha_take = ai_result['alpha_take']
    context_tag = ai_result.get('context_tag')
    hashtags_ai = ai_result.get('hashtags')
    
    # Используем AI хештеги если есть, иначе fallback
    hashtags_raw = hashtags_ai if hashtags_ai else hashtags_fallback
    
    # Применяем политику: max 2 коротких хэштега
    hashtags = sanitize_hashtags(hashtags_raw, max_count=2, max_length=10)
    
    # Новый формат: Hashtags -> Title -> Indicator Line -> Alpha Take -> Context Tag
    caption = f"{hashtags}\n" if hashtags else ""
    caption += f"<b>{title}</b>\n"
    
    # Добавляем indicator line если есть
    if indicator_line:
        caption += f"{indicator_line}\n"
    
    caption += f"\n<b>📡 Alpha Take</b>\n"
    caption += f"{alpha_take}\n\n"
    
    # Добавляем Context Tag если есть
    if context_tag:
        caption += f"<i>Context: {context_tag}</i>"
    
    return caption
