"""
МОДИФИКАЦИИ ДЛЯ screenshot_parser.py
======================================

Добавить эти функции и модификации для улучшения загрузки heatmap с текстом.

ИНСТРУКЦИЯ:
1. Найти функцию capture_screenshot() в screenshot_parser.py
2. Добавить код ниже ПЕРЕД строкой screenshot = await element.screenshot()
3. Код проверяет source_key и применяет специальные действия для heatmap
"""

# ============================================================================
# ДОБАВИТЬ ПЕРЕД screenshot = await element.screenshot()
# ============================================================================

async def apply_heatmap_interactions(page, source_key, source_config):
    """
    Применяет специальные действия для загрузки heatmap с текстом.
    
    Разные варианты heatmap используют разные техники:
    - v1-v3: Scroll + Hover на SVG
    - v4: TradingView может требовать клик
    - v5: CoinGlass специальная логика
    - v6: Stealth mode
    - v7: Network idle wait
    - v8: Finviz scroll
    """
    
    # v1, v2, v3 - CMC variants: Scroll + Hover
    if source_key in ['heatmap_v1_fullpage', 'heatmap_v2_small', 'heatmap_v3_longwait']:
        logger.info(f"[{source_key}] Applying scroll + hover interactions")
        
        # Прокрутить страницу вниз и вверх для триггера загрузки
        await page.evaluate("window.scrollTo(0, 500)")
        await asyncio.sleep(1)
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)
        
        # Навести мышь на SVG элемент
        try:
            svg_element = await page.query_selector('svg#d3svg')
            if svg_element:
                box = await svg_element.bounding_box()
                if box:
                    # Навести мышь в центр SVG
                    center_x = box['x'] + box['width'] / 2
                    center_y = box['y'] + box['height'] / 2
                    await page.mouse.move(center_x, center_y)
                    await asyncio.sleep(1)
                    
                    # Небольшое движение мыши для триггера hover эффектов
                    await page.mouse.move(center_x + 10, center_y + 10)
                    await asyncio.sleep(1)
        except Exception as e:
            logger.warning(f"[{source_key}] Hover failed: {e}")
        
        # Дополнительное ожидание
        await asyncio.sleep(3)
    
    # v4 - TradingView: Клик для активации
    elif source_key == 'heatmap_v4_tradingview':
        logger.info(f"[{source_key}] Applying TradingView interactions")
        
        # TradingView может требовать клик для загрузки
        try:
            await page.evaluate("window.scrollTo(0, 300)")
            await asyncio.sleep(2)
            
            # Клик в центр страницы
            await page.mouse.click(960, 540)
            await asyncio.sleep(2)
        except Exception as e:
            logger.warning(f"[{source_key}] Click failed: {e}")
    
    # v5 - CoinGlass: Scroll + Wait
    elif source_key == 'heatmap_v5_coinglass':
        logger.info(f"[{source_key}] Applying CoinGlass interactions")
        
        await page.evaluate("window.scrollTo(0, 400)")
        await asyncio.sleep(2)
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(3)
    
    # v6 - Stealth Mode: Дополнительная маскировка
    elif source_key == 'heatmap_v6_stealth':
        logger.info(f"[{source_key}] Applying stealth mode")
        
        # Эмуляция человеческого поведения
        await page.evaluate("window.scrollTo(0, 200)")
        await asyncio.sleep(0.5)
        await page.evaluate("window.scrollTo(0, 400)")
        await asyncio.sleep(0.5)
        await page.evaluate("window.scrollTo(0, 600)")
        await asyncio.sleep(0.5)
        await page.evaluate("window.scrollTo(0, 300)")
        await asyncio.sleep(2)
        
        # Hover на элементе
        await page.mouse.move(500, 500)
        await asyncio.sleep(1)
        await page.mouse.move(700, 500)
        await asyncio.sleep(2)
    
    # v7 - Network Idle: уже обработано через wait_for
    elif source_key == 'heatmap_v7_networkidle':
        logger.info(f"[{source_key}] Network idle wait applied")
        # Дополнительная пауза после network idle
        await asyncio.sleep(5)
    
    # v8 - Finviz: Simple scroll
    elif source_key == 'heatmap_v8_finviz':
        logger.info(f"[{source_key}] Applying Finviz scroll")
        await page.evaluate("window.scrollTo(0, 300)")
        await asyncio.sleep(2)


async def setup_stealth_mode(page):
    """
    Настройка stealth mode для обхода детектирования бота.
    """
    # Переопределить navigator.webdriver
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)
    
    # Добавить реалистичные заголовки
    await page.set_extra_http_headers({
        'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document'
    })
    
    # Переопределить chrome runtime
    await page.add_init_script("""
        window.chrome = {
            runtime: {}
        };
    """)
    
    # Переопределить permissions
    await page.add_init_script("""
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
    """)


