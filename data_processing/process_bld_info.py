import json

'''This file takes as input the building info list from the bld_info.json file and processes it to remove unnecessary keys.  Currently it parses the following keys from the :
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
'''

# open the building information and store it as bld_info_list
with open('C:/Projects/Housing_Price_Prediction/data_processing/raw_bld_info.json', 'r') as f:
    raw_bld_info_list = f.read()
bld_info_list = json.loads(raw_bld_info_list)


def keep_keys(dict: dict, wanted_keys: list):
    '''utility function to remove unwanted keys.  Takes a dict and a list of wanted keys as input and returns the processed dict'''
    processed_dict = {}
    for key, value in dict.items():
        if key in wanted_keys:
            processed_dict.update({key: value})
    return processed_dict


def inherit_subset_dict(superset: dict, subset: dict, subset_key: str, sub_keys: list):
    '''utility function that returns the superset dictionary after inheriting the information from the subset dictionary. The subset keeps the keys in the key list before being inherited by the supsert dictionary.
    '''
    # keep the wanted keys in the subset
    processed_subset = keep_keys(
        subset, sub_keys)

    # add the processed subset to the superset
    superset.update(processed_subset)

    # delete the subset
    if subset_key in superset.keys():
        del superset[subset_key]

    return superset


def process_address(address: dict):
    '''returns the address from the address dictionary.  Concatenates the street address, city, state and zip codes together.
    '''
    add = address['streetAddress'] + " " + address['city'] + \
        " " + address['state'] + " " + address['zipcode']
    return add

# ***FIX AMENITYSUMMARY WHEN NEW DATA COMES IN


def process_amenitySummary(amenitySummary: dict):
    '''processes the amenities of the amenitySummary dictionary.  Currently there are 3 keys in this dictionary: building, __typename, and laundry.  Check later if there are other keys when parsing more listings
    '''
    amen_summary = amenitySummary['laundry']
    return amen_summary


def add_bld_att(bld_info: dict):
    '''returns a processed building dictionary that includes the building attributes from the buildingAttributes dictionary.  This function keeps all keys in the wanted_keys list and discards the rest.
    '''
    # keep these keys from the building attribute dictionary
    keys = ['hasSharedLaundry', 'airConditioning', 'appliances', 'parkingTypes', 'detailedParkingPolicies', 'outdoorCommonAreas', 'hasBarbecue', 'heatingSource', 'detailedPetPolicy', 'petPolicies', 'hasElevator', '__typename', 'communityRooms', 'sportsCourts', 'hasBicycleStorage', 'hasGuestSuite', 'hasStorage', 'hasPetPark', 'hasTwentyFourHourMaintenance', 'hasDryCleaningDropOff', 'hasOnlineRentPayment', 'hasOnlineMaintenancePortal', 'hasOnsiteManagement', 'hasPackageService',
            'hasValetTrash', 'hasSpanishSpeakingStaff', 'securityTypes', 'viewType', 'hasHotTub', 'hasSauna', 'hasSwimmingPool', 'hasAssistedLiving', 'hasDisabledAccess', 'floorCoverings', 'communicationTypes', 'hasCeilingFan', 'hasFireplace', 'hasPatioBalcony', 'isFurnished', 'customAmenities', 'parkingDescription', 'petPolicyDescription', 'parkingRentDescription', 'isSmokeFree', 'applicationFee', 'administrativeFee', 'depositFeeMin', 'depositFeeMax', 'leaseTerms', 'utilitiesIncluded', 'leaseLengths'
            ]

    # inherit the buildingAttribute dictionary and add it to the building dictionary
    processed_bld_info = inherit_subset_dict(
        bld_info, bld_info['buildingAttributes'], 'buildingAttributes', keys)

    return processed_bld_info


def process_bld_info(bld_info: dict):
    '''returns a processed building dictionary.  When processing the building dictionary, 6 steps are performed:
    1. processes the building address
    2. process the building attributes
    2. processes the amenity summary
    - assignedSchools
    3. processes the walking score
    4. processes the transit score
    5. processes the bike score
    - amenity Details
    - deailed Pet Policy
    '''
    # process the bld_info_dict
    processed_bld_info = bld_info

    # process the address key
    processed_bld_info['address'] = process_address(
        bld_info['address'])

    # get the building's walking score from the walkScore key
    processed_bld_info['walkScore'] = bld_info['walkScore']['walkscore']

    # get the building's transit score from the transitScore key
    processed_bld_info['transitScore'] = bld_info['transitScore']['transit_score']

    # get the building's bike score from the bikeScore key
    processed_bld_info['bikeScore'] = bld_info['bikeScore']['bikescore']

    # process the amenitySummary key
    processed_bld_info['amenitySummary'] = process_amenitySummary(
        bld_info['amenitySummary'])

    # split the building attributes from the buildingAttributes key
    # processed_bld_info_dict = add_bld_att(bld_info_dict)

    return processed_bld_info


def split_floor_plans(bld_info: dict):
    '''returns a list of processed building dictionies that includes the different floor plans from the floorPlan dictionary.  This function keeps all keys in the wanted_keys list and discards the rest.
    '''
    processed_floor_plan = []
    wanted_keys = ['minPrice', 'maxPrice', 'units', 'baths', 'beds',
                   'floorPlanUnitPhotos', 'name', 'photos', 'sqft', 'description']

    # iterate through each floor plan in the 'floorPlans' key
    for floor_plan in bld_info['floorPlans']:

        # combine the floorPlan_dict
        processed_floorPlans = comb_subset_dict(
            floor_plan, bld_info, 'floorPlans', wanted_keys)

        # apend the result to the processed_floor_plans_list
        processed_floor_plan.append(processed_floorPlans)

    return processed_floor_plan


def get_unit_info_list(bld_info: dict):
    '''returns a list of apartment dictionies with information about the building, floor plan, and specific unit of the apartment for each floor plan and unit in the building dictionary. processes the building dictionary in 2 steps:
    1. splits the floor plans from each building
    2. splits the units from each floor plan
    '''
    # split the floor plans from each building
    floor_plans_info = split_floor_plans(bld_info)

    # append the new apartment dictionaries created by the clean_floorPlans() function to the apt_info_list
    # apt_info_list = clean_floorPlans(processed_bld_info_dict)
    # for apt in apt_info_list:
    # processed_apt_info_list.append(apt)
    return floor_plans_info

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
# TEST


processed_info_list = []
processed_bld_info_list = []

# iterate through each building dictionary and processes the data
for bld_info_dict in bld_info_list:

    # process the building related keys
    processed_bld_info_dict = process_bld_info(bld_info_dict)

    # test
    processed_bld_info_list.append(processed_bld_info_dict)

    # gets the information for each unit in the building (bld_info_dict)
    # unit_info_list = get_unit_info_list(processed_bld_info_dict)
    # for unit_info_dict in unit_info_list:
    # processed_info_list.append(unit_info_dict)

print(json.dumps(processed_bld_info_list[0], indent=5))
