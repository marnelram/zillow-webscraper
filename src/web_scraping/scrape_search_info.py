"""  A module to scrape the search url for the listing url extensions (ex. /seattle-wa/arthouse/5Yy9f4/").

This module is a work in progress and will be updated as the project progresses.
"""
import requests
import json
from bs4 import BeautifulSoup

HEADERS = {
    "authority": "www.zillow.com",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,it-IT;q=0.8,it;q=0.7",
    "dnt": "1",
    "sec-ch-ua": '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
}
city = "seattle-wa"
max_page_num = 20
# IMPORTANT** for search results with number of listings above 800, you must create a filter to make sure the number of listings stay under 800.  In this case, limiting the minimum and maximum rent will keep the number of listings under 800.
rent_intervals = [(0, 1699), (1700, 2199), (2200, 3199), (3200, 9000)]


def run():
    """A function to run when the scrape_search_info.py module is called

    A work in progress, will be updated when the project progresses
    """
    response_list = scrape_search_results_from_zillow()
    pass


def set_request_info(
    city: str, rent_intervals: list, max_page_num: int
) -> list:
    """Makes a request information list that includes the parameters and current page.

    A work in progress.  Will be updated when the project progresses

    Args:
        city (str): The city to that is being scraped.
        rent_intervals (list): A list of rent intervals to be scraped.
        max_page_num (int): The maximum number of pages

    Returns:
        request_info_list (list): The list of information needed to make a HTML request.  Contains the parameters and current page for the request.
    """

    def set_params(min_rent: int, max_rent: int, current_page: int) -> dict:
        """Sets the parameters for the request info list.

        A work in progress, will be updated when the project progresses.

        Args:
            min_rent (int): The minimum rent of the current interval in the rent_interval list.
            max_rent (int): The maximum rent of the current interval in the rent_interval list.
            current_page (int): The current page being scraped.

        Returns:
            params (dict): The parameter list for the current page.
        """
        params = {
            "mapBounds": {
                "west": -122.465159,
                "east": -122.224433,
                "south": 47.491912,
                "north": 47.734145,
            },
            "regionSelection": [{"regionId": 16037, "regionType": 6}],
            "filterState": {
                "fsba": {"value": False},
                "fsbo": {"value": False},
                "nc": {"value": False},
                "fore": {"value": False},
                "cmsn": {"value": False},
                "auc": {"value": False},
                "fr": {"value": True},
                "ah": {"value": True},
                "mf": {"value": False},
                "land": {"value": False},
                "manu": {"value": False},
                # monthy rent
                "mp": {"max": max_rent, "min": min_rent},
            },
            "pagination": {"currentPage": current_page},
        }
        return params

    request_info_list = []
    current_page = 1
    for min_rent, max_rent in rent_intervals:
        # iterate through each page for the current rent_interval filter
        while current_page <= max_page_num:
            request_info_list.append(
                current_page,
                params=set_params(min_rent, max_rent, current_page),
            )
            current_page += 1
        current_page = 1
    return request_info_list


def scrape_search_results_from_zillow(response_list: list) -> list:
    """A function to scrape the search url for the listing url extensions.

    In progress, will be updated as the project progresses.

    Returns:
        A list of response objects generated from scraping the search results from zillow
    """
    request_info_list = set_request_info(
        city=city, rent_intervals=rent_intervals, max_page_num=max_page_num
    )
    response_list = []
    for current_page, params in request_info_list:
        # store the html request for the current page of the current rent_interval
        response = requests.get(
            "https://www.zillow.com/"
            + f"{city}/"
            + "rentals/"
            + f"{current_page}_p/"
            + "?searchQueryState=",
            headers=HEADERS,
            params=params,
        )
        response_list.append(response)
    return response_list


def parse_responses(response_list: list) -> list:
    """Parses the responses made to Zillow through beautiful soup."""

    def make_soup_list(response_list: list) -> list:
        """Parses the response list into a beautiful soup object."""
        soup_list = []
        for response in response_list:
            soup = BeautifulSoup(response.text, "html.parser")
            soup_list.append(soup)

    def get_list_results(soup: object) -> dict:
        """Finds the list_results json object in the soup."""

        def get_API_request_dict(soup: object) -> dict:
            """Get's the dictionary containing the API request information"""
            API_request_tag = soup.find(
                "script",
                {
                    "data-zrr-shared-data-key": "mobileSearchPageStore",
                    "type": "application/json",
                },
            )
            json_API_request_tag = API_request_tag.text.replace("<!--", "").replace(
                "-->", ""
            )
            API_request_dict = json.loads(json_API_request_tag)
            return API_request_dict

        def get_listResults_dict(API_request_dict: dict) -> list:
            """ This python dictionary is a python dict that contains multiple dicts.  To find where the list_results dict is, the following selections must happen: cat1 dict->searchResults dict->listResults dict"""
            listing_info = []
            for key, value in API_request_dict.items():
                # find the cat1 (category 1) dict
                if key == "cat1":
                    for key, value in value.items():
                        # find the searchResults dict
                        if key == "searchResults":
                            for key, value in value.items():
                                # find the listResults dict
                                if key == "listResults":
                                    for listing in value:
                                         listing_info.append(listing)


        for soup in soup_list:
             API_request_dict = get_API_request_dict(soup)


    apartment_info = []
    soup_list = make_soup_list(response_list)


                                    apartment_info.append(listing)

    apartment_info_json = json.dumps(apartment_info)

with open(
    "C:/Projects/Housing_Price_Prediction/data_processing/raw_bld_url_exts.json",
    "w",
) as f:
    f.write(apartment_info_json)
