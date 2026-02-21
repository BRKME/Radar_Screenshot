"""
Конфигурация источников для скриншотов
Version: 1.4.0 - Short hashtags (max 2, max 10 chars)
"""

# Конфигурация источников для скриншотов
# v1.4.0: Короткие хэштеги (max 2, max 10 символов)
SCREENSHOT_SOURCES = {
    "fear_greed": {
        "name": "Crypto Fear & Greed Index",
        "url": "https://coinmarketcap.com/charts/fear-and-greed-index/",
        "selector": "div[data-role='progressbar-wrapper']",  # ✅ ОБНОВЛЕН: Стабильный data-атрибут
        "wait_for": "svg",  # ✅ ОБНОВЛЕН: Ждем SVG внутри
        "telegram_title": "📊 Fear & Greed Index",
        "telegram_hashtags": "#Bitcoin #Sentiment",
        "enabled": True,
        "priority": 1,
        "skip_width_padding": True,
        "element_padding": {"top": 60, "right": 50, "bottom": 60, "left": 50},  # ✅ УВЕЛИЧЕН padding
        "scale": 1.0,
        "hide_elements": "nav, footer, [class*='banner'], [class*='ad']",  # ✅ УПРОЩЕН
        "crop": {"top": 0, "right": 0, "bottom": 0, "left": 0}  # ✅ БЕЗ crop (padding достаточно)
    },
    
    "altcoin_season": {
        "name": "Altcoin Season Index",
        "url": "https://coinmarketcap.com/charts/altcoin-season-index/",
        "selector": "[data-role='main-wrapper']",
        "wait_for": "[data-role='main-wrapper']",
        "telegram_title": "🌈 Altcoin Season Index",
        "telegram_hashtags": "#Altcoins #Bitcoin",
        "enabled": True,
        "priority": 2,
        "viewport_width": 1280,
        "viewport_height": 800,
        "hide_elements": "aside, nav, header, footer, [class*='sidebar'], [class*='banner'], [class*='ad'], iframe, .description, h1:not(:first-of-type), table, svg[class*='chart']",
        "crop": {"top": 100, "right": 400, "bottom": 400, "left": 400}
    },
    
    "btc_dominance": {
        "name": "Bitcoin Dominance",
        "url": "https://coinmarketcap.com/charts/bitcoin-dominance/",
        "selector": "xpath=//h2[contains(text(), 'Bitcoin Dominance')]/parent::div",  # ✅ ОБНОВЛЕН: Стабильный XPath
        "wait_for": "h2:has-text('Bitcoin Dominance')",  # ✅ ОБНОВЛЕН: Ждем заголовок
        "telegram_title": "₿ Bitcoin Dominance",
        "telegram_hashtags": "#Bitcoin #Dominance",
        "enabled": True,
        "priority": 3,
        "viewport_width": 1280,
        "viewport_height": 800,
        "hide_elements": "aside, nav, header, footer, [class*='sidebar'], [class*='banner'], [class*='ad'], iframe",
        "element_padding": {"top": 40, "right": 40, "bottom": 40, "left": 40},  # ✅ ДОБАВЛЕН padding
        "crop": {"top": 0, "right": 0, "bottom": 0, "left": 0},  # ✅ БЕЗ crop
        "skip_width_padding": True
    },
    
    "eth_etf": {
        "name": "Ethereum ETF Tracker",
        "url": "https://coinmarketcap.com/etf/ethereum/",
        "selector": "[data-role='content-wrapper']",
        "wait_for": "[data-role='content-wrapper']",
        "telegram_title": "💎 Ethereum ETF Tracker",
        "telegram_hashtags": "#Ethereum #ETF",
        "enabled": True,
        "priority": 4,
        "skip_width_padding": True,
        "element_padding": {"top": 60, "right": 40, "bottom": 60, "left": 40},
        "scale": 1.0,
        "crop": {"top": 50, "right": 30, "bottom": 220, "left": 0},
        "extra_wait": 10
    },
    
    "btc_etf": {
        "name": "Bitcoin ETF Tracker",
        "url": "https://coinmarketcap.com/etf/bitcoin/",
        "selector": "[data-role='content-wrapper']",
        "wait_for": "[data-role='content-wrapper']",
        "telegram_title": "₿ Bitcoin ETF Tracker",
        "telegram_hashtags": "#Bitcoin #ETF",
        "enabled": True,
        "priority": 5,
        "skip_width_padding": True,
        "element_padding": {"top": 60, "right": 40, "bottom": 60, "left": 40},
        "scale": 1.0,
        "crop": {"top": 50, "right": 30, "bottom": 220, "left": 0},
        "extra_wait": 10
    },
    
    "derivatives": {
        "name": "Crypto Derivatives",
        "url": "https://coinmarketcap.com/charts/perpetual-markets/",
        "selector": None,
        "wait_for": "table",
        "telegram_title": "📈 Crypto Derivatives Market",
        "telegram_hashtags": "#Crypto #Trading",
        "enabled": False,  # ❌ Отключен: CMC anti-bot защита
        "priority": 6
    },
    
    "top_gainers": {
        "name": "Top Gainers",
        "url": "https://dropstab.com/",
        "selector": "#__next > div.z-app.relative > div > div.lg\\:ml-auto.w-full.flex.flex-col.lg\\:w-\\[calc\\(100\\%-72px\\)\\].xl\\:w-\\[calc\\(100\\%-256px\\)\\] > main > div > div.relative.z-0.w-full.styles_carousel__lIy83.mb-4.lg\\:mb-6 > div > div > div:nth-child(1) > div > section > span",
        "wait_for": "section",
        "telegram_title": "🚀 Top Gainers Today",
        "telegram_hashtags": "#Crypto #Gainers",
        "enabled": True,
        "priority": 7,
        "skip_width_padding": True,  # ✅ НЕ добавлять белый padding по бокам
        "element_padding": {"top": 40, "right": 30, "bottom": 40, "left": 30},  # Небольшие отступы
        "scale": 1.0,  # ✅ Уменьшаем scale до 1.0 (было 1.2)
        "crop": {"top": 20, "right": 20, "bottom": 20, "left": 20}  # ✅ Обрезка со всех сторон
    },
    
    "crypto_liquidations": {
        "name": "Crypto Liquidations",
        "url": "https://coinmarketcap.com/charts/liquidations/",
        "selector": "div[data-role='ic-content']",  # ✅ Стабильный data-атрибут
        "wait_for": "div[data-role='ic-content']",
        "telegram_title": "💥 Crypto Liquidations",
        "telegram_hashtags": "#Bitcoin #Trading",
        "enabled": True,
        "priority": 8,
        "skip_width_padding": True,
        "element_padding": {"top": 50, "right": 40, "bottom": 50, "left": 40},
        "scale": 1.0,
        "hide_elements": "nav, footer, [class*='banner'], [class*='ad']",
        "crop": {"top": 0, "right": 0, "bottom": 0, "left": 0}
    },
    
    "token_unlocks": {
        "name": "Token Unlocks Next 7 Days",
        "url": "https://dropstab.com/vesting",
        "selector": "body",
        "wait_for": "table tbody tr",
        "telegram_title": "🔓 Token Unlocks Next 7 Days",
        "telegram_hashtags": "#Crypto #Vesting",
        "enabled": False,
        "priority": 8,
        "extra_wait": 20,
        "viewport_width": 1920,
        "viewport_height": 1080,
        "hide_elements": "aside, nav, header, footer, [class*='sidebar'], [class*='Sidebar'], [class*='menu'], [class*='Menu'], [class*='nav'], [class*='Nav'], table tbody tr:nth-child(n+7), [class*='banner'], [class*='Banner'], [class*='ad'], [class*='Ad'], [class*='advertisement'], iframe, [id*='ad'], .description, h1, h2, p, button, [role='banner'], [role='navigation'], [class*='cookie']",
        "crop": {"top": 150, "right": 300, "bottom": 400, "left": 300},
        "skip_ai": True
    },
    
    # ========================================================================
    # HEATMAP SOURCES - BLOCKCHAIN.COM (ПОБЕДИТЕЛЬ!)
    # ========================================================================
    
    # HEATMAP: Blockchain.com (Canvas-based) - ЕДИНСТВЕННЫЙ АКТИВНЫЙ
    "heatmap_blockchain": {
        "name": "Crypto Market Heatmap",
        "url": "https://www.blockchain.com/explorer/prices/heatmap",
        "selector": "canvas#heatmapCanvas",
        "wait_for": "canvas#heatmapCanvas",
        "telegram_title": "🗺️ Crypto Market Heatmap",
        "telegram_hashtags": "#Crypto #Heatmap",
        "enabled": True,
        "priority": 8,
        "extra_wait": 10,
        "viewport_width": 1920,
        "viewport_height": 1080,
        "element_padding": {"top": 50, "right": 50, "bottom": 50, "left": 50},
        "hide_elements": "header, nav, footer, aside, [class*='navbar'], [class*='Navigation'], [class*='sidebar'], [class*='banner'], [class*='ad'], [class*='cookie']",
        "crop": {"top": 0, "right": 0, "bottom": 0, "left": 0},
        "skip_width_padding": True
    },
    
    # ОТКЛЮЧЕННЫЕ (для истории)
    "heatmap_v1_coin360": {
        "name": "Crypto Market Heatmap - Coin360",
        "url": "https://coin360.com/",
        "enabled": False,  # ❌ ОТКЛЮЧЕН
        "priority": 8
    },
    
    "heatmap_v3_ndax": {
        "name": "Crypto Market Heatmap - NDAX",
        "url": "https://ndax.io/en/markets/heatmap",
        "enabled": False,  # ❌ ОТКЛЮЧЕН
        "priority": 8
    }
}

