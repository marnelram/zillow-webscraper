"""This script processes the raw building information and stores the processed information in a json file."""

import json

# open the building information and store it as bld_info_list
with open("raw-bld-info.json", "r", encoding="utf-8") as f:
    raw_bld_info = f.read()
bld_info = json.loads(raw_bld_info)


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
    processed_bld["amenitySummary"] = process_amenitySummary(
        bld["amenitySummary"]
    )
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
        processed_unit = inherit_subset_dict(
            floor_plan, unit, "units", unit_keys
        )
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
