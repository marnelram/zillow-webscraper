"""This script processes the raw building information and stores the processed information in a json file."""

import json

# open the building information and store it as bld_info_list
with open("raw-bld-info.json", "r", encoding="utf-8") as f:
    raw_bld_info = f.read()
bld_info = json.loads(raw_bld_info)


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
        superset (dict):
            the superset dict that contains the subset.
        subset (dict):
            the subset dict that is contained by the superset.
        subset_key (str):
            the key of the subset dictionary.
        sub_keys (list):
            a list of subset keys to keep.

    Returns:
        dict:
            A dictionary that includes inherited heys from the subset specified by sub_keys.
    """
    processed_dict = superset.copy()
    processed_subset = filter_dict(subset, sub_keys)
    processed_dict.update(processed_subset)
    if subset_key in processed_dict:
        del processed_dict[subset_key]
    return processed_dict


def split_list_of_subset_dicts(superset: dict, subset_key: str, sub_keys: list) -> list:
    """Extract a list of dictionaries from a list of subset dictionaries with the specified keys.

    Each element of the list contains keys from both the superset dictionary and the corresponding subset dictionary.  The keys from the subset dictionary are specified by the sub_keys list.

    Args:
        superset (dict): the superset dictionary that contains the subset.

        an example of the superset dictionary is shown below:

        "superset": {
            "superset_key_1": "superset_value_1",
            "subset_key": [
                {
                    "subset_dict[0]_key": "subset_dict[0]_value_1".
                    "subset_dict[0]_sub_keys[0]": "subset_dict[0]_sub_keys[0]_value",
                    "subset_dict[0]_sub_keys[1]": "subset_dict[0]_sub_keys[1]_value",
                    ...
                },
                {
                    "subset_dict[1]_key": "subset_dict[0]_alue_1".
                    "subset_dict[1]_sub_keys[0]": "subset_dict[1]_sub_keys[0]_value",
                    ...
                },
            ]
            "superset_key_2": "superset_value_2",
            ...
        }

        subset_key (str): the key in the superset dictionary that maps to a list of subset dictionaries.
        sub_keys (list): list of subset keys to keep.

    Returns:
        list: list of dictionaries that include the inherited keys specified by 'sub_keys'.

        An example of the returned list is shown below:

        [
            "processed_dicts[0]": {
                "superset_key_1": "superset_value_1",

                "superset_key_2": "superset_value_2",

                "subset_dict[0]_sub_keys[0]": "subset_dict[0]_sub_keys[0]_value",

                "subset_dict[0]_sub_keys[1]": "subset_dict[0]_sub_keys[1]_value",
                ...
            }

            "processed_dicts[1]": {
                "superset_key_1": "superset_value_1",

                "superset_key_2": "superset_value_2",

                "subset_dict[1]_sub_keys[0]": "subset_dict[1]_sub_keys[0]_value",

                "subset_dict[1]_sub_keys[1]": "subset_dict[1]_sub_keys[1]_value",
                ...
            }
        ]
    """
    processed_dicts = []
    for subset_dict in superset[subset_key]:
        processed_superset = inherit_subset_dict(
            superset, subset_dict, subset_key, sub_keys
        )
        processed_dicts.append(processed_superset)
    return processed_dicts


def process_address(address: dict) -> dict:
    """returns the address from the address dictionary.

    Concatenates the street address, city, state and zip codes together.
    """
    return (
        address["streetAddress"]
        + " "
        + address["city"]
        + " "
        + address["state"]
        + " "
        + address["zipcode"]
    )


# ***FIX AMENITYSUMMARY WHEN NEW DATA COMES IN


def process_amenitySummary(amenitySummary: dict):
    """Returns the amenity summary from the amenitySummary dictionary.  Concatenates the laundry, parking, and pet policies together.

    The amenitySummary dictionary has the following format:
        "amenitySummary": {
            "laundry": "In Unit",
            "parking": "Garage",
            "petPolicy": ""
        }
    """
    amen_summary = amenitySummary["laundry"]
    return amen_summary


def add_bld_att(bld: dict):
    """returns a processed building dictionary that includes the building attributes from the buildingAttributes dictionary.  This function keeps all keys in the wanted_keys list and discards the rest."""
    # keep these keys from the building attribute dictionary
    keys = [
        "hasSharedLaundry",
        "airConditioning",
        "appliances",
        "parkingTypes",
        "detailedParkingPolicies",
        "outdoorCommonAreas",
        "hasBarbecue",
        "heatingSource",
        "detailedPetPolicy",
        "petPolicies",
        "hasElevator",
        "__typename",
        "communityRooms",
        "sportsCourts",
        "hasBicycleStorage",
        "hasGuestSuite",
        "hasStorage",
        "hasPetPark",
        "hasTwentyFourHourMaintenance",
        "hasDryCleaningDropOff",
        "hasOnlineRentPayment",
        "hasOnlineMaintenancePortal",
        "hasOnsiteManagement",
        "hasPackageService",
        "hasValetTrash",
        "hasSpanishSpeakingStaff",
        "securityTypes",
        "viewType",
        "hasHotTub",
        "hasSauna",
        "hasSwimmingPool",
        "hasAssistedLiving",
        "hasDisabledAccess",
        "floorCoverings",
        "communicationTypes",
        "hasCeilingFan",
        "hasFireplace",
        "hasPatioBalcony",
        "isFurnished",
        "customAmenities",
        "parkingDescription",
        "petPolicyDescription",
        "parkingRentDescription",
        "isSmokeFree",
        "applicationFee",
        "administrativeFee",
        "depositFeeMin",
        "depositFeeMax",
        "leaseTerms",
        "utilitiesIncluded",
        "leaseLengths",
    ]

    # inherit the buildingAttribute dictionary and add it to the building dictionary
    processed_bld_info = inherit_subset_dict(
        bld, bld["buildingAttributes"], "buildingAttributes", keys
    )

    return processed_bld_info


def process_bld_features(bld: dict):
    """returns a processed building dictionary.  When processing the building dictionary, 6 steps are performed:
    1. processes the building address
    2. process the building attributes
    2. processes the amenity summary
    - assignedSchools
    3. processes the walking score
    4. processes the transit score
    5. processes the bike score
    - amenity Details
    - deailed Pet Policy
    """
    processed_bld = bld.copy()
    processed_bld["address"] = process_address(bld["address"])
    processed_bld["walkScore"] = bld["walkScore"]["walkscore"]
    processed_bld["transitScore"] = bld["transitScore"]["transit_score"]
    processed_bld["bikeScore"] = bld["bikeScore"]["bikescore"]
    processed_bld["amenitySummary"] = process_amenitySummary(bld["amenitySummary"])
    # processed_bld_info_dict = add_bld_att(bld_info_dict)

    return processed_bld


def get_plans_from_bld(bld: dict):
    """returns a list of floor plans from the building. each floor plan includes features about the building and the floor plan."""
    floor_plans = []
    plan_keys = [
        "minPrice",
        "maxPrice",
        "units",
        "baths",
        "beds",
        "floorPlanUnitPhotos",
        "name",
        "photos",
        "sqft",
    ]

    # iterate through each floor plan in the 'floorPlans' key
    for floor_plan in bld["floorPlans"]:
        # inherit the floorPlan dict and keep the plan's keys
        processed_floor_plan = inherit_subset_dict(
            bld, floor_plan, "floorPlans", plan_keys
        )

        # apend the result to the floor plans list
        floor_plans.append(processed_floor_plan)

    return floor_plans


def get_units_from_plans(floor_plan: dict):
    """returns a list of units from the floor plan. each unit includes features about the building, floor plan and unit."""
    units = []
    unit_keys = ["unitNumber", "zpid", "availableFrom", "price"]

    for unit in floor_plan["units"]:
        processed_unit = inherit_subset_dict(floor_plan, unit, "units", unit_keys)
        units.append(processed_unit)

    return units


def get_units_from_bld(bld: dict):
    """returns a list of units from the building.  Each unit includes features about the building, floor plan, and unit."""
    units = []

    # get the floor plans from each building
    floor_plans = get_plans_from_bld(bld)

    # get the units from each floor plan
    for floor_plan in floor_plans:
        units.append(get_units_from_plans(floor_plan))
    return units


# maybe make `wanted_floor_plan_keys` a parameter for the function?


def process_bld_info(bld_info: list):
    processed_info = []
    for bld in bld_info:
        processed_bld = process_bld_features(bld)
        units = get_units_from_bld(processed_bld)
        for unit in units:
            processed_info.append(unit)

    return processed_info


processed_info = process_bld_info(bld_info)
print(json.dumps(processed_info, indent=5))
