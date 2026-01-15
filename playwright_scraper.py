"""
Playwright Stealth Email Scraper
Main scraping module using Playwright with stealth capabilities
"""

import asyncio
import re
import os
import random
import time
import logging
from typing import List, Optional, Set
from urllib.parse import quote_plus
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

from config import ScraperConfig, get_random_user_agent, default_config
from human_behavior import HumanBehavior
from proxy_manager import ProxyManager, Proxy
from stealth_utils import apply_stealth, setup_stealth_context, get_stealth_headers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper.log')
    ]
)
logger = logging.getLogger(__name__)


class PlaywrightEmailScraper:
    """
    Async email scraper using Playwright with stealth capabilities
    Designed to avoid CAPTCHA and bot detection
    """
    
    # Email regex pattern
    EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    
    # Cookie consent button selectors (try multiple)
    COOKIE_SELECTORS = [
        '#W0wltc',  # Google "I agree" button
        'button[id="L2AGLb"]',  # Another Google consent button
        '[aria-label="Accept all"]',
        'button:has-text("Accept all")',
        'button:has-text("Accept")',
        'button:has-text("I agree")',
    ]
    
    # Next page button selectors
    NEXT_PAGE_SELECTORS = [
        '#pnnext',
        'a[id="pnnext"]',
        '[aria-label="Next page"]',
        'a:has-text("Next")',
    ]
    
    def __init__(
        self,
        config: Optional[ScraperConfig] = None,
        proxy_manager: Optional[ProxyManager] = None
    ):
        """
        Initialize the scraper
        
        Args:
            config: Scraper configuration
            proxy_manager: Optional proxy manager for rotation
        """
        self.config = config or default_config
        self.proxy_manager = proxy_manager
        self.human = HumanBehavior(self.config)
        
        # State
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.current_proxy: Optional[Proxy] = None
        
        # Metrics
        self.pages_scraped = 0
        self.emails_found = 0
        self.captcha_count = 0
    
    async def start(self) -> None:
        """Start the browser and create context"""
        logger.info("Starting Playwright scraper...")
        self.playwright = await async_playwright().start()
        
        # Get proxy if available
        proxy_config = None
        if self.proxy_manager and self.config.use_proxy:
            self.current_proxy = self.proxy_manager.get_next_proxy()
            if self.current_proxy:
                proxy_config = self.current_proxy.to_playwright_config()
                logger.info(f"Using proxy: {self.current_proxy.server}")
        
        # Launch browser
        launch_options = {
            "headless": self.config.headless,
            "slow_mo": self.config.slow_mo,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-site-isolation-trials",
                "--disable-web-security",
                "--disable-features=TranslateUI",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-background-networking",
                "--disable-sync",
                "--disable-translate",
                "--metrics-recording-only",
                "--disable-default-apps",
                "--mute-audio",
                "--no-pings",
                "--disable-plugins-discovery",
            ],
        }
        
        if proxy_config:
            launch_options["proxy"] = proxy_config
        
        self.browser = await self.playwright.chromium.launch(**launch_options)
        
        # Create stealth context
        viewport = self.config.get_random_viewport()
        user_agent = get_random_user_agent()
        
        self.context = await setup_stealth_context(
            self.browser,
            user_agent=user_agent,
            viewport=viewport,
            locale=self.config.get_random_locale(),
            timezone_id=self.config.get_random_timezone(),
            extra_http_headers=get_stealth_headers(user_agent),
            proxy=proxy_config,
        )
        
        # Create page and apply stealth
        self.page = await self.context.new_page()
        
        # Apply stealth modifications
        if self.config.enable_stealth:
            await apply_stealth(self.page)
        
        logger.info(f"Browser started with viewport: {viewport['width']}x{viewport['height']}, locale: {self.config.get_random_locale()}")
    
    async def stop(self) -> None:
        """Stop the browser"""
        logger.info("Stopping scraper...")
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def _handle_cookie_consent(self) -> None:
        """Handle cookie consent dialogs"""
        for selector in self.COOKIE_SELECTORS:
            try:
                button = await self.page.query_selector(selector)
                if button:
                    await self.human.action_delay()
                    await button.click()
                    logger.info("Accepted cookie consent")
                    await self.human.action_delay()
                    return
            except Exception:
                continue
    
    async def _check_for_captcha(self) -> bool:
        """Check if CAPTCHA is present on the page"""
        captcha_indicators = [
            "recaptcha",
            "captcha",
            "unusual traffic",
            "are you a robot",
            "verify you're human",
            "security check",
        ]
        
        try:
            content = await self.page.content()
            content_lower = content.lower()
            
            for indicator in captcha_indicators:
                if indicator in content_lower:
                    self.captcha_count += 1
                    logger.warning(f"⚠️  CAPTCHA detected! ({indicator})")
                    return True
        except Exception:
            pass
        
        return False
    
    async def _extract_emails_from_page(self) -> Set[str]:
        """Extract emails from current page content"""
        emails = set()
        
        try:
            # Get page content
            content = await self.page.content()
            soup = BeautifulSoup(content, "lxml")
            
            # Extract text and find emails
            text = soup.get_text()
            found_emails = self.EMAIL_REGEX.findall(text)
            
            # Filter and clean emails
            for email in found_emails:
                email = email.lower().strip()
                # Basic validation
                if len(email) > 5 and "." in email:
                    emails.add(email)
        except Exception as e:
            logger.error(f"Error extracting emails: {e}")
        
        return emails
    
    async def _click_next_page(self) -> bool:
        """Click the next page button if available"""
        for selector in self.NEXT_PAGE_SELECTORS:
            try:
                button = await self.page.query_selector(selector)
                if button:
                    is_visible = await button.is_visible()
                    if is_visible:
                        await self.human.scroll_to_element(self.page, button)
                        await self.human.action_delay()
                        await self.human.human_like_click(self.page, button)
                        return True
            except Exception:
                continue
        
        return False
    
    async def scrape_query(
        self,
        query: str,
        max_pages: Optional[int] = None
    ) -> List[str]:
        """
        Scrape emails for a given search query
        
        Args:
            query: Search query string
            max_pages: Maximum pages to scrape (overrides config)
        
        Returns:
            List of found emails
        """
        if not self.page:
            await self.start()
        
        max_pages = max_pages or self.config.max_pages_per_query
        all_emails = set()
        page_num = 1
        
        # Build search URL
        encoded_query = quote_plus(query)
        search_url = f"{self.config.base_url}?q={encoded_query}"
        
        logger.info(f"🔍 Searching: {query}")
        
        try:
            # Navigate to search page
            await self.page.goto(search_url, timeout=self.config.page_load_timeout)
            await self.human.page_delay()
            
            # Handle cookie consent on first page
            await self._handle_cookie_consent()
            
            # Check for CAPTCHA
            if await self._check_for_captcha():
                logger.warning("❌ CAPTCHA encountered, stopping this query")
                if self.current_proxy and self.proxy_manager:
                    self.proxy_manager.mark_failure(self.current_proxy)
                return list(all_emails)
            
            # Random page interaction to appear more human
            await self.human.random_page_interaction(self.page)
            
            # Scrape pages
            while page_num <= max_pages:
                logger.info(f"  📄 Processing Page {page_num}...")
                
                # Extract emails from current page
                page_emails = await self._extract_emails_from_page()
                new_emails = page_emails - all_emails
                all_emails.update(page_emails)
                
                logger.info(f"  Found {len(new_emails)} new emails (total: {len(all_emails)})")
                self.pages_scraped += 1
                
                # Check for CAPTCHA
                if await self._check_for_captcha():
                    logger.warning("❌ CAPTCHA encountered, stopping")
                    break
                
                # Try to go to next page
                if page_num < max_pages:
                    await self.human.page_delay()
                    
                    # Some random interaction before clicking next
                    if random.random() < 0.3:
                        await self.human.random_page_interaction(self.page)
                    
                    if not await self._click_next_page():
                        logger.info("  ℹ️  No more pages available")
                        break
                    
                    # Wait for next page to load
                    await self.page.wait_for_load_state("domcontentloaded")
                    await self.human.page_delay()
                
                page_num += 1
            
            # Mark proxy as successful
            if self.current_proxy and self.proxy_manager:
                self.proxy_manager.mark_success(self.current_proxy)
        
        except Exception as e:
            logger.error(f"❌ Error scraping query: {e}")
            if self.current_proxy and self.proxy_manager:
                self.proxy_manager.mark_failure(self.current_proxy)
        
        self.emails_found += len(all_emails)
        return list(all_emails)
    
    async def rotate_proxy(self) -> bool:
        """Rotate to a new proxy (requires restart)"""
        if not self.proxy_manager:
            return False
        
        logger.info("🔄 Rotating proxy...")
        
        # Stop current browser
        await self.stop()
        
        # Start with new proxy
        await self.start()
        
        return self.current_proxy is not None
    
    def get_stats(self) -> dict:
        """Get scraping statistics"""
        return {
            "pages_scraped": self.pages_scraped,
            "emails_found": self.emails_found,
            "captcha_count": self.captcha_count,
            "current_proxy": str(self.current_proxy) if self.current_proxy else None,
        }


