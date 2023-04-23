import requests
import pandas as pd

'''This python file will gather and parse specific apartment data using each building key and lotID.  The request made is meant to mimick a fetch request to the zillow API for data on a specific apartment.  This is done by making a .post() request from the `detailUrl`.  The `detailUrl` is the redirect link that shows a specific apartment's information, and is what the user clicks on in the right search bar of the zillow.com website to inquire about a specific apartment. This file converts the API curl request made to zillow's server and uses it to create a response with the following apartment data:
(insert apartment data here)
'''

# open the database of building keys, lotIDs and detailUrls
# example dataframe
data = {
    'building_keys': [420, 380, 390],
    'lotIds': [50, 40, 45],
    'detailUrls': [140, 160, 180]
}

df = pd.DataFrame(data)
# make a parameter list with all of the information to make a zillow database query
paramlist = []

# iterate through the dataframe rows and set the headers and data for the paramlist
for index, row in df.iterrows():

    # for each row in the dataframe, set the detail Url, building key and lotId
    detailUrl = row['detailUrl']
    buildingkey = row['building_keys']
    lotId = row['lotId']
    headers = {
        'authority': 'www.zillow.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,it-IT;q=0.8,it;q=0.7',
        'client-id': 'vertical-living',
        'content-type': 'text/plain',
        'dnt': '1',
        'origin': 'https://www.zillow.com',

        # set the referer to the 'origin' + 'detail Url' value, example: 'https://www.zillow.com/b/arthouse-seattle-wa-5Yy9f4/'
        'referer': 'https://www.zillow.com' + detailUrl,
        'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    }

    # set the building key and the lotId to the rows building key and lotId
    data = '{"operationName":"BuildingQuery","variables":{"buildingKey":f{buildingkey},"cache":false,"latitude":null,"longitude":null,"lotId":f{lotId},"update":false},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"ad04c9e688ad8981f898c335a89d09f9778804786b2211073ee12ff80e530a63"}}}'

# loop through the paramlist and make a response list
responselist = []
for headers, data in paramlist:
    response = requests.post('https://www.zillow.com/graphql/',
                             headers=headers, data=data)
    responselist.append(response)
print(response)
