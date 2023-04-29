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


def keep_keys(dict, wanted_keys_list):
    '''utility function to remove unwanted keys.  Takes a dict and a list of wanted keys as input and returns the processed dict'''
    processed_dict = {}
    for key, value in dict.items():
        if key in wanted_keys_list:
            processed_dict.update({key: value})
    return processed_dict

# **working on changes


def comb_subset_dict(subset_dict, superset_dict, subset_key, wanted_keys, del_subset):
    '''utility function that combines the subset and superset dicts together and keeps the wanted keys in the subset
    '''

    processed_subset_dict = keep_keys(
        subset_dict, wanted_keys)

    # add the subset dictionary to the superset dictionary
    superset_dict.update(processed_subset_dict)

    # if the subset needs to be deleted, then delete the subset dictionary
    if del_subset:
        if subset_key in superset_dict.keys():
            del superset_dict[subset_key]

    return superset_dict
# defines functions to process each key (column) of each building dictionary (row)


def process_address(address_dict):
    '''returns the address from the address dictionary.  Concatenates the street address, city, state and zip codes together.
    '''
    address = ""
    wanted_keys = ['streetAddress', 'city', 'state', 'zipcode']
    processed_address_dict = keep_keys(address_dict, wanted_keys)
    for key, value in processed_address_dict.items():
        address = address + value + " "
    return address[0:-1]

# ***FIX AMENITYSUMMARY WHEN NEW DATA COMES IN


def process_amenitySummary(amenitySummary_dict):
    '''processes the amenities of the amenitySummary dictionary.  Currently there are 3 keys in this dictionary: building, __typename, and laundry.  Check later if there are other keys when parsing more listings
    '''
    amenitySummary = None
    for key, value in amenitySummary_dict.items():
        # **CHECK IN THE FUTURE IF THERE ARE MORE BUILDING AMENITIES
        if key == 'laundry':
            amenitySummary = value
    return amenitySummary


def process_walkScore(walkScore_dict):
    '''returns the walk score from the walk score dictionary.'''
    walk_score = None
    for key, value in walkScore_dict.items():
        if key == 'walkscore':
            walk_score = value
    return walk_score


def process_transitScore(transitScore_dict):
    '''returns the transit score from the transit score dictionary.'''
    transit_score = None
    for key, value in transitScore_dict.items():
        if key == 'transit_score':
            transit_score = value
    return transit_score


def process_bikeScore(bikeScore_dict):
    '''returns the bike score from the bike score dictionary.'''
    bike_score = None
    for key, value in bikeScore_dict.items():
        if key == 'bikescore':
            bike_score = value
    return bike_score


def add_bld_att(bld_info_dict):
    '''returns a processed building dictionary that includes the building attributes from the buildingAttributes dictionary.  This function keeps all keys in the wanted_keys list and discards the rest.
    '''
    # remove unwanted keys
    wanted_keys = ['hasSharedLaundry', 'airConditioning', 'appliances', 'parkingTypes', 'detailedParkingPolicies', 'outdoorCommonAreas', 'hasBarbecue', 'heatingSource', 'detailedPetPolicy', 'petPolicies', 'hasElevator', '__typename', 'communityRooms', 'sportsCourts', 'hasBicycleStorage', 'hasGuestSuite', 'hasStorage', 'hasPetPark', 'hasTwentyFourHourMaintenance', 'hasDryCleaningDropOff', 'hasOnlineRentPayment', 'hasOnlineMaintenancePortal', 'hasOnsiteManagement', 'hasPackageService',
                   'hasValetTrash', 'hasSpanishSpeakingStaff', 'securityTypes', 'viewType', 'hasHotTub', 'hasSauna', 'hasSwimmingPool', 'hasAssistedLiving', 'hasDisabledAccess', 'floorCoverings', 'communicationTypes', 'hasCeilingFan', 'hasFireplace', 'hasPatioBalcony', 'isFurnished', 'customAmenities', 'parkingDescription', 'petPolicyDescription', 'parkingRentDescription', 'isSmokeFree', 'applicationFee', 'administrativeFee', 'depositFeeMin', 'depositFeeMax', 'leaseTerms', 'utilitiesIncluded', 'leaseLengths'
                   ]

    # combine the buildingAttribute dictionary with the building dictionary
    processed_bld_info_dict = comb_subset_dict(bld_info_dict['buildingAttributes'],
                                               bld_info_dict, 'buildingAttributes', wanted_keys, del_subset=True)

    return processed_bld_info_dict


def process_bld_info(bld_info_dict):
    '''returns a processed building dictionary.  When processing the building dictionary, 6 steps are performed:
    1. processes the building address
    - floorPlans
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
    processed_bld_info_dict = bld_info_dict

    # process the address key
    processed_bld_info_dict['address'] = process_address(
        bld_info_dict['address'])

    # process the walkingScore key
    processed_bld_info_dict['walkScore'] = process_walkScore(
        bld_info_dict['walkScore'])

    # process the transitScore key
    processed_bld_info_dict['transitScore'] = process_transitScore(
        bld_info_dict['transitScore'])

    # process the bikeScore key
    processed_bld_info_dict['bikeScore'] = process_bikeScore(
        bld_info_dict['bikeScore'])

    # process the amenitySummary key
    processed_bld_info_dict['amenitySummary'] = process_amenitySummary(
        bld_info_dict['amenitySummary'])

    # split the building attributes from the buildingAttributes key
    # processed_bld_info_dict = add_bld_att(bld_info_dict)

    return processed_bld_info_dict

# working on changes


def split_floor_plans(bld_info_dict):
    '''returns a list of processed building dictionies that includes the different floor plans from the floorPlan dictionary.  This function keeps all keys in the wanted_keys list and discards the rest.
    '''
    processed_floor_plan_list = []
    wanted_keys = ['minPrice', 'maxPrice', 'units', 'baths', 'beds',
                   'floorPlanUnitPhotos', 'name', 'photos', 'sqft', 'description']

    # iterate through each floor plan in the 'floorPlans' key
    for floorPlan_dict in bld_info_dict['floorPlans']:

        # combine the floorPlan_dict with the bld_info_dict
        processed_floorPlans_dict = comb_subset_dict(
            floorPlan_dict, bld_info_dict, 'floorPlans', wanted_keys, del_subset=False)

        # apend the result to the processed_floor_plans_list
        processed_floor_plan_list.append(processed_floorPlans_dict)

    return processed_floor_plan_list


def get_unit_info_list(bld_info_dict):
    '''returns a list of apartment dictionies with information about the building, floor plan, and specific unit of the apartment for each floor plan and unit in the building dictionary. processes the building dictionary in 2 steps:
    1. splits the floor plans from each building
    2. splits the units from each floor plan
    '''
    # split the floor plans from each building
    floor_plans_info_list = split_floor_plans(bld_info_dict)

    # append the new apartment dictionaries created by the clean_floorPlans() function to the apt_info_list
    # apt_info_list = clean_floorPlans(processed_bld_info_dict)
    # for apt in apt_info_list:
    # processed_apt_info_list.append(apt)
    return floor_plans_info_list

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

# iterate through each building dictionary and processes the data
for bld_info_dict in bld_info_list:

    # process the building related keys
    processed_bld_info_dict = process_bld_info(bld_info_dict)

    # gets the information for each unit in the building (bld_info_dict)
    unit_info_list = get_unit_info_list(processed_bld_info_dict)
    for unit_info_dict in unit_info_list:
        processed_info_list.append(unit_info_dict)