async def scrape_from_csv(
    csv_path: str,
    output_dir: str,
    config: Optional[ScraperConfig] = None,
    proxy_manager: Optional[ProxyManager] = None
) -> None:
    """
    Scrape emails for queries from a CSV file
    
    Args:
        csv_path: Path to CSV file with queries
        output_dir: Directory to save output files
        config: Scraper configuration
        proxy_manager: Optional proxy manager
    """
    # Read CSV
    try:
        df = pd.read_csv(csv_path, header=None)
    except Exception as e:
        logger.error(f"Error reading CSV: {e}")
        return
    
    if df.empty:
        logger.warning("No queries to process")
        return
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Initialize scraper
    scraper = PlaywrightEmailScraper(config=config, proxy_manager=proxy_manager)
    
    try:
        await scraper.start()
        
        processed_rows = []
        
        for index, row in df.iterrows():
            # Query is in second column (index 1)
            if len(row) < 2:
                continue
            
            query = str(row[1])
            
            # Skip if already processed (has value in column 3)
            if len(row) >= 3 and pd.notna(row[2]) and str(row[2]).lower() == "true":
                continue
            
            # Clean query name for filename
            query_name = re.sub(r'[\W_]+', '-', query.lower())[:50]
            
            # Scrape emails
            emails = await scraper.scrape_query(query)
            
            if emails:
                # Save to CSV
                random_suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=3))
                output_file = Path(output_dir) / f"{query_name}_{random_suffix}.csv"
                
                email_df = pd.DataFrame(emails, columns=['Emails'])
                email_df.index += 1
                email_df.to_csv(output_file, index_label='Sr No.')
                
                logger.info(f"  ✅ Saved {len(emails)} emails to {output_file.name}")
                processed_rows.append(index)
            else:
                logger.warning(f"  ⚠️  No emails found for query")
            
            # Rotate proxy periodically to avoid detection
            if proxy_manager and config and config.rotate_proxy_per_request:
                if random.random() < 0.3:  # 30% chance to rotate
                    await scraper.rotate_proxy()
        
        # Remove processed rows from source CSV
        if processed_rows:
            df = df.drop(processed_rows)
            df = df.reset_index(drop=True)
            df.to_csv(csv_path, header=None, index=False)
            logger.info(f"\n✅ Removed {len(processed_rows)} processed queries from source CSV")
        
        # Print stats
        stats = scraper.get_stats()
        logger.info(f"\n📊 Scraping Statistics:")
        logger.info(f"   Pages scraped: {stats['pages_scraped']}")
        logger.info(f"   Emails found: {stats['emails_found']}")
        logger.info(f"   CAPTCHAs encountered: {stats['captcha_count']}")
    
    finally:
        await scraper.stop()


async def main():
    """Main entry point"""
    # Load configuration from environment
    config = ScraperConfig.from_env()
    
    # Get paths from environment or use defaults
    csv_path = os.getenv('CSV_PATH', '/app/input/search.queries.1.csv')
    output_dir = os.getenv('OUTPUT_DIR', '/app/output')
    
    logger.info("=" * 60)
    logger.info("🚀 Playwright Stealth Email Scraper")
    logger.info("=" * 60)
    logger.info(f"CSV Path: {csv_path}")
    logger.info(f"Output Directory: {output_dir}")
    logger.info(f"Headless: {config.headless}")
    logger.info(f"Stealth Mode: {config.enable_stealth}")
    logger.info(f"Using Proxy: {config.use_proxy}")
    logger.info("=" * 60)
    
    # Setup proxy manager if configured
    proxy_manager = None
    if config.use_proxy and config.proxy_list_file:
        proxy_manager = ProxyManager(proxy_file=config.proxy_list_file)
        logger.info(f"Loaded {len(proxy_manager)} proxies")
    
    # Run scraper
    await scrape_from_csv(
        csv_path=csv_path,
        output_dir=output_dir,
        config=config,
        proxy_manager=proxy_manager
    )


if __name__ == "__main__":
    asyncio.run(main())
