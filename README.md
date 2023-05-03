# Zillow Web Scraper
This is a Python script that allows you to scrape data from Zillow, a popular online real estate marketplace, and save it to a CSV file. You can use this data for various purposes such as analysis, research, and visualization.

## Prerequisites
Python 3.x
Requests
BeautifulSoup4
Pandas

## Usage
1. Clone this repository to your local machine.
2. Install the required Python packages by running pip install -r requirements.txt in your terminal or command prompt.
3. Open zillow_scraper.py in your preferred code editor and modify the URL and other settings to suit your needs.
4. Run zillow_scraper.py by typing python zillow_scraper.py in your terminal or command prompt.
5. Wait for the script to finish scraping the data from Zillow.
6. Find the CSV file containing the scraped data in the output folder.

## Configuration
You can configure the following settings in `zillow_scraper.py`:

- `BASE_URL`: The base URL of the Zillow website. You can change this if you want to scrape data from a different Zillow website, e.g., Zillow Canada.
- `SEARCH_URL`: The search URL for the Zillow search query. You can change this to customize your search query, e.g., by changing the location or property type.
- `HEADERS`: The HTTP headers used by the scraper. You can modify this to mimic a different user agent or to include other custom headers.
- `MAX_PAGES`: The maximum number of pages to scrape. You can change this to scrape more or fewer pages, depending on your needs.
- `DELAY`: The delay between requests, in seconds. You can change this to avoid overloading the Zillow servers and captchas.

## Limitations
Please note that web scraping can be against the terms of service of some websites and may be illegal in some jurisdictions. Use this script at your own risk and responsibility. Additionally, Zillow may change their website structure or anti-scraping measures at any time, which could render this script obsolete.
