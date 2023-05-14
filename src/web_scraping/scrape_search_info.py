"""  A module to scrape the search url for the listing url extensions (ex. /seattle-wa/arthouse/5Yy9f4/").

This module is a work in progress and will be updated as the project progresses.
"""
import requests
import json
from bs4 import BeautifulSoup

HEADERS = {
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

def scrape():
    """ A function to scrape the search url for the listing url extensions.
    """


# make a list of responses to store the html requests
response_list = []

# define the parameters for the request such as the city, mapbounds, region and filter state

city = 'seattle-wa'

# IMPORTANT** for search results with number of listings above 800, you must create a filter to make sure the number of listings stay under 800.  In this case, limiting the minimum and maximum rent will keep the number of listings under 800.
rent_intervals = [(0, 1699), (1700, 2199), (2200, 3199), (3200, 9000)]

# pagination for each search result
max_page_num = 20
current_page = 1

# make a list of information to make the requests
request_info_list = []

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
        # append the request information to the request_info_list
        request_info_list.append((current_page, params))

        # increase the page counter
        current_page += 1
        
    # reset the page counter
    current_page = 1

# iterate through each page in the request_info_list
for (current_page, params) in request_info_list:
    
    # store the html request for the current page of the current rent_interval
    response = requests.get('https://www.zillow.com/' +
                        f'{city}/' + 'rentals/' + f'{current_page}_p/' + '?searchQueryState=', headers=HEADERS, params=params)
    
    # append the response to the response_list
    response_list.append(response)

soup_list = []
for response in response_list:
    soup = BeautifulSoup(response.text, 'html.parser')
    soup_list.append(soup)

apartment_info = []

# find the list_results json object for each soup in soup_list (contains the apartment information)
for soup in soup_list:
    API_request_tag = soup.find("script", {"data-zrr-shared-data-key": "mobileSearchPageStore", "type": "application/json"})
    json_API_request_tag = API_request_tag.text.replace('<!--', '').replace('-->', '')
    API_request_dict = json.loads(json_API_request_tag)

    # this python dictionary is a python dict that contains multiple dicts.  To find where the list_results dict is, the following selections must happen: cat1 dict->searchResults dict->listResults dict
    for key, value in API_request_dict.items():
        # find the cat1 (category 1) dict
        if key == 'cat1':
            for key, value in value.items():
                # find the searchResults dict
                if key == 'searchResults':
                    for key, value in value.items():
                        # find the listResults dict
                        if key == 'listResults':
                            for listing in value:
                                apartment_info.append(listing)

apartment_info_json = json.dumps(apartment_info)

with open('C:/Projects/Housing_Price_Prediction/data_processing/raw_bld_url_exts.json', 'w') as f:
    f.write(apartment_info_json)
