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

# defines functions to process each key (column) of each building dictionary (row)


def process_address(address_dict):
    '''fixes the address of the address dictionary of each building dictionary
    '''
    try:
        address = ""
        for key, value in address_dict.items():
            if key != '__typename' and key != 'neighborhood':
                address = address + value + " "
        return address[0:-2]
    except AttributeError as e:
        print("building address is the wrong format or is already parsed")

# fix:


def process_amenitySummary(amenitySummary_dict):
    '''fixes the amenities of the amenitySummary dictionary of each building dictionary.  Currently there are 3 keys in this dictionary: building, __typename, and laundry.  Check later if there are other keys when parsing more listings
    '''
    for key, value in amenitySummary_dict.items():
        # **CHECK IN THE FUTURE IF THERE ARE MORE BUILDING AMENITIES
        if key == 'laundry':
            amenitySummary = value
    return amenitySummary


def process_walkingScore(walkingScore_dict):
    return None


def process_transitScore(transitScore_dict):
    return None


def process_bikeScore(bikeScore_dict):
    return None


def process_bld_keys(bld_info_dict):

    # process the bld_info_dict
    processed_bld_info_dict = {}

    # process the adress key
    processed_bld_info_dict['address'] = process_address(
        bld_info_dict['address'])

    # process the amenitySummary key
    processed_bld_info_dict['amenitySummary'] = process_amenitySummary(
        bld_info_dict['amenitySummary'])

    """
    # process the walkingScore key
    processed_bld_info_dict['walkingScore'] = process_walkingScore(
        bld_info_dict['walkingScore'])

    # process the transitScore key
    processed_bld_info_dict['transitScore'] = process_transitScore(
        bld_info_dict['transitScore'])

    # process the bikeScore key
    processed_bld_info_dict['bikeScore'] = process_bikeScore(
        bld_info_dict['bikeScore'])
    """

    return processed_bld_info_dict


processed_apt_info_list = []


def process_apt_info_dict(bld_info_dict):
    '''returns a processed apartment dictionary with information about the building, floor plan, and specific unit of the apartment. processes the building dictionary in 3 steps:
    1. process all of the building related keys
    2. splits the floor plans from each building
    3. splits the units from each floor plan
    '''
    # process building keys
    processed_bld_info_dict = process_bld_keys(bld_info_dict)

    # split the floor plans from each building
    # floor_plans_info_list = split_floorPlans(bld_info_dict)

    # append the new apartment dictionaries created by the clean_floorPlans() function to the apt_info_list
    # apt_info_list = clean_floorPlans(processed_bld_info_dict)
    # for apt in apt_info_list:
    # processed_apt_info_list.append(apt)

# maybe make `wanted_floor_plan_keys` a parameter for the function?


def split_floorPlans(building_info_dict):
    '''returns a list of dictionaries containing extra information about the different floor plans from the building dictionary.
    '''
    floor_plan_list = []
    wanted_floor_plan_keys = ['units', 'baths', 'beds',
                              'floorPlanUnitPhotos', 'name', 'photos', 'sqft', 'description']
    # append the wanted floor plan attributes (keys) to the processed_floor_plan_dict
    for floor_plan_dict in building_info_dict['floorPlans']:

        # keep wanted keys in the floor plan dictionary
        processed_floor_plan_dict = keep_keys(
            floor_plan_dict, wanted_floor_plan_keys)

        # delete the floorPlans key and add the rest of the building keys
        del building_info_dict['floorPlans']
        processed_floor_plan_dict.update(building_info_dict)

        # append the processed floor plan to the floor plan list
        floor_plan_list.append(processed_floor_plan_dict)

    return floor_plan_list


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

for bld_info_dict in bld_info_list:
    apt_info_dict = process_apt_info_dict(bld_info_dict)
