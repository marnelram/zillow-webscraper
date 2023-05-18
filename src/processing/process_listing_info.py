"""This script processes the raw building information and stores the processed information in a json file.

notes:
    Maybe make `wanted_floor_plan_keys` a parameter for the function?
"""

import json
import src.utils as dict_utils


def run():
    """A function to run the module.  First opens the raw listing information, processes it, then dumps the data as a json format.  In progress, will be updated with the project progresses"""
    listings_info = open_data()
    processed_info = process_listings(listings_info)
    dump_data(processed_info)


def open_data() -> dict:
    """open the building information and store it as bld_info"""
    with open("data/raw/raw_listings_2.json", "r", encoding="utf-8") as f:
        raw_bld_info = f.read()
    listings_info = json.loads(raw_bld_info)
    return listings_info


def process_listings(bld_info: list) -> list:
    """Returns a list of processed listing information.  Each listing includes features about the building, floor plan, and unit."""
    processed_info = []
    for bld in bld_info:
        processed_bld = process_bld_features(bld)
        units = get_units_from_bld(processed_bld)
        for unit in units:
            processed_info.append(unit)
    return processed_info


def dump_data(processed_info: dict):
    """function to dump the data in a json file.  In progress, will be updated as the project progresses"""
    with open("data/interim/listings.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(processed_info))


def process_bld_features(bld: dict) -> dict:
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

    def process_amenitySummary(amenitySummary: dict):
        """Returns the amenity summary from the amenitySummary dictionary.  Concatenates the laundry, parking, and pet policies together.

        Args:
            amenitySummary (dict): the amenity summary dictionary.

        The amenitySummary dictionary has the following format:
            "amenitySummary": {
                "laundry": "In Unit",
                "parking": "Garage",
                "petPolicy": ""
            }
        """
        amen_summary = amenitySummary["laundry"]
        return amen_summary

    def split_bld_att(bld: dict) -> dict:
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
        processed_bld = dict_utils.inherit_subset_dict(
            bld, bld["buildingAttributes"], "buildingAttributes", keys
        )

        return processed_bld

    processed_bld = bld.copy()
    processed_bld["address"] = process_address(bld["address"])
    processed_bld["walkScore"] = bld["walkScore"]["walkscore"]
    processed_bld["transitScore"] = bld["transitScore"]["transit_score"]
    processed_bld["bikeScore"] = bld["bikeScore"]["bikescore"]
    processed_bld["amenitySummary"] = process_amenitySummary(
        bld["amenitySummary"]
    )
    return processed_bld


def get_plans_from_bld(bld: dict):
    """Returns a list of floor plans from the building. Each floor plan includes features about the building and the floor plan.

    Used as a part of the get_units_from_bld function.  This function is used to process the floor plans from the building dictionary.  The floor plans are then used to process the units from the building dictionary.  The floor plans are processed by inheriting the building dictionary and adding the floor plan dictionary to the building dictionary.  The floor plan dictionary is then added to the floor plans list.

    Exceptions:
        - some buildings do not have floor plans.  This causes a TypeError when trying to access the floor plans from the building dictionary.  This issue is handled by using a try/except block to catch the TypeError and pass it.
    """
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
    # check if the building has floor plans
    try:
        for floor_plan in bld["floorPlans"]:
            processed_floor_plan = dict_utils.inherit_subset_dict(
                bld, floor_plan, "floorPlans", plan_keys
            )
            floor_plans.append(processed_floor_plan)
    # if the building does not have floor plans then don't add it to the floor_plans
    except TypeError as e:
        pass
    return floor_plans


def get_units_from_plan(floor_plan: dict):
    """returns a list of units from the floor plan. each unit includes features about the building, floor plan and unit.

    Used as a part of the get_units_from_bld function.  This function is used to process the units from the floor plan dictionary.  The units are processed by inheriting the floor plan dictionary and adding the unit dictionary to the floor plan dictionary.  The unit dictionary is then added to the units list.

    Exceptions:
        - some floor plans do not have units.  This causes a TypeError when trying to access the units from the floor plan dictionary.  This issue is handled by using a try/except block to catch the TypeError and pass it.
    """
    units = []
    unit_keys = ["unitNumber", "zpid", "availableFrom", "price"]

    # check if the floor plan has units
    try:
        for unit in floor_plan["units"]:
            processed_unit = dict_utils.inherit_subset_dict(
                floor_plan, unit, "units", unit_keys
            )
            del processed_unit["minPrice"]
            del processed_unit["maxPrice"]
            units.append(processed_unit)
    # if the floor plan does not have units, then delete the "units" key, set the price of the floor plan, and add the floor plan to the units list
    except TypeError as e:
        del floor_plan["units"]
        floor_plan["price"] = floor_plan["minPrice"]
        del floor_plan["minPrice"]
        del floor_plan["maxPrice"]
        units.append(floor_plan)
    return units


def get_units_from_bld(bld: dict) -> list:
    """returns a list of units from the building.  Each unit includes features about the building, floor plan, and unit."""

    units = []
    floor_plans = get_plans_from_bld(bld)
    for floor_plan in floor_plans:
        floor_units = get_units_from_plan(floor_plan)
        for unit in floor_units:
            units.append(unit)
    return units


def print_floor_plans(listing_info):
    for listing in listing_info:
        print(json.dumps(listing["floorPlans"], indent=4))


if __name__ == "__main__":
    run()
