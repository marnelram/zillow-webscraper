import urllib.parse
import json

"""this file is meant to parse the URL-encoded JSON string of the website that you are trying to webscrape.  To use this utility file first:

 1. copy the URL of the website that your trying to scrape
 example: https://www.zillow.com/seattle-wa/rentals/20_p/?searchQueryState=%7B%22mapBounds%22%3A%7B%22west%22%3A-122.465159%2C%22east%22%3A-122.224433%2C%22south%22%3A47.491912%2C%22north%22%3A47.734145%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A16037%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22pagination%22%3A%7B%22currentPage%22%3A20%7D%7D)

2. remove the string up to the first % sign:
example: %7B%22mapBounds%22%3A%7B%22west%22%3A-122.465159%2C%22east%22%3A-122.224433%2C%22south%22%3A47.491912%2C%22north%22%3A47.734145%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A16037%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22pagination%22%3A%7B%22currentPage%22%3A20%7D%7D

3. then pass this as the encoded json to return a decoded json object
"""

url_encoded_json = '%7B"pagination"%3A%7B%7D%2C"mapBounds"%3A%7B"north"%3A47.81096392569374%2C"south"%3A47.36731519862966%2C"east"%3A-121.84965815488289%2C"west"%3A-123.04167475644539%7D%2C"regionSelection"%3A%5B%7B"regionId"%3A16037%2C"regionType"%3A6%7D%5D%2C"isMapVisible"%3Atrue%2C"filterState"%3A%7B"fsba"%3A%7B"value"%3Afalse%7D%2C"fsbo"%3A%7B"value"%3Afalse%7D%2C"nc"%3A%7B"value"%3Afalse%7D%2C"cmsn"%3A%7B"value"%3Afalse%7D%2C"auc"%3A%7B"value"%3Afalse%7D%2C"fore"%3A%7B"value"%3Afalse%7D%2C"fr"%3A%7B"value"%3Atrue%7D%2C"mf"%3A%7B"value"%3Afalse%7D%2C"land"%3A%7B"value"%3Afalse%7D%2C"manu"%3A%7B"value"%3Afalse%7D%2C"mp"%3A%7B"max"%3A2800%2C"min"%3A2200%7D%2C"price"%3A%7B"max"%3A559020%2C"min"%3A439230%7D%7D%2C"isListVisible"%3Atrue%7D'

url_encoded_json_2 = "%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22Los%20Angeles%2C%20CA%22%2C%22mapBounds%22%3A%7B%22west%22%3A-119.21510774414062%2C%22east%22%3A-117.60835725585937%2C%22south%22%3A33.49931041837867%2C%22north%22%3A34.53964245346171%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A12447%2C%22regionType%22%3A6%7D%5D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22price%22%3A%7B%22min%22%3A162842%2C%22max%22%3A322980%7D%2C%22mp%22%3A%7B%22min%22%3A800%2C%22max%22%3A1600%7D%2C%22beds%22%3A%7B%22min%22%3A2%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%7D"

decoded_json = urllib.parse.unquote(url_encoded_json)
decoded_json_2 = urllib.parse.unquote(url_encoded_json_2)
json_object = json.loads(decoded_json)
json_object_2 = json.loads(decoded_json_2)

print(json_object)
print()
print(json_object_2)
