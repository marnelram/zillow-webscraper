"""A module with all of the information to make a ZillowScraper object. This object will be used to scrape each listing on the Zillow.com for the information we want to collect.

This module is a work in progress and will be updated as the project progresses.
"""
import pandas as pd
import urllib.parse

import web_scraping.scrape_search_info as scrape_search_info
import web_scraping.scrape_listings as scrape_listings

import processing.process_search_info as process_search_info
import processing.process_listing_info as process_listings_info


class ZillowScraper:
    """A class to represent a ZillowScraper object.

    This object will be used to scrape each listing on the Zillow.com for the information.

    This class is a work in progress and will be updated as the project progresses.

    Attributes:
        search_url (str): The url to search for apartments on Zillow.com
        num_pages (int): The number of pages to scrape. Cannot exceed the maximum number of pages for the search query.
    """

    def __init__(self, search_url: str, num_pages=1):
        """The constructor for the ZillowScraper class.

        Args:
            search_url (str): The url to search for apartments on Zillow.com.
            num_pages (int, optional): The number of pages to scrape. Cannot exceed the maximum number of pages for the search query.  Defaults to 1.
        """
        self.searh_url = search_url
        self.num_pages = num_pages

    def parse_search_url(self, search_url: str):
        """A function to parse the search url into parameters.

        Args:
            search_url (str): The url to search for apartments on Zillow.com.

        Returns:
            search_parameters (dict): A dictionary of the search parameters.
        """

        # split the url into the base url and the query string
        base_url, search_url = search_url.split("?")
        # parse the search url into parameters
        search_parameters = urllib.parse.parse_qs(
            urllib.parse.urlparse(search_url).query
        )
        return search_parameters

    def scrape(self):
        """A function to scrape the search url for the apartment listings, then scrape listings for more detailed information.

        The scraping process happens in two steps:
            1. Scrape the search url for the listing url extensions (ex. /seattle-wa/arthouse/5Yy9f4/").
            2. Scrape each listing using the url extensions.

        Returns:
            listing_information (csv): A csv file with the listing information.
        """
        scrape_search_info.scrape()

        scrape_search_info.parse()
