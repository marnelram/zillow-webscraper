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
    with open("data.search_info.json", "r") as f:
        search_info_str = f.read()
    search_info = json.loads(search_info_str)
    return search_info


def process_listing_url_ext(search_info):
    """A function to process the search page information into a list of urls extensions.

    Args:
        search_info (dict): A dictionary containing all the information from the search pages.

    Returns:
        processed_listing_url_exts (list): A list of the processed listing urls.
    """

    def get_urls_exts(search_info):
        """A function to get the url extensions from the search_info dictionary.

        Args:
            search_info (dict): A dictionary containing all the information from the search pages.

        Returns:
            urls (list): A list of the urls from the search_info dictonary.
        """
        url_exts = []
        for listing in search_info:
            for key, value in listing.items():
                if key == "detailUrl":
                    url_exts.append(value)
        return url_exts

    def filter_urls(urls):
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

    url_exts = get_urls_exts(search_info)
    processed_url_exts = filter_urls(url_exts)
    return processed_url_exts


def dump_url_exts(url_exts):
    """A function to dump the processed urls into a json file.

    Args:
        processed_urls (list): A list of the processed urls.
    """
    with open("data.url_exts.json", "w") as f:
        f.write(json.dumps(url_exts))
