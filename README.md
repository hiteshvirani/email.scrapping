# 📧 Email Scraping System - Playwright Stealth Edition

A high-performance, stealthy email scraper designed to bypass bot detection and CAPTCHAs using **Playwright**. It simulates human behavior, rotates proxies, and extracts emails efficiently.

## 🚀 Key Features

*   **Anti-Detection**: Built on `playwright-stealth` to evade generic bot checks.
*   **Human Simulation**: Realistic mouse movements, typing speeds, and scrolling patterns.
*   **Proxy Support**: Built-in proxy rotation with health checks (supports HTTP/HTTPS).
*   **Scalable**: Docker-ready for easy deployment and scaling.
*   **Centralized Config**: Simple `.env` configuration.

---

## 🛠️ Setup & Installation

### Option 1: Docker (Recommended)

1.  **Build the Image**:
    ```bash
    ./run_docker.sh build
    ```

2.  **Configure Environment**:
    Copy `.env.example` to `.env` and adjust settings:
    ```bash
    cp .env.example .env
    ```
    *   Set `USE_PROXY=true` if using proxies.
    *   Set `HEADLESS=true` for background execution.

### Option 2: Local Python

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

---

## 🏃 Usage

### 1. Generate Search Queries
The scraper reads queries from CSV files in the `input/` folder. You can use the included script to generate them:

```bash
python generate.query.py
```
*This creates `input/search.queries.x.csv` files with queries like `site:linkedin.com "New York" "@gmail.com"`.*

### 2. Run the Scraper

**Using Docker:**
```bash
./run_docker.sh run
```

**Using Local Python:**
```bash
python playwright_scraper.py
```

### 3. Scaling (Multiple Containers)
To run multiple scrapers in parallel processing different CSV files, use Docker Compose.

1.  Edit `docker-compose.yml` to uncomment the scaling section or run:
    ```bash
    docker-compose up -d --scale email-scraper=3
    ```
    *Note: Ensure your `input/` directory has enough query files for multiple instances if you want them to process unique data, or configure different `CSV_PATH` env vars for each service in `docker-compose.yml`.*

### 4. Post-Processing
After scraping, consolidated emails can be found in the individual CSVs in `output/`. To merge them into a single file:

```bash
python filter_emails.py
```
*   Reads from `output/`
*   Saves to `emails/extracted_emails.csv`
*   Removes duplicates and invalid emails

---

## ⚙️ Configuration

| Variable | Default | Description |
| :--- | :--- | :--- |
| `HEADLESS` | `true` | Run browser in background |
| `ENABLE_STEALTH` | `true` | Use anti-detection techniques |
| `USE_PROXY` | `false` | Enable proxy rotation |
| `CSV_PATH` | `input/search.queries.1.csv` | Path to input queries |
| `OUTPUT_DIR` | `output` | Directory for scraped results |
| `MAX_PAGES_PER_QUERY`| `10` | Max Google pages to scrape per query |

### Proxy Configuration
Create a `proxies.txt` file (one per line):
```text
http://user:pass@1.2.3.4:8080
http://5.6.7.8:3128
```
Then set `PROXY_LIST_FILE=/app/proxies.txt` in `.env`.

---

## 🛡️ Anti-Detection Strategy

This scraper uses a multi-layered approach:
1.  **Browser Fingerprinting**: Modifies `navigator` properties (`webdriver`, `plugins`, `languages`) to look like a real user.
2.  **Behavioral Analysis**: Randomizes delays between actions and mimics human mouse curves.
3.  **Network**: Rotates User-Agents and Proxies to prevent IP bans.

**Note**: If you encounter CAPTCHAs, increase `MIN_PAGE_DELAY` in `.env` or use high-quality residential proxies.
