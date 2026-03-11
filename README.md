# Vivino Filters Scraper

Automated data extraction tool for Vivino using Python and Selenium to collect Grapes, Regions, Countries, and Wine Styles from the explore filters.

## Features
- **Selenium Automation**: Uses Selenium to handle Vivino's dynamic, JavaScript-heavy pages.
- **Filter Scraping**: Opens the explore page and extracts all available:
  - Grapes
  - Regions
  - Countries
  - Wine Styles
- **Smart UI Handling**: Automatically clicks "Show more" and expands all filter toggles so hidden options are included.
- **Clean JSON Output**: Normalizes and deduplicates filter items, then saves them into a single JSON file (e.g. `vivino_filters.json`).

## Tech Stack
- Python 3.9.6
- Selenium

## Requirements

- Python 3.9.6
- Google Chrome (latest version)
- ChromeDriver matching your Chrome version
- pip package manager

---

## Installation
```bash
git clone https://github.com/yourusername/vivino_filters_scraper.git
cd vivino_filters_scraper
pip install -r requirements.txt

## Usage

```bash
python main.py

## What the Scraper Does

The scraper will:

- Launch the Vivino explore page
- Automatically expand all filter toggles (Grapes, Regions, Countries, Wine Styles)
- Click **"Show more"** until all options load
- Extract, clean, and deduplicate the data
- Save results to `vivino_filters.json`

---

## Sample Output

```json
{
  "grapes": ["Pinot Noir", "Cabernet Sauvignon", "Chardonnay"],
  "regions": ["Napa Valley", "Tuscany", "Bordeaux"],
  "countries": ["USA", "France", "Italy", "Spain"],
  "wine_styles": ["Red", "White", "Sparkling", "Dessert"]
}
