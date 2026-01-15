"""
Proxy Manager for Playwright Stealth Email Scraper
Handles proxy rotation, health checking, and authentication
"""

import random
import asyncio
import aiohttp
from typing import List, Optional, Dict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Proxy:
    """Represents a proxy server"""
    server: str
    username: Optional[str] = None
    password: Optional[str] = None
    is_healthy: bool = True
    failure_count: int = 0
    last_used: float = 0
    
    def to_playwright_config(self) -> Dict:
        """Convert to Playwright proxy configuration"""
        config = {"server": self.server}
        if self.username and self.password:
            config["username"] = self.username
            config["password"] = self.password
        return config
    
    def __str__(self) -> str:
        if self.username:
            return f"{self.username}:***@{self.server}"
        return self.server


class ProxyManager:
    """
    Manages a pool of proxies with rotation, health checking, and failover
    """
    
    def __init__(
        self,
        proxies: Optional[List[str]] = None,
        proxy_file: Optional[str] = None,
        default_username: Optional[str] = None,
        default_password: Optional[str] = None,
        max_failures: int = 3,
        health_check_url: str = "https://httpbin.org/ip"
    ):
        """
        Initialize ProxyManager
        
        Args:
            proxies: List of proxy URLs (format: http://host:port or http://user:pass@host:port)
            proxy_file: Path to file containing proxy list (one per line)
            default_username: Default username for proxies without auth
            default_password: Default password for proxies without auth
            max_failures: Max failures before marking proxy unhealthy
            health_check_url: URL to use for health checks
        """
        self.proxies: List[Proxy] = []
        self.current_index = 0
        self.max_failures = max_failures
        self.health_check_url = health_check_url
        self.default_username = default_username
        self.default_password = default_password
        
        # Load proxies
        if proxies:
            self._load_proxies_from_list(proxies)
        if proxy_file:
            self._load_proxies_from_file(proxy_file)
    
    def _load_proxies_from_list(self, proxy_list: List[str]) -> None:
        """Load proxies from a list of URLs"""
        for proxy_url in proxy_list:
            proxy = self._parse_proxy_url(proxy_url)
            if proxy:
                self.proxies.append(proxy)
    
    def _load_proxies_from_file(self, file_path: str) -> None:
        """Load proxies from a file (one per line)"""
        path = Path(file_path)
        if not path.exists():
            print(f"Warning: Proxy file not found: {file_path}")
            return
        
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    proxy = self._parse_proxy_url(line)
                    if proxy:
                        self.proxies.append(proxy)
    
    def _parse_proxy_url(self, url: str) -> Optional[Proxy]:
        """
        Parse proxy URL into Proxy object
        Supports formats:
        - host:port
        - http://host:port
        - http://user:pass@host:port
        - user:pass@host:port
        """
        try:
            # Clean up the URL
            url = url.strip()
            
            # Extract auth if present
            username = None
            password = None
            
            # Check for @ (indicates auth)
            if "@" in url:
                auth_part, host_part = url.rsplit("@", 1)
                
                # Remove protocol from auth_part if present
                if "://" in auth_part:
                    auth_part = auth_part.split("://")[1]
                
                if ":" in auth_part:
                    username, password = auth_part.split(":", 1)
                
                # Reconstruct server URL
                if "://" in url:
                    protocol = url.split("://")[0]
                    server = f"{protocol}://{host_part}"
                else:
                    server = f"http://{host_part}"
            else:
                # No auth in URL
                if "://" not in url:
                    server = f"http://{url}"
                else:
                    server = url
                
                # Use default credentials if none provided
                username = self.default_username
                password = self.default_password
            
            return Proxy(
                server=server,
                username=username,
                password=password
            )
        except Exception as e:
            print(f"Warning: Failed to parse proxy URL '{url}': {e}")
            return None
    
    def get_next_proxy(self) -> Optional[Proxy]:
        """Get the next healthy proxy in rotation"""
        if not self.proxies:
            return None
        
        # Find next healthy proxy
        healthy_proxies = [p for p in self.proxies if p.is_healthy]
        
        if not healthy_proxies:
            # Reset all proxies if none are healthy
            print("Warning: All proxies marked unhealthy. Resetting...")
            for p in self.proxies:
                p.is_healthy = True
                p.failure_count = 0
            healthy_proxies = self.proxies
        
        # Round-robin selection
        self.current_index = (self.current_index + 1) % len(healthy_proxies)
        proxy = healthy_proxies[self.current_index]
        
        import time
        proxy.last_used = time.time()
        
        return proxy
    
    def get_random_proxy(self) -> Optional[Proxy]:
        """Get a random healthy proxy"""
        if not self.proxies:
            return None
        
        healthy_proxies = [p for p in self.proxies if p.is_healthy]
        
        if not healthy_proxies:
            # Reset all proxies if none are healthy
            for p in self.proxies:
                p.is_healthy = True
                p.failure_count = 0
            healthy_proxies = self.proxies
        
        return random.choice(healthy_proxies)
    
    def mark_failure(self, proxy: Proxy) -> None:
        """Mark a proxy as having failed"""
        proxy.failure_count += 1
        
        if proxy.failure_count >= self.max_failures:
            proxy.is_healthy = False
            print(f"Proxy marked unhealthy after {self.max_failures} failures: {proxy}")
    
    def mark_success(self, proxy: Proxy) -> None:
        """Mark a proxy as having succeeded (reset failure count)"""
        proxy.failure_count = 0
        proxy.is_healthy = True
    
    async def health_check(self, proxy: Proxy, timeout: int = 10) -> bool:
        """
        Check if a proxy is working by making a test request
        """
        try:
            proxy_url = proxy.server
            if proxy.username and proxy.password:
                # Insert auth into URL
                parts = proxy.server.split("://")
                if len(parts) == 2:
                    proxy_url = f"{parts[0]}://{proxy.username}:{proxy.password}@{parts[1]}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.health_check_url,
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    if response.status == 200:
                        proxy.is_healthy = True
                        proxy.failure_count = 0
                        return True
        except Exception as e:
            print(f"Health check failed for {proxy}: {e}")
        
        proxy.is_healthy = False
        return False
    
    async def health_check_all(self, timeout: int = 10) -> Dict[str, bool]:
        """Run health check on all proxies"""
        results = {}
        tasks = []
        
        for proxy in self.proxies:
            tasks.append(self.health_check(proxy, timeout))
        
        check_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for proxy, result in zip(self.proxies, check_results):
            if isinstance(result, Exception):
                results[str(proxy)] = False
            else:
                results[str(proxy)] = result
        
        return results
    
    def get_stats(self) -> Dict:
        """Get proxy pool statistics"""
        healthy = sum(1 for p in self.proxies if p.is_healthy)
        return {
            "total": len(self.proxies),
            "healthy": healthy,
            "unhealthy": len(self.proxies) - healthy,
            "proxies": [
                {
                    "server": p.server,
                    "healthy": p.is_healthy,
                    "failures": p.failure_count
                }
                for p in self.proxies
            ]
        }
    
    def __len__(self) -> int:
        return len(self.proxies)
    
    def __bool__(self) -> bool:
        return len(self.proxies) > 0


# Factory function for easy creation
def create_proxy_manager(
    proxy_list: Optional[List[str]] = None,
    proxy_file: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None
) -> ProxyManager:
    """Create a ProxyManager with the given configuration"""
    return ProxyManager(
        proxies=proxy_list,
        proxy_file=proxy_file,
        default_username=username,
        default_password=password
    )
