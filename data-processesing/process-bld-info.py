"""This file takes as input the raw building information from the raw_bld_info.json file and outputs a dataframe object to use in analysis.  processes it to remove unnecessary keys.  Currently it parses the following keys from the :
1. address
2. floorPlans
3. buildingAttributes
4. amenitySummary
5. assignedSchools
6. walkScore
7. transitScore
8. bikeScore
9. amenityDetails
10. detailedPetPolicy
"""
import json

# open the building information and store it as bld_info_list
with open(
    "C:/Projects/Housing_Price_Prediction/data_processing/raw_bld_info.json", "r"
) as f:
    raw_bld_info = f.read()
bld_info = json.loads(raw_bld_info)


def filter_dict(source_dict: dict, keys: list):
    """returns a processed dictionary that only has the source dictionary keys from the keys list."""
    processed_dict = {}

    # add the specified keys to the processed dictionary
    for key, value in source_dict.items():
        if key in keys:
            processed_dict.update({key: value})

    return processed_dict


def inherit_subset_dict(superset: dict, subset: dict, subset_key: str, sub_keys: list):
    """returns a processed dictionary after inheriting the information from the subset dictionary. The subset keeps the keys in the sub_key list before being inherited by the supsert dictionary."""
    # copy the source dictionary
    processed_dict = superset.copy()

    # keep the wanted keys in the subset
    processed_subset = filter_dict(subset, sub_keys)

    # add the processed subset to the superset
    processed_dict.update(processed_subset)

    # delete the subset
    if subset_key in processed_dict.keys():
        del processed_dict[subset_key]

    return processed_dict


def split_list_of_dicts(superset: dict, subset_key: str, sub_keys: list):
    """Extracts a list of dictionaries from the list of subset dictionaries.  Each element of the list contains keys from both the superset dictionary and the corresponding subset dictionary."""
    superset_dicts = []

    # iterate through each element in the list of values of the subset key
    for subset_dict in superset[subset_key]:
        # inherit the subset dictionary keys into the processed superset dictionary
        processed_superset = inherit_subset_dict(
            superset, subset_dict, subset_key, sub_keys
        )

        # append the result to the superset dictionary list
        superset_dicts.append(processed_superset)

    return superset_dicts


def extract_subset_dicts(source_dict: dict, subset_key: str, sub_keys: list):
    """Extracts a list of dictionaries from a source dictionary using a specified subset key and list of sub keys."""
    subset_dicts = []
    for subset_dict in source_dict[subset_key]:
        processed_dict = inherit_subset_dict(
            source_dict, subset_dict, subset_key, sub_keys
        )
        subset_dicts.append(processed_dict)
    return subset_dicts


def process_address(address: dict):
    """returns the address from the address dictionary.  Concatenates the street address, city, state and zip codes together."""
    add = (
        address["streetAddress"]
        + " "
        + address["city"]
        + " "
        + address["state"]
        + " "
        + address["zipcode"]
    )
    return add


# ***FIX AMENITYSUMMARY WHEN NEW DATA COMES IN


def process_amenitySummary(amenitySummary: dict):
    """processes the amenities of the amenitySummary dictionary.  Currently there are 3 keys in this dictionary: building, __typename, and laundry.  Check later if there are other keys when parsing more listings"""
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
    # make a copy of the building dictionary
    processed_bld = bld.copy()

    # process the address key
    processed_bld["address"] = process_address(bld["address"])

    # get the building's walking score from the walkScore key
    processed_bld["walkScore"] = bld["walkScore"]["walkscore"]

    # get the building's transit score from the transitScore key
    processed_bld["transitScore"] = bld["transitScore"]["transit_score"]

    # get the building's bike score from the bikeScore key
    processed_bld["bikeScore"] = bld["bikeScore"]["bikescore"]

    # process the amenitySummary key
    processed_bld["amenitySummary"] = process_amenitySummary(bld["amenitySummary"])

    # split the building attributes from the buildingAttributes key
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

    # iterate through each unit in the 'units' key
    for unit in floor_plan["units"]:
        # inherit the unit dict and keep the unit's keys
        processed_unit = inherit_subset_dict(floor_plan, unit, "units", unit_keys)

        # append the result to the units list
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


"""
def clean_floorPlans(building_info_dict):
    '''Processes the building dictionary into multiple apartment unit dictionaries.
    Creates a list of apartment units for each unit in each plan of the different floor plans.
    Returns a list of apartment dictionaries unit information of each apartment.  Each index contains different floor plan attributes, but the same building information
    '''

    wanted_building_keys = ['buildingName', 'latitude', 'longitude', 'lotId', 'address', 'zipcode', 'isLandlordLiaisonProgram', 'buildingType', 'listingFeatureType', 'photoCount', 'videos', 'buildingAttributes', 'amenitySummary',
                            'isLowIncome', 'isSeniorHousing', 'isStudentHousing', 'screeningCriteria', 'assignedSchools', 'nearbyAmenities', 'walkScore', 'transitScore', 'bikeScore', 'description', 'amenityDetails', 'detailedPetPolicy']
    procesed_building_info_dict = keep_keys(
        building_info_dict, wanted_building_keys)

    apt_info_list = []
    # iterate through each floor plan (dictionary) in the building's floor plan list
    for floor_plan_dict in building_info_dict['floorPlans']:

        # append the wanted floor plan attributes (keys) to the processed_floor_plan_dict
        wanted_floor_plan_keys = [
            'baths', 'beds', 'floorPlanUnitPhotos', 'name', 'photos', 'sqft', 'description']
        processed_floor_plan_dict = keep_keys(
            floor_plan_dict, wanted_floor_plan_keys)

        # iterate through the key, value pairs in the floor plan dictionary
        for key, value in floor_plan_dict.items():

            # check if the key is the 'units' key
            if key == 'units':
                units_list = value

                # iterate through each unit in the units list of each floor plan of each building
                for unit_dict in units_list:

                    # append the wanted unit attributes (keys) to the processed_unit_dict
                    wanted_unit_keys = [
                        'unitNumber', 'zpid', 'availableFrom', 'hasApprovedThirdPartyVirtualTour', 'price']
                    processed_unit_dict = keep_keys(
                        unit_dict, wanted_unit_keys)

                    # make a new dict (row) to store the building, floor plan and the unit attributes
                    apt_info_dict = {}

                    # add the building attributes to the apt dict
                    apt_info_dict.update(procesed_building_info_dict)

                    # add the floor plan info to the apt dict
                    apt_info_dict.update(processed_floor_plan_dict)

                    # add the unit info to the apt dict
                    apt_info_dict.update(processed_unit_dict)

                    # append the apt_info_dict to the apt_info_list
                    apt_info_list.append(apt_info_dict)

    # return the apartment info list
    return apt_info_list
"""


def process_bld_info(bld_info: list):
    processed_info = []
    # iterate through each building dictionary and processes the data
    for bld in bld_info:
        # process the building related features
        processed_bld = process_bld_features(bld)

        # get a list of units from the building
        units = get_units_from_bld(processed_bld)

        # append each unit to the information list
        for unit in units:
            processed_info.append(unit)

    return processed_info


processed_info = process_bld_info(bld_info)
print(json.dumps(processed_info, indent=5))
