"""
Configuration module for Playwright Stealth Email Scraper
Centralized configuration with environment variable support
"""

import os
import random
from dataclasses import dataclass, field
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class ScraperConfig:
    """Main configuration class for the email scraper"""
    
    # === Stealth Settings ===
    enable_stealth: bool = True
    randomize_fingerprint: bool = True
    remove_webdriver_flag: bool = True
    
    # === Browser Settings ===
    headless: bool = True
    slow_mo: int = 0  # Slow down operations by specified milliseconds
    
    # === Viewport Options (will be randomized) ===
    viewports: List[dict] = field(default_factory=lambda: [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
        {"width": 1440, "height": 900},
        {"width": 1280, "height": 720},
        {"width": 1600, "height": 900},
    ])
    
    # === Timing Settings (seconds) ===
    min_page_delay: float = 3.0
    max_page_delay: float = 12.0
    min_action_delay: float = 0.3
    max_action_delay: float = 1.5
    min_typing_delay: int = 50   # milliseconds
    max_typing_delay: int = 150  # milliseconds
    page_load_timeout: int = 60000  # milliseconds
    
    # === Proxy Settings ===
    use_proxy: bool = False
    proxy_server: Optional[str] = None  # Format: http://host:port
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None
    proxy_list_file: Optional[str] = None
    rotate_proxy_per_request: bool = True
    
    # === Retry Settings ===
    max_retries: int = 3
    retry_delay: float = 5.0
    
    # === Output Settings ===
    output_dir: str = "/app/output"
    input_dir: str = "/app/input"
    
    # === Google Search Settings ===
    base_url: str = "https://www.google.com/search"
    max_pages_per_query: int = 10
    
    # === Locales and Timezones (for randomization) ===
    locales: List[str] = field(default_factory=lambda: [
        "en-US", "en-GB", "en-CA", "en-AU"
    ])
    timezones: List[str] = field(default_factory=lambda: [
        "America/New_York", "America/Los_Angeles", "America/Chicago",
        "Europe/London", "America/Denver", "America/Phoenix"
    ])
    
    def get_random_viewport(self) -> dict:
        """Get a random viewport size"""
        return random.choice(self.viewports)
    
    def get_random_locale(self) -> str:
        """Get a random locale"""
        return random.choice(self.locales)
    
    def get_random_timezone(self) -> str:
        """Get a random timezone"""
        return random.choice(self.timezones)
    
    def get_page_delay(self) -> float:
        """Get a random delay between pages"""
        return random.uniform(self.min_page_delay, self.max_page_delay)
    
    def get_action_delay(self) -> float:
        """Get a random delay between actions"""
        return random.uniform(self.min_action_delay, self.max_action_delay)
    
    def get_typing_delay(self) -> int:
        """Get a random typing delay in milliseconds"""
        return random.randint(self.min_typing_delay, self.max_typing_delay)
    
    @classmethod
    def from_env(cls) -> "ScraperConfig":
        """Create configuration from environment variables"""
        config = cls()
        
        # Override with environment variables if present
        if os.getenv("ENABLE_STEALTH"):
            config.enable_stealth = os.getenv("ENABLE_STEALTH", "true").lower() == "true"
        
        if os.getenv("HEADLESS"):
            config.headless = os.getenv("HEADLESS", "true").lower() == "true"
        
        if os.getenv("USE_PROXY"):
            config.use_proxy = os.getenv("USE_PROXY", "false").lower() == "true"
        
        if os.getenv("PROXY_SERVER"):
            config.proxy_server = os.getenv("PROXY_SERVER")
        
        if os.getenv("PROXY_USERNAME"):
            config.proxy_username = os.getenv("PROXY_USERNAME")
        
        if os.getenv("PROXY_PASSWORD"):
            config.proxy_password = os.getenv("PROXY_PASSWORD")
        
        if os.getenv("PROXY_LIST_FILE"):
            config.proxy_list_file = os.getenv("PROXY_LIST_FILE")
        
        if os.getenv("OUTPUT_DIR"):
            config.output_dir = os.getenv("OUTPUT_DIR")
        
        if os.getenv("INPUT_DIR"):
            config.input_dir = os.getenv("INPUT_DIR")
        
        if os.getenv("MAX_PAGES_PER_QUERY"):
            config.max_pages_per_query = int(os.getenv("MAX_PAGES_PER_QUERY", "10"))
        
        if os.getenv("MIN_PAGE_DELAY"):
            config.min_page_delay = float(os.getenv("MIN_PAGE_DELAY", "3.0"))
        
        if os.getenv("MAX_PAGE_DELAY"):
            config.max_page_delay = float(os.getenv("MAX_PAGE_DELAY", "12.0"))
        
        return config


# User-Agent strings that look like real browsers
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    # Chrome on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Chrome on Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    # Firefox on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]


def get_random_user_agent() -> str:
    """Get a random user agent string"""
    return random.choice(USER_AGENTS)


# Default configuration instance
default_config = ScraperConfig.from_env()
