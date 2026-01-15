#!/bin/bash

# ============================================
# Playwright Stealth Email Scraper
# Docker Build and Run Script
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="playwright-email-scraper"
CONTAINER_NAME="email-scraper"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Playwright Stealth Email Scraper - Docker${NC}"
echo -e "${BLUE}============================================${NC}"

# Create directories if they don't exist
mkdir -p input output logs

# Parse command line arguments
ACTION="${1:-run}"

case $ACTION in
    build)
        echo -e "${GREEN}Building Docker image...${NC}"
        docker build -t ${IMAGE_NAME}:latest .
        echo -e "${GREEN}Build complete!${NC}"
        ;;
    
    run)
        echo -e "${GREEN}Running scraper...${NC}"
        
        # Stop existing container if running
        docker stop ${CONTAINER_NAME} 2>/dev/null || true
        docker rm ${CONTAINER_NAME} 2>/dev/null || true
        
        # Run container
        docker run -it --rm \
            --name ${CONTAINER_NAME} \
            -v "$(pwd)/input:/app/input:ro" \
            -v "$(pwd)/output:/app/output" \
            -e HEADLESS=true \
            -e ENABLE_STEALTH=true \
            -e USE_PROXY=false \
            -e CSV_PATH=/app/input/search.queries.1.csv \
            -e OUTPUT_DIR=/app/output \
            ${IMAGE_NAME}:latest
        ;;
    
    run-with-proxy)
        echo -e "${GREEN}Running scraper with proxy...${NC}"
        
        if [ ! -f "proxies.txt" ]; then
            echo -e "${YELLOW}Warning: proxies.txt not found. Creating from example...${NC}"
            cp proxies.example.txt proxies.txt 2>/dev/null || echo "# Add your proxies here" > proxies.txt
        fi
        
        docker stop ${CONTAINER_NAME} 2>/dev/null || true
        docker rm ${CONTAINER_NAME} 2>/dev/null || true
        
        docker run -it --rm \
            --name ${CONTAINER_NAME} \
            -v "$(pwd)/input:/app/input:ro" \
            -v "$(pwd)/output:/app/output" \
            -v "$(pwd)/proxies.txt:/app/proxies.txt:ro" \
            -e HEADLESS=true \
            -e ENABLE_STEALTH=true \
            -e USE_PROXY=true \
            -e PROXY_LIST_FILE=/app/proxies.txt \
            -e CSV_PATH=/app/input/search.queries.1.csv \
            -e OUTPUT_DIR=/app/output \
            ${IMAGE_NAME}:latest
        ;;
    
    compose)
        echo -e "${GREEN}Running with Docker Compose...${NC}"
        docker-compose up --build
        ;;
    
    compose-detach)
        echo -e "${GREEN}Running with Docker Compose (detached)...${NC}"
        docker-compose up -d --build
        ;;
    
    stop)
        echo -e "${YELLOW}Stopping container...${NC}"
        docker stop ${CONTAINER_NAME} 2>/dev/null || docker-compose down
        echo -e "${GREEN}Stopped!${NC}"
        ;;
    
    logs)
        docker logs -f ${CONTAINER_NAME} 2>/dev/null || docker-compose logs -f
        ;;
    
    shell)
        echo -e "${GREEN}Opening shell in container...${NC}"
        docker run -it --rm \
            --name ${CONTAINER_NAME}-shell \
            -v "$(pwd)/input:/app/input:ro" \
            -v "$(pwd)/output:/app/output" \
            ${IMAGE_NAME}:latest \
            /bin/bash
        ;;
    
    test)
        echo -e "${GREEN}Running detection test...${NC}"
        docker run -it --rm \
            --name ${CONTAINER_NAME}-test \
            ${IMAGE_NAME}:latest \
            python -c "
import asyncio
from playwright.async_api import async_playwright
from stealth_utils import apply_stealth, setup_stealth_context
from config import get_random_user_agent

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await setup_stealth_context(
            browser,
            user_agent=get_random_user_agent(),
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        await apply_stealth(page)
        
        # Test on bot detection site
        await page.goto('https://bot.sannysoft.com/')
        await asyncio.sleep(3)
        await page.screenshot(path='/app/output/test_detection.png')
        print('Screenshot saved to /app/output/test_detection.png')
        
        await browser.close()

asyncio.run(test())
"
        ;;
    
    *)
        echo -e "${YELLOW}Usage: $0 {build|run|run-with-proxy|compose|compose-detach|stop|logs|shell|test}${NC}"
        echo ""
        echo "Commands:"
        echo "  build           - Build the Docker image"
        echo "  run             - Run the scraper (basic mode)"
        echo "  run-with-proxy  - Run with proxy rotation"
        echo "  compose         - Run with Docker Compose"
        echo "  compose-detach  - Run with Docker Compose (detached)"
        echo "  stop            - Stop the container"
        echo "  logs            - View container logs"
        echo "  shell           - Open a shell in the container"
        echo "  test            - Run bot detection test"
        exit 1
        ;;
esac