# ============================================================================
# МОДИФИКАЦИЯ capture_screenshot() ФУНКЦИИ
# ============================================================================

"""
В функции capture_screenshot() найти этот блок:

    # Wait for element to load
    if "wait_for" in source_config:
        wait_selector = source_config["wait_for"]
        logger.info(f"Waiting for selector: {wait_selector}")
        await page.wait_for_selector(wait_for_selector, timeout=30000)
    
    # Extra wait if specified
    if "extra_wait" in source_config:
        extra_wait = source_config["extra_wait"]
        logger.info(f"Extra wait: {extra_wait} seconds")
        await asyncio.sleep(extra_wait)

И ДОБАВИТЬ ПОСЛЕ НЕГО:

    # Apply heatmap-specific interactions
    if source_key.startswith('heatmap_'):
        await apply_heatmap_interactions(page, source_key, source_config)
    
    # Apply stealth mode if configured
    if source_config.get('use_stealth', False):
        await setup_stealth_mode(page)

"""

# ============================================================================
# АЛЬТЕРНАТИВА: МОДИФИКАЦИЯ wait_for ДЛЯ NETWORK IDLE
# ============================================================================

"""
Для heatmap_v7_networkidle изменить логику wait_for:

В функции capture_screenshot() найти:
    
    if "wait_for" in source_config:
        wait_selector = source_config["wait_for"]
        logger.info(f"Waiting for selector: {wait_selector}")
        await page.wait_for_selector(wait_selector, timeout=30000)

И ЗАМЕНИТЬ НА:

    if "wait_for" in source_config:
        wait_selector = source_config["wait_for"]
        
        # Special handling for network idle
        if wait_selector == "networkidle":
            logger.info(f"Waiting for network idle")
            await page.wait_for_load_state('networkidle', timeout=30000)
        else:
            logger.info(f"Waiting for selector: {wait_selector}")
            await page.wait_for_selector(wait_selector, timeout=30000)
"""

# ============================================================================
# ПОЛНЫЙ ПРИМЕР МОДИФИЦИРОВАННОЙ capture_screenshot()
# ============================================================================

"""
async def capture_screenshot(source_key, source_config):
    # ... existing code ...
    
    # Navigate to URL
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    logger.info(f"Page loaded: {url}")
    
    # Hide elements
    if "hide_elements" in source_config:
        # ... existing hide code ...
    
    # Wait for element to load
    if "wait_for" in source_config:
        wait_selector = source_config["wait_for"]
        
        # Special handling for network idle
        if wait_selector == "networkidle":
            logger.info(f"Waiting for network idle")
            await page.wait_for_load_state('networkidle', timeout=30000)
        else:
            logger.info(f"Waiting for selector: {wait_selector}")
            await page.wait_for_selector(wait_selector, timeout=30000)
    
    # Extra wait if specified
    if "extra_wait" in source_config:
        extra_wait = source_config["extra_wait"]
        logger.info(f"Extra wait: {extra_wait} seconds")
        await asyncio.sleep(extra_wait)
    
    # ✅ ДОБАВИТЬ ЭТИ СТРОКИ ✅
    # Apply heatmap-specific interactions
    if source_key.startswith('heatmap_'):
        await apply_heatmap_interactions(page, source_key, source_config)
    
    # Apply stealth mode if configured
    if source_config.get('use_stealth', False):
        await setup_stealth_mode(page)
    # ✅ КОНЕЦ ДОБАВЛЕНИЯ ✅
    
    # Find element to screenshot
    element = await page.query_selector(selector)
    if not element:
        raise ValueError(f"Element not found: {selector}")
    
    # Take screenshot
    screenshot = await element.screenshot()
    
    # ... rest of code ...
"""

# ============================================================================
# IMPORTS NEEDED
# ============================================================================

"""
В начале screenshot_parser.py убедиться что есть:

import asyncio
from playwright.async_api import async_playwright
"""

print("""
✅ ИНСТРУКЦИЯ ПО МОДИФИКАЦИИ screenshot_parser.py

1. Скопируй функции apply_heatmap_interactions() и setup_stealth_mode() 
   в screenshot_parser.py (после imports, перед capture_screenshot)

2. В capture_screenshot() добавь после extra_wait:
   
   # Apply heatmap-specific interactions
   if source_key.startswith('heatmap_'):
       await apply_heatmap_interactions(page, source_key, source_config)
   
   # Apply stealth mode if configured
   if source_config.get('use_stealth', False):
       await setup_stealth_mode(page)

3. Измени обработку wait_for для поддержки 'networkidle'

4. Готово! Теперь каждый heatmap вариант будет использовать свои трюки

📋 ВАРИАНТЫ:
- v1-v3: Scroll + Hover на SVG
- v4: TradingView клик
- v5: CoinGlass scroll
- v6: Stealth mode
- v7: Network idle
- v8: Finviz scroll
""")