# ===============================================================================
# РАСПИСАНИЕ - ГИБКАЯ ЛОГИКА ПО ВРЕМЕНИ MSK
# ===============================================================================

POST_SCHEDULE = {
    # HEATMAP - 2 РАЗА В ДЕНЬ (BLOCKCHAIN.COM)
    # ⚠️ FIX: GitHub Actions cron неточный (может запускаться ±10 минут)
    # Добавлен буфер 10 минут перед каждым слотом
    "morning_heatmap": {
        "time_range_msk": (6.85, 8.0),  # 06:51-08:00 (07:00 MSK утром)
        "sources": ["heatmap_blockchain"],
        "selection": "fixed"
    },
    "evening_heatmap": {
        "time_range_msk": (18.85, 19.85),  # 18:51-19:51 (19:00 MSK) ✅ FIX: было 20.00, убрано пересечение
        "sources": ["heatmap_blockchain"],
        "selection": "fixed"
    },
    
    # REGULAR SCHEDULE
    "daily_market_sentiment": {
        "time_range_msk": (16.35, 17.0),  # 16:21-17:00 (16:30 MSK)
        "sources": ["fear_greed", "altcoin_season", "btc_dominance"],
        "selection": "random"
    },
    "crypto_liquidations_daily": {
        "time_range_msk": (17.85, 18.85),  # 17:51-18:51 (18:00 MSK) ✅ FIX: было 19.00, убрано пересечение
        "sources": ["crypto_liquidations"],
        "selection": "fixed"
    },
    "btc_etf_flows": {
        "time_range_msk": (19.85, 20.35),  # 19:51-20:21 ✅ FIX: убрано пересечение с ETH ETF
        "sources": ["btc_etf"],
        "selection": "fixed"
    },
    "eth_etf_flows": {
        "time_range_msk": (20.35, 21.0),  # 20:21-21:00 (20:30 MSK)
        "sources": ["eth_etf"],
        "selection": "fixed"
    },
    "top_gainers_radar": {
        "time_range_msk": (21.85, 22.5),  # 21:51-22:30 (22:00 MSK)
        "sources": ["top_gainers"],
        "selection": "fixed"
    }
}

# Настройки для обработки изображений
IMAGE_SETTINGS = {
    "telegram_max_width": 1200,
    "telegram_min_width": 1000,
    "telegram_max_height": 1280,
    "quality": 85,
    "format": "JPEG",
    "crop_padding": 20,
    "add_padding_if_narrow": True,
    "padding_color": (255, 255, 255)
}

# Настройки скриншотов
SCREENSHOT_SETTINGS = {
    "viewport_width": 1920,
    "viewport_height": 1080,
    "full_page": False,
    "wait_timeout": 30000,
    "wait_after_load": 5
}
