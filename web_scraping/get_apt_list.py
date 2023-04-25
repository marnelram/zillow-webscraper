import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

'''This python file makes html requests to the zillow back-end server via the zillow website with parameters for the apartment listings that you need to scrape from.  The requests are recieved in a JSON format, and is parsed to extract the apartment's building key, lotId and the detailUrl to scrape more information.

IMPORTANT:

'''
# make a list of responses to store the html requests
response_list = []

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

# your city
city = 'seattle-wa'

# define the rent interval to scrape from
# IMPORTANT** for search results with number of listings above 800, you must create a filter to make sure the number of listings stay under 800.  In this case, limiting the minimum and maximum rent will keep the number of listings under 800.
rent_intervals = [(0, 1699), (1700, 2199), (2200, 3199), (3200, 9000)]

# pagination for each search result
max_pages = 20
current_page = 1

# iterate through each rent_interval filter
for (min_rent, max_rent) in rent_intervals:

    # iterate through each page for the current rent_interval filter
    while current_page <= max_pages:
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
                'currentPage': current_page
            }
        }
        # store the html request for the current page of the current rent_interval
        response = requests.get('https://www.zillow.com/' +
                                f'{city}/' + 'rentals/' + f'{current_page}_p/' + '?searchQueryState=', headers=headers, params=params)

        # append the response to the response_list
        response_list.append(response)

    # reset the page counter
    current_page = 1

# parse the JSON doc

"""
# parse the html responses through beautiful soup and make a soup list
souplist = []
for response in response_list:
    soup = BeautifulSoup(response.content, 'html.parser')
    souplist.append(soup)

# parse the beautiful soup into a dataframe

# the html document has a JSON doc at the bottom.  Parse the JSON doc, gather the information from "cat1" to "total result count"
print(souplist[1].prettify())
"""
