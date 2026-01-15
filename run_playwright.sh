#!/bin/bash

# ============================================
# Playwright Stealth Email Scraper
# Run Script for Local Development
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Playwright Stealth Email Scraper${NC}"
echo -e "${BLUE}============================================${NC}"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Install Playwright browsers if not already installed
echo -e "${GREEN}Installing Playwright browsers...${NC}"
playwright install chromium

# Check for .env file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}Creating .env from .env.example...${NC}"
        cp .env.example .env
    fi
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Default paths
INPUT_DIR="${INPUT_DIR:-./input}"
OUTPUT_DIR="${OUTPUT_DIR:-./output}"

# Create directories if they don't exist
mkdir -p "$INPUT_DIR" "$OUTPUT_DIR"

echo -e "${GREEN}Configuration:${NC}"
echo -e "  Input Directory:  ${INPUT_DIR}"
echo -e "  Output Directory: ${OUTPUT_DIR}"
echo -e "  Headless Mode:    ${HEADLESS:-true}"
echo -e "  Stealth Mode:     ${ENABLE_STEALTH:-true}"
echo -e "  Use Proxy:        ${USE_PROXY:-false}"
echo ""

# Run the scraper
echo -e "${GREEN}Starting scraper...${NC}"
echo -e "${BLUE}--------------------------------------------${NC}"
python playwright_scraper.py

echo -e "${BLUE}--------------------------------------------${NC}"
echo -e "${GREEN}Scraping complete!${NC}"
