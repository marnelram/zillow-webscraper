import requests
from bs4 import BeautifulSoup

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
        'ah': {'value': True}
    },
    'pagination': {
        'currentPage': page
    }
}

# make a list of URLs to extract the html data
urllist = []
while page <= pagenum:
    url = 'https://www.zillow.com/' + \
        f'{city}/' + 'rentals/' + f'{page}_p/' + '?searchQueryState='
    urllist.append(url)

# get the html response each url in the url list and store it in a response list
responselist = []
for url in urllist:
    response = requests.get(url, headers=headers, params=params)
    responselist.append(response)
    page += 1

# parse the html responses through beautiful soup and make a soup list
souplist = []
for response in responselist:
    soup = BeautifulSoup(response.content, 'html.parser')

print(responselist[1].content)
