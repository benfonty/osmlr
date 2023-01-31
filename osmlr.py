from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass

nominatim = Nominatim()
overpass = Overpass()

def getStreets(areaName, selector):
    areaId = nominatim.query(areaName).areaId()
    query = overpassQueryBuilder(area=areaId, elementType='relation', selector='"type"="' + selector + '"', out='body')
    return overpass.query(query).relations()

def getWay():
    return None

streets = getStreets('Nantes, France', 'street') + getStreets('Nantes, France', 'associatedStreet')
print(len(streets))
for street in streets:
    name = street.tags().get("name")
    #print(street.id())
    street.members()[0]._unshallow()
    print(street.members()[0].toXML())
  
    ways = [ i for i in street.members()] # how to access the damn role to extract the street ways from the relation?
    #print(name, wayIds)
