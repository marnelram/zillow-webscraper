import urllib.parse
import json

'''
print(urllib.parse.unquote(
    '%7B%22pagination%22%3A%7B%7D%2C%22mapBounds%22%3A%7B%22north%22%3A47.734145%2C%22east%22%3A-122.224433%2C%22south%22%3A47.491912%2C%22west%22%3A-122.465159%7D%2C%22isMapVisible%22%3Afalse%2C%22filterState%22%3A%7B%22isForSaleByAgent%22%3A%7B%22value%22%3Afalse%7D%2C%22isForSaleByOwner%22%3A%7B%22value%22%3Afalse%7D%2C%22isNewConstruction%22%3A%7B%22value%22%3Afalse%7D%2C%22isForSaleForeclosure%22%3A%7B%22value%22%3Afalse%7D%2C%22isComingSoon%22%3A%7B%22value%22%3Afalse%7D%2C%22isAuction%22%3A%7B%22value%22%3Afalse%7D%2C%22isForRent%22%3A%7B%22value%22%3Atrue%7D%2C%22isAllHomes%22%3A%7B%22value%22%3Atrue%7D%2C%22sortSelection%22%3A%7B%22value%22%3A%22beds%22%7D%2C%22monthlyPayment%22%3A%7B%22max%22%3A1200%7D%2C%22price%22%3A%7B%22max%22%3A242031%7D%7D%2C%22isListVisible%22%3Atrue%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A16037%2C%22regionType%22%3A6%7D%5D%7D&wants={%22cat1%22:[%22listResults%22]}&requestId=9'))
'''

json_ob = json.loads(
    '{"data":{"viewer":null,"property":{"zpid":2088034915,"brokerId":null,"isHousingConnectorExclusive":false,"rentalListingOwnerReputation":{"responseRate":null,"responseTimeMs":null,"contactCount":1652,"applicationCount":0,"isLandlordIdVerified":null,"__typename":"RentalListingOwnerReputation"},"isFeatured":true,"isListedByOwner":false,"rentalListingOwnerContact":{"displayName":"Axle","businessName":"Quarterra","phoneNumber":"(720) 330-4646","agentBadgeType":null,"photoUrl":"","reviewsReceivedCount":null,"reviewsUrl":null,"ratingAverage":null,"isBrokerLocalCompliance":false,"__typename":"RentalListingOwnerContactType"},"postingProductType":"ApartmentUnit","postingContact":{"brokerName":"Quarterra","brokerageName":"Quarterra","name":"Axle","__typename":"postingContact"},"postingUrl":null,"rentalMarketingTreatments":["trustedListing","paid","multiFamilySalesListing"],"building":{"bdpUrl":"/apartments/seattle-wa/axle/9VXKQL/","buildingName":"Axle","housingConnector":{"hcLink":null,"__typename":"HousingConnector"},"ppcLink":null,"__typename":"BuildingMini"},"__typename":"Property"}},"extensions":{}}')
print
