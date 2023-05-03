"""This module contains a list of utility functions for processing dictionaries."""


def filter_dict(source_dict: dict, filter_keys: list) -> dict:
    """filters a dictionary and removes keys not in the filter keys list."""
    processed_dict = {}
    for key, value in source_dict.items():
        if key in filter_keys:
            processed_dict[key] = value
    return processed_dict


def inherit_subset_dict(
    superset: dict, subset: dict, subset_key: str, sub_keys: list
) -> dict:
    """Inherit the keys from the subset in the key list into the superset.

    Args:
        superset (dict): the superset dict that contains the subset.
        subset (dict): the subset dict that is contained by the superset.
        subset_key (str): the key of the subset dictionary.
        sub_keys (list): a list of subset keys to keep.

    Returns:
        dict: A dictionary that includes inherited heys from the subset specified by sub_keys.
    """
    processed_dict = superset.copy()
    processed_subset = filter_dict(subset, sub_keys)
    processed_dict.update(processed_subset)
    if subset_key in processed_dict:
        del processed_dict[subset_key]
    return processed_dict


def split_list_of_subset_dicts(
    superset: dict, subset_key: str, sub_keys: list
) -> list:
    """Extract a list of dictionaries from a list of subset dictionaries with the specified keys.

    Each element of the list contains keys from both the superset dictionary and the corresponding subset dictionary.  The keys from the subset dictionary are specified by the sub_keys list.

    Args:
        superset (dict): the superset dictionary that contains the subset.
        subset_key (str): the key in the superset dictionary that maps to a list of subset dictionaries.
        sub_keys (list): list of subset keys to keep.

    Returns:
        list: list of dictionaries that include the inherited keys specified by 'sub_keys'.

    Examples:
        >>> bld = { 'name': 'The Park at Irvine Spectrum Center', 'floorPlans': [floorPlan1, floorPlan2, ...]}
        >>> processed_dict = split_list_of_subset_dicts(bld, 'floorPlans', ['name', 'bedrooms', 'bathrooms', 'minPrice', 'maxPrice', 'minSquareFeet', 'maxSquareFeet'])
        >>> print(processed_dicts[0])
        { 'name': 'The Park at Irvine Spectrum Center', 'bedrooms': 1, 'bathrooms': 1, 'minPrice': 2, 'maxPrice': 2, 'minSquareFeet': 2, 'maxSquareFeet': 2 }
    """
    processed_dicts = []
    for subset_dict in superset[subset_key]:
        processed_superset = inherit_subset_dict(
            superset, subset_dict, subset_key, sub_keys
        )
        processed_dicts.append(processed_superset)
    return processed_dicts
