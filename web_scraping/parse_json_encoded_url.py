import urllib.parse
import json

'''this file is meant to parse the URL-encoded JSON string of the website that you are trying to webscrape.  To use this utility file first:

 1. copy the URL of the website that your trying to scrape 
 example: https://www.zillow.com/seattle-wa/rentals/20_p/?searchQueryState=%7B%22mapBounds%22%3A%7B%22west%22%3A-122.465159%2C%22east%22%3A-122.224433%2C%22south%22%3A47.491912%2C%22north%22%3A47.734145%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A16037%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22pagination%22%3A%7B%22currentPage%22%3A20%7D%7D)

2. remove the string up to the first % sign: 
example: %7B%22mapBounds%22%3A%7B%22west%22%3A-122.465159%2C%22east%22%3A-122.224433%2C%22south%22%3A47.491912%2C%22north%22%3A47.734145%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A16037%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22pagination%22%3A%7B%22currentPage%22%3A20%7D%7D

3. then pass this as the encoded json to return a decoded json object
'''

url_encoded_json = '%7B%22mapBounds%22%3A%7B%22west%22%3A-122.465159%2C%22east%22%3A-122.224433%2C%22south%22%3A47.491912%2C%22north%22%3A47.734145%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A16037%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22pagination%22%3A%7B%22currentPage%22%3A9%7D%7D'

decoded_json = urllib.parse.unquote(url_encoded_json)
json_object = json.loads(decoded_json)

print(json_object)
