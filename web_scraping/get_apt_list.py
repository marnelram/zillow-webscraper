import requests
from bs4 import BeautifulSoup
import pandas as pd

'''This python file makes html requests to the zillow websites with parameters for the apartment listings that you need to scrape from
'''
# define the headers for the request
headers = {
    'authority': 'www.zillow.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,it-IT;q=0.8,it;q=0.7',
    'dnt': '1',
    'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
}

# define the parameters for the request such as the city, mapbounds, region and filter state
city = 'seattle-wa'

# number of pages of listings for your city
pagenum = 20
page = 1
# define the minimum and maximum monthy rent (to get all of the apartment listings in seattle multiple scraping sessions have to be made.  The maximum amount of listings shown for one search is about 800, or 20 pages of listings)
rent_interval = [(0, 1699), (1700, 2199), (2200, 3199), (3200, 9000)]

# make a list of parameters for each rent interval
params_list = []
for (min_rent, max_rent) in rent_interval:
    params = {
        'mapBounds': {
            'west': -122.465159,
            'east': -122.224433,
            'south': 47.491912,
            'north': 47.734145
        },
        'regionSelection': [
            {
                'regionId': 16037,
                'regionType': 6
            }
        ],
        'filterState': {
            'fsba': {'value': False},
            'fsbo': {'value': False},
            'nc': {'value': False},
            'fore': {'value': False},
            'cmsn': {'value': False},
            'auc': {'value': False},
            'fr': {'value': True},
            'ah': {'value': True},
            'mf': {'value': False},
            'land': {'value': False},
            'manu': {'value': False},

            # monthy rent
            'mp': {'max': max_rent, 'min': min_rent},
        },
        'pagination': {
            'currentPage': page
        }
    }
    params_list.append(params)

# make a list of URLs to extract the html data
url_list = []
# iterate through each rent interval
for params in params_list:

    # iterate trough each page for each rent interval
    while page <= pagenum:

        # for each page, make a url and add it to the url_list
        url = 'https://www.zillow.com/' + \
            f'{city}/' + 'rentals/' + f'{page}_p/' + '?searchQueryState='
        url_list.append(url)

        # increase the page counter
        page += 1
    # reset the page counter
    page = 1

# get the html response each url in the url list and store it in a response list
response_list = []
for url in url_list:
    response = requests.get(url, headers=headers, params=params)
    response_list.append(response)

# parse the html responses through beautiful soup and make a soup list
souplist = []
for response in response_list:
    soup = BeautifulSoup(response.content, 'html.parser')
    souplist.append(soup)

# parse the beautiful soup into a dataframe
print(souplist[1].prettify())
