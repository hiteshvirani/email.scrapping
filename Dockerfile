# ============================================
# Playwright Stealth Email Scraper
# Docker Image using Official Playwright Base
# ============================================

# Use official Playwright image which includes Python and all browser dependencies
FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Install Playwright browsers (Chromium only for smaller image if possible, 
# but the base image might have them or we ensure they are present)
RUN playwright install chromium

# Copy application code
COPY config.py .
COPY human_behavior.py .
COPY proxy_manager.py .
COPY stealth_utils.py .
COPY playwright_scraper.py .

# Optional: Copy legacy scripts if needed (keeping filter_emails as it might be useful)
COPY filter_emails.py .

# Create directories for input/output
RUN mkdir -p /app/input /app/output

# Default environment variables
ENV HEADLESS=true
ENV ENABLE_STEALTH=true
ENV USE_PROXY=false
ENV CSV_PATH=/app/input/search.queries.1.csv
ENV OUTPUT_DIR=/app/output
ENV MIN_PAGE_DELAY=3.0
ENV MAX_PAGE_DELAY=12.0
ENV MAX_PAGES_PER_QUERY=10

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from playwright.sync_api import sync_playwright; print('OK')" || exit 1

# Run the scraper
CMD ["python", "playwright_scraper.py"]
