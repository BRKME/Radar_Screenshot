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
    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("✓ OpenAI client initialized")
else:
    logger.warning("⚠️ OPENAI_API_KEY not found - AI comments disabled")


# Промпты для разных типов источников
SOURCE_PROMPTS = {
    "fear_greed": """Analyze this Fear & Greed Index screenshot. 
Provide a brief 1-2 sentence summary of the current market sentiment and what it means.
Then classify the overall sentiment as: Bullish, Bearish, or Neutral.""",
    
    "altcoin_season": """Analyze this Altcoin Season Index screenshot.
Provide a brief 1-2 sentence summary about whether we're in altcoin season or bitcoin season and what this means for traders.
Then classify the overall sentiment as: Bullish, Bearish, or Neutral.""",
    
    "btc_dominance": """Analyze this Bitcoin Dominance screenshot.
Provide a brief 1-2 sentence summary of Bitcoin's market dominance and its implications.
Then classify the overall sentiment as: Bullish, Bearish, or Neutral.""",
    
    "eth_etf": """Analyze this Ethereum ETF flows screenshot.
Provide a brief 1-2 sentence summary of the ETF flow trends and what they indicate.
Then classify the overall sentiment as: Bullish, Bearish, or Neutral.""",
    
    "btc_etf": """Analyze this Bitcoin ETF flows screenshot.
Provide a brief 1-2 sentence summary of the ETF flow trends and what they indicate.
Then classify the overall sentiment as: Bullish, Bearish, or Neutral.""",
    
    "top_gainers": """Analyze this Top Gainers screenshot.
Provide a brief 1-2 sentence summary of which tokens are pumping the most and overall market sentiment.
Then classify the overall sentiment as: Bullish, Bearish, or Neutral.""",
    
    "token_unlocks": """Analyze this Token Unlocks screenshot.
Provide a brief 1-2 sentence summary of upcoming cliff unlocks and potential market impact.
Then classify the overall sentiment as: Bullish, Bearish, or Neutral.""",
    
    "heatmap": """Analyze this Crypto Market Heatmap.
Provide a brief 1-2 sentence summary of overall market performance and key trends.
Then classify the overall sentiment as: Bullish, Bearish, or Neutral."""
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
    Получает AI комментарий от OpenAI для скриншота
    
    Args:
        source_key: Ключ источника (fear_greed, btc_etf, etc)
        image_path: Путь к изображению скриншота
        
    Returns:
        dict: {"comment": "...", "sentiment": "Bullish|Bearish|Neutral"}
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
        
        logger.info(f"🤖 Requesting AI comment from OpenAI for {source_key}...")
        
        # Вызываем OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Быстрая и дешевая модель с vision
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""{prompt}

Format your response EXACTLY as:
COMMENT: [your 1-2 sentence analysis]
SENTIMENT: [Bullish|Bearish|Neutral]

Be concise and specific. Focus on actionable insights."""
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
            max_tokens=150,
            temperature=0.7
        )
        
        # Парсим ответ
        content = response.choices[0].message.content.strip()
        logger.info(f"  OpenAI response: {content}")
        
        # Извлекаем comment и sentiment
        comment = None
        sentiment = None
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('COMMENT:'):
                comment = line.replace('COMMENT:', '').strip()
            elif line.startswith('SENTIMENT:'):
                sentiment_raw = line.replace('SENTIMENT:', '').strip()
                # Нормализуем sentiment
                if 'bullish' in sentiment_raw.lower():
                    sentiment = 'Bullish'
                elif 'bearish' in sentiment_raw.lower():
                    sentiment = 'Bearish'
                else:
                    sentiment = 'Neutral'
        
        # Валидация
        if not comment or not sentiment:
            logger.warning(f"Could not parse AI response properly")
            logger.warning(f"  Comment: {comment}")
            logger.warning(f"  Sentiment: {sentiment}")
            return None
        
        logger.info(f"  ✓ AI Comment: {comment}")
        logger.info(f"  ✓ Sentiment: {sentiment}")
        
        return {
            "comment": comment,
            "sentiment": sentiment
        }
        
    except Exception as e:
        logger.error(f"Error getting AI comment: {e}")
        import traceback
        traceback.print_exc()
        return None


def format_sentiment_emoji(sentiment):
    """Возвращает эмодзи для сентимента"""
    if sentiment == 'Bullish':
        return '🟢'
    elif sentiment == 'Bearish':
        return '🔴'
    else:  # Neutral
        return '⚪'


def add_ai_comment_to_caption(caption, ai_result):
    """
    Добавляет AI комментарий к caption
    
    Args:
        caption: Исходный caption
        ai_result: Результат от get_ai_comment()
        
    Returns:
        str: Caption с AI комментарием
    """
    if not ai_result:
        return caption
    
    comment = ai_result['comment']
    sentiment = ai_result['sentiment']
    emoji = format_sentiment_emoji(sentiment)
    
    # Форматируем AI блок
    ai_block = f"\n\n{emoji} <b>{sentiment}</b>\n{comment}"
    
    return caption + ai_block
