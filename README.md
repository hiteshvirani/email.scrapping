# 📧 Email Scraping Tool - The Ultimate Email Hunter!

## 🌟 Overview

Welcome to the **Email Scraping Tool**, where we turn you into a digital detective! Whether you’re chasing down emails from a single CSV file or unleashing an army of containers to tackle a CSV army, we’ve got your back. This tool breaks the job into two epic modes:

1. **Manual Mode**: 🔍 For when you’re in the zone and just need to scrape emails from one CSV.
2. **Automated Mode**: 🗿 The big leagues. Let’s automate this! Just throw a bunch of CSVs at it and let the magic happen.

## 🛠️ Prerequisites

- **Docker**: Because we don’t want to clutter your system. [Get Docker](https://docs.docker.com/get-docker/) and keep your machine clean.

## 🚀 Getting Started

### 1. Clone the Repository

Start by cloning the repo to your local machine. We’ll keep it simple:

```bash
git clone https://github.com/your-username/email-scraping-tool.git
cd email-scraping-tool
```

### 2. Build the Docker Image

Now, let’s build that Docker image. It’s like baking a cake but without the calories:

```bash
docker build -t scrapping_img .
```

## 📦 Manual Mode: The Solo Act

**Run a single container to scrape emails from your CSV file. It’s like one-on-one training:**

```bash
docker run \
  --name email-scraper-container \
  -v /path/to/your/input/search.queries.1.csv:/app/input/search.queries.1.csv \
  -v /path/to/your/output:/app/output \
  -e DISPLAY=:99 \
  -e CSV_PATH=/app/input/search.queries.1.csv \
  scrapping_img \
  python scrapping.py
```

**Parameters:**
- Swap out `/path/to/your/input/search.queries.1.csv` with your actual CSV path.
- Set `/path/to/your/output` where you want those juicy email results.
- Change `CSV_PATH` if you’re using a different file. 

**Emails will be delivered straight to your output folder.**

## ⚙️ Automated Mode: The Multitasking Master

**Ready to go big? Automate the entire process and let the machines do the heavy lifting:**

1. **Set Permissions and Run the Script:**

```bash
chmod +x run_scrapper.sh
./run_scrapper.sh
```

2. **Prepare Your Arsenal:**
   - Drop all your query CSV files into the `/input` folder.
   - Keep it simple: each CSV should have one query to avoid chaos.

**Why Automated Mode Rocks:**
- 🗿 **Multi-Container Madness**: Multiple containers working in sync. It’s like having a small army.
- 📂 **Organized Output**: Scraped emails are neatly stored in the `/output` folder.
- 📜 **Logs Galore**: All container logs are saved in the `logs/` folder. Keep tabs on your scraping adventure!
- 💪 **Error Handling**: Automated error management. No sweat, just results.

## 📁 Directory Layout

- **`/input`**: Toss your query CSV files here.
- **`/output`**: Where the magic happens – your scraped emails are stored.
- **`logs/`**: For all the juicy details – container logs.

## 🤝 Contributing

Want to make this tool even cooler? Fork it, add your magic, and send a pull request. We love new ideas!

## 📜 License

This tool is licensed under the MIT License. Check out the [LICENSE](LICENSE) file for all the legal jazz.

## 🙌 Acknowledgments

- **Docker**: For keeping things tidy and organized.
- **Python**: For making scraping a breeze.

Got questions? Open an issue or shoot me a message. Let’s get scraping!

Happy scraping, you digital detective! 🕵️‍♂️🎉
