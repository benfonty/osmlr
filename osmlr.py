from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass

nominatim = Nominatim()
overpass = Overpass()

def getStreets(areaName):
    areaId = nominatim.query(areaName).areaId()
    query = overpassQueryBuilder(area=areaId, elementType='relation', selector='"type"="associatedStreet"', out='body')
    return overpass.query(query).relations()

def getWay():
    return None

streets = getStreets('Nantes, France')
print(len(streets))
for street in streets:
    name = street.tags().get("name")
    print(street.id())
    wayIds = [ i.id() for i in street.members() ] # how to access the damn role to extract the street ways from the relation?
    print(name, wayIds)