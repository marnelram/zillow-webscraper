from src import zillow_scraper

# copy the url from the search results page
url = "https://www.zillow.com/los-angeles-ca/rentals/?searchQueryState=%7B%22usersSearchTerm%22%3A%22Los%20Angeles%2C%20CA%22%2C%22mapBounds%22%3A%7B%22west%22%3A-119.21510774414062%2C%22east%22%3A-117.60835725585937%2C%22south%22%3A33.49931041837867%2C%22north%22%3A34.53964245346171%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A12447%2C%22regionType%22%3A6%7D%5D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22price%22%3A%7B%22min%22%3A162842%2C%22max%22%3A447816%7D%2C%22mp%22%3A%7B%22min%22%3A800%2C%22max%22%3A2200%7D%2C%22beds%22%3A%7B%22min%22%3A2%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%7D"

# create a zillow scraper and pass the search url and number of pages to scrape
scraper = zillow_scraper.ZillowScraper(url, 5)
print(scraper.parse_search_url())
