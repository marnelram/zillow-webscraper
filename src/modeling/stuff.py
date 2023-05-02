from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Define the search bounds
west = -122.465159
east = -122.224433
south = 47.491912
north = 47.734145

# Define the geolocator object
geolocator = Nominatim(user_agent="my_app")

# Get the coordinates of the search bounds
nw = (north, west)
ne = (north, east)
sw = (south, west)
se = (south, east)

# Get the zip codes for each coordinate
nw_zip = geolocator.reverse(nw).raw["address"]["postcode"]
ne_zip = geolocator.reverse(ne).raw["address"]["postcode"]
sw_zip = geolocator.reverse(sw).raw["address"]["postcode"]
se_zip = geolocator.reverse(se).raw["address"]["postcode"]

# Print the zip codes
print("Zip codes for the search bounds:")
print(f"NW: {nw_zip}")
print(f"NE: {ne_zip}")
print(f"SW: {sw_zip}")
print(f"SE: {se_zip}")
