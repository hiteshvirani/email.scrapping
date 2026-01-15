"""
Human Behavior Simulation for Playwright Stealth Email Scraper
Simulates realistic human-like browsing patterns to avoid bot detection
"""

import asyncio
import random
import math
from typing import Tuple, Optional


class HumanBehavior:
    """Simulates human-like behavior in browser automation"""
    
    def __init__(self, config=None):
        """Initialize with optional configuration"""
        self.config = config
    
    async def random_delay(self, min_seconds: float = 0.5, max_seconds: float = 2.0) -> None:
        """
        Wait for a random amount of time to simulate human thinking/reading
        Uses a beta distribution for more natural timing
        """
        # Beta distribution gives more natural timing (most delays are medium-length)
        delay = min_seconds + (max_seconds - min_seconds) * random.betavariate(2, 5)
        await asyncio.sleep(delay)
    
    async def page_delay(self) -> None:
        """Delay between page loads (longer, simulating reading)"""
        if self.config:
            delay = self.config.get_page_delay()
        else:
            delay = random.uniform(3.0, 12.0)
        
        # Add some micro-variations
        delay += random.uniform(-0.5, 0.5)
        delay = max(1.0, delay)  # Minimum 1 second
        
        await asyncio.sleep(delay)
    
    async def action_delay(self) -> None:
        """Short delay between actions (clicking, typing, etc.)"""
        if self.config:
            delay = self.config.get_action_delay()
        else:
            delay = random.uniform(0.3, 1.5)
        
        await asyncio.sleep(delay)
    
    async def human_like_mouse_move(self, page, target_x: int, target_y: int) -> None:
        """
        Move mouse to target position with human-like curved movement
        Uses Bezier curves for natural movement patterns
        """
        try:
            # Get current viewport size
            viewport = page.viewport_size
            if not viewport:
                viewport = {"width": 1920, "height": 1080}
            
            # Start from a random position (simulating where cursor might be)
            start_x = random.randint(0, viewport["width"])
            start_y = random.randint(0, viewport["height"])
            
            # Generate bezier curve control points for natural movement
            control_x = (start_x + target_x) / 2 + random.randint(-100, 100)
            control_y = (start_y + target_y) / 2 + random.randint(-100, 100)
            
            # Number of steps for smooth movement
            steps = random.randint(15, 30)
            
            for i in range(steps + 1):
                t = i / steps
                
                # Quadratic Bezier curve calculation
                x = (1 - t) ** 2 * start_x + 2 * (1 - t) * t * control_x + t ** 2 * target_x
                y = (1 - t) ** 2 * start_y + 2 * (1 - t) * t * control_y + t ** 2 * target_y
                
                await page.mouse.move(x, y)
                
                # Variable speed - slower at start and end
                speed_factor = 1 - 4 * (t - 0.5) ** 2  # Parabola peaking at t=0.5
                delay = 0.01 + 0.02 * (1 - speed_factor)
                await asyncio.sleep(delay)
        except Exception:
            # If mouse movement fails, just continue
            pass
    
    async def human_like_click(self, page, element) -> None:
        """
        Click an element with human-like behavior:
        - Move mouse to element
        - Small random offset from center
        - Variable click timing
        """
        try:
            # Get element bounding box
            box = await element.bounding_box()
            if not box:
                await element.click()
                return
            
            # Calculate click position with slight randomness (not always dead center)
            offset_x = random.uniform(-box["width"] * 0.2, box["width"] * 0.2)
            offset_y = random.uniform(-box["height"] * 0.2, box["height"] * 0.2)
            
            target_x = box["x"] + box["width"] / 2 + offset_x
            target_y = box["y"] + box["height"] / 2 + offset_y
            
            # Move mouse to element
            await self.human_like_mouse_move(page, int(target_x), int(target_y))
            
            # Small delay before click
            await asyncio.sleep(random.uniform(0.05, 0.15))
            
            # Click with slight position variation
            await page.mouse.click(target_x, target_y)
            
            # Small delay after click
            await asyncio.sleep(random.uniform(0.1, 0.3))
        except Exception:
            # Fallback to regular click
            await element.click()
    
    async def human_like_typing(self, element, text: str, delay_range: Tuple[int, int] = (50, 150)) -> None:
        """
        Type text with human-like patterns:
        - Variable typing speed
        - Occasional pauses (simulating thinking)
        - Random micro-delays between keystrokes
        """
        for i, char in enumerate(text):
            # Base delay with variation
            delay = random.randint(delay_range[0], delay_range[1])
            
            # Occasionally pause longer (simulating thinking)
            if random.random() < 0.05:  # 5% chance
                delay += random.randint(200, 500)
            
            # Slightly faster for common patterns
            if i > 0 and text[i-1:i+1] in ['th', 'he', 'in', 'er', 'an', 're', 'on']:
                delay = int(delay * 0.7)
            
            await element.type(char, delay=delay)
    
    async def natural_scroll(self, page, direction: str = "down", amount: Optional[int] = None) -> None:
        """
        Scroll the page naturally with variable speed and pauses
        """
        if amount is None:
            amount = random.randint(200, 600)
        
        if direction == "up":
            amount = -amount
        
        # Break scroll into multiple smaller scrolls
        scroll_steps = random.randint(3, 8)
        step_amount = amount // scroll_steps
        
        for _ in range(scroll_steps):
            # Add variation to each step
            step = step_amount + random.randint(-30, 30)
            await page.mouse.wheel(0, step)
            
            # Variable delay between scroll steps
            await asyncio.sleep(random.uniform(0.05, 0.2))
        
        # Pause after scrolling (simulating reading)
        await asyncio.sleep(random.uniform(0.3, 1.0))
    
    async def scroll_to_element(self, page, element) -> None:
        """Scroll to make an element visible with natural scrolling"""
        try:
            # Check if element is visible
            is_visible = await element.is_visible()
            
            if not is_visible:
                # Get element position
                box = await element.bounding_box()
                viewport = page.viewport_size
                
                if box and viewport:
                    # Calculate how much to scroll
                    scroll_amount = box["y"] - viewport["height"] / 2
                    
                    if abs(scroll_amount) > 100:
                        await self.natural_scroll(page, "down" if scroll_amount > 0 else "up", int(abs(scroll_amount)))
            
            # Always try to scroll into view as fallback
            await element.scroll_into_view_if_needed()
        except Exception:
            pass
    
    async def random_page_interaction(self, page) -> None:
        """
        Perform random interactions to appear more human:
        - Random scrolling
        - Random mouse movements
        - Occasional hover on elements
        """
        actions = [
            self._random_scroll_action,
            self._random_mouse_movement_action,
            self._random_hover_action,
        ]
        
        # Pick 1-2 random actions
        num_actions = random.randint(1, 2)
        selected_actions = random.sample(actions, num_actions)
        
        for action in selected_actions:
            await action(page)
            await self.action_delay()
    
    async def _random_scroll_action(self, page) -> None:
        """Random small scroll"""
        direction = random.choice(["up", "down"])
        amount = random.randint(50, 200)
        await self.natural_scroll(page, direction, amount)
    
    async def _random_mouse_movement_action(self, page) -> None:
        """Random mouse movement"""
        viewport = page.viewport_size
        if viewport:
            x = random.randint(100, viewport["width"] - 100)
            y = random.randint(100, viewport["height"] - 100)
            await page.mouse.move(x, y)
    
    async def _random_hover_action(self, page) -> None:
        """Hover over a random link"""
        try:
            links = await page.query_selector_all("a")
            if links:
                link = random.choice(links[:10])  # Only from first 10 links
                box = await link.bounding_box()
                if box:
                    await page.mouse.move(
                        box["x"] + box["width"] / 2,
                        box["y"] + box["height"] / 2
                    )
                    await asyncio.sleep(random.uniform(0.1, 0.3))
        except Exception:
            pass


# Global instance
human = HumanBehavior()
