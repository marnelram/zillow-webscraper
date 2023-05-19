""" A module to process the search information scraped from the Zillow search pages.

This module contains functions to process the search information scraped from the Zillow search pages. The search information is loaded from a json file, processed, and then dumped into a json file.

Example:
    To run the module, import it and call the run function.
        $ import process_search_info
        $ process_search_info.run()
"""
import json


def run():
    """A function to run the process_search_info module."""
    search_info = load_search_info()
    url_exts = process_listing_url_ext(search_info)
    dump_url_exts(url_exts)


def load_search_info():
    """A function to load the information scraped from each Zillow search page.

    Returns:
        search_info (dict): A dictionary containing information from the search pages scraped.
    """
    with open(
        "C:/python-projects/zillow_webscraper/issues/zillow-webscraper/data/raw_v2/raw_search_info_2",
        "r",
    ) as f:
        search_info_str = f.read()
    search_info = json.loads(search_info_str)
    return search_info


def process_listing_url_ext(search_info: list) -> list:
    """A function to process the search page information into a list of urls extensions.

    Args:
        search_info (list): A list of search_info dictionaries containing all the information from the search pages.

    Returns:
        processed_listing_url_exts (list): A list of the processed listing urls.
    """

    def get_url_ext(listing: dict) -> str:
        """A function to get the url extensions from the search_info dictionary.

        Args:
            search_info (dict): A dictionary containing all the information from the search pages.

        Returns:
            detail_url (str): the url for the building page to query from.

        Exceptions:
            TypeError: If the listing is not a dictionary, then the function will be skipped over.
        """
        try:
            for key, value in listing.items():
                if key == "detailUrl":
                    return value
        except AttributeError as e:
            pass

    def filter_urls(urls: list) -> list:
        """A function to filter the listing urls extensions to only include the url extensions that have a building key.

        Args:
            urls (list): A list of the urls from the search information.

        Returns:
            processed_urls (list): A list of the filtered urls.
        """
        processed_urls = []
        for url in urls:
            if "https" not in url:
                processed_urls.append(url)
        return processed_urls

    url_exts = []
    for page in search_info:
        if page is not None:
            for listing in page:
                url_exts.append(get_url_ext(listing))
    processed_url_exts = filter_urls(url_exts)
    return processed_url_exts


def dump_url_exts(url_exts):
    """A function to dump the processed urls into a json file.

    Args:
        processed_urls (list): A list of the processed urls.
    """
    with open(
        "C:/python-projects/zillow_webscraper/issues/zillow-webscraper/data/raw_v2/url_exts_2.json",
        "w",
    ) as f:
        f.write(json.dumps(url_exts))


if __name__ == "__main__":
    run()
