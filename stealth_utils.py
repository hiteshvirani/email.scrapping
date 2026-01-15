"""
Stealth utilities for Playwright to avoid bot detection
Applies various anti-detection techniques
"""

import random
from typing import Optional, Dict, Any
from playwright.async_api import Page, BrowserContext

# Try to import playwright_stealth, provide fallback if not available
try:
    from playwright_stealth import stealth_async
    HAS_PLAYWRIGHT_STEALTH = True
except ImportError:
    HAS_PLAYWRIGHT_STEALTH = False
    stealth_async = None


class StealthConfig:
    """Configuration for stealth features"""
    
    def __init__(
        self,
        # Core stealth options
        webdriver: bool = True,
        webgl_vendor: bool = True,
        chrome_app: bool = True,
        chrome_csi: bool = True,
        chrome_load_times: bool = True,
        chrome_runtime: bool = True,
        iframe_content_window: bool = True,
        media_codecs: bool = True,
        navigator_hardware_concurrency: int = 4,
        navigator_languages: bool = True,
        navigator_permissions: bool = True,
        navigator_platform: bool = True,
        navigator_plugins: bool = True,
        navigator_user_agent: bool = True,
        navigator_vendor: bool = True,
        outerdimensions: bool = True,
        hairline: bool = True,
        # Additional options
        run_on_insecure_origins: bool = False,
    ):
        self.webdriver = webdriver
        self.webgl_vendor = webgl_vendor
        self.chrome_app = chrome_app
        self.chrome_csi = chrome_csi
        self.chrome_load_times = chrome_load_times
        self.chrome_runtime = chrome_runtime
        self.iframe_content_window = iframe_content_window
        self.media_codecs = media_codecs
        self.navigator_hardware_concurrency = navigator_hardware_concurrency
        self.navigator_languages = navigator_languages
        self.navigator_permissions = navigator_permissions
        self.navigator_platform = navigator_platform
        self.navigator_plugins = navigator_plugins
        self.navigator_user_agent = navigator_user_agent
        self.navigator_vendor = navigator_vendor
        self.outerdimensions = outerdimensions
        self.hairline = hairline
        self.run_on_insecure_origins = run_on_insecure_origins


async def apply_stealth(page: Page, config: Optional[StealthConfig] = None) -> None:
    """
    Apply stealth modifications to a Playwright page
    Uses playwright_stealth if available, otherwise applies manual patches
    """
    if HAS_PLAYWRIGHT_STEALTH:
        await stealth_async(page)
    else:
        # Apply manual stealth patches
        await apply_manual_stealth(page, config or StealthConfig())


async def apply_manual_stealth(page: Page, config: StealthConfig) -> None:
    """
    Apply manual stealth patches when playwright_stealth is not available
    """
    # Collection of stealth scripts to inject
    stealth_scripts = []
    
    # 1. Remove webdriver flag - CRITICAL
    if config.webdriver:
        stealth_scripts.append("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
    
    # 2. Fix chrome.runtime
    if config.chrome_runtime:
        stealth_scripts.append("""
            window.chrome = {
                runtime: {},
            };
        """)
    
    # 3. Fix navigator.languages
    if config.navigator_languages:
        stealth_scripts.append("""
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        """)
    
    # 4. Fix navigator.plugins (make it look like real Chrome)
    if config.navigator_plugins:
        stealth_scripts.append("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    const plugins = [
                        {
                            0: {type: 'application/x-google-chrome-pdf'},
                            description: 'Portable Document Format',
                            filename: 'internal-pdf-viewer',
                            length: 1,
                            name: 'Chrome PDF Plugin'
                        },
                        {
                            0: {type: 'application/pdf'},
                            description: '',
                            filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                            length: 1,
                            name: 'Chrome PDF Viewer'
                        },
                        {
                            0: {type: 'application/x-nacl'},
                            1: {type: 'application/x-pnacl'},
                            description: '',
                            filename: 'internal-nacl-plugin',
                            length: 2,
                            name: 'Native Client'
                        }
                    ];
                    plugins.item = (index) => plugins[index];
                    plugins.namedItem = (name) => plugins.find(p => p.name === name);
                    plugins.refresh = () => {};
                    return plugins;
                },
            });
        """)
    
    # 5. Fix navigator.permissions
    if config.navigator_permissions:
        stealth_scripts.append("""
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
    
    # 6. Fix WebGL vendor and renderer (hide headless indicators)
    if config.webgl_vendor:
        stealth_scripts.append("""
            const getParameterPrototype = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameterPrototype.call(this, parameter);
            };
        """)
    
    # 7. Fix hardware concurrency
    stealth_scripts.append(f"""
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {config.navigator_hardware_concurrency},
        }});
    """)
    
    # 8. Fix platform
    if config.navigator_platform:
        stealth_scripts.append("""
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32',
            });
        """)
    
    # 9. Fix vendor
    if config.navigator_vendor:
        stealth_scripts.append("""
            Object.defineProperty(navigator, 'vendor', {
                get: () => 'Google Inc.',
            });
        """)
    
    # 10. Fix iframe contentWindow
    if config.iframe_content_window:
        stealth_scripts.append("""
            Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
                get: function() {
                    return window;
                }
            });
        """)
    
    # 11. Mask automation-related properties
    stealth_scripts.append("""
        // Remove automation-related properties
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        delete window.__webdriver_evaluate;
        delete window.__selenium_evaluate;
        delete window.__webdriver_script_function;
        delete window.__webdriver_script_func;
        delete window.__webdriver_script_fn;
        delete window.__fxdriver_evaluate;
        delete window.__driver_unwrapped;
        delete window.__webdriver_unwrapped;
        delete window.__driver_evaluate;
        delete window.__selenium_unwrapped;
        delete window.__fxdriver_unwrapped;
        
        // Fix toString methods
        const originalFunction = Function.prototype.toString;
        Function.prototype.toString = function() {
            if (this === navigator.permissions.query) {
                return 'function query() { [native code] }';
            }
            return originalFunction.call(this);
        };
    """)
    
    # Combine and inject all scripts
    combined_script = "\n".join(stealth_scripts)
    
    await page.add_init_script(combined_script)


async def setup_stealth_context(
    browser,
    user_agent: Optional[str] = None,
    viewport: Optional[Dict] = None,
    locale: str = "en-US",
    timezone_id: str = "America/New_York",
    geolocation: Optional[Dict] = None,
    permissions: Optional[list] = None,
    color_scheme: str = "light",
    extra_http_headers: Optional[Dict] = None,
    proxy: Optional[Dict] = None,
) -> BrowserContext:
    """
    Create a browser context with stealth settings
    """
    context_options = {
        "locale": locale,
        "timezone_id": timezone_id,
        "color_scheme": color_scheme,
        "device_scale_factor": random.choice([1, 1.25, 1.5, 2]),
        "has_touch": False,
        "is_mobile": False,
        "java_script_enabled": True,
    }
    
    if user_agent:
        context_options["user_agent"] = user_agent
    
    if viewport:
        context_options["viewport"] = viewport
    
    if geolocation:
        context_options["geolocation"] = geolocation
    
    if permissions:
        context_options["permissions"] = permissions
    
    if extra_http_headers:
        context_options["extra_http_headers"] = extra_http_headers
    
    if proxy:
        context_options["proxy"] = proxy
    
    context = await browser.new_context(**context_options)
    
    return context


def get_stealth_headers(user_agent: str) -> Dict[str, str]:
    """
    Get headers that help avoid detection
    """
    return {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": user_agent,
    }
