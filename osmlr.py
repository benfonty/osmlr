from OSMPythonTools.nominatim import Nominatim
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
import math

nominatim = Nominatim()
overpass = Overpass()

def getRelations(areaName, selector):
    areaId = nominatim.query(areaName).areaId()
    query = overpassQueryBuilder(area=areaId, elementType='relation', selector='"type"="' + selector + '"', out='body')
    return overpass.query(query).relations()

def distance(lat1, lon1, lat2, lon2):
    # https://www.movable-type.co.uk/scripts/latlong.html
    R = 6371000
    phi1 = lat1 * math.pi / 180
    phi2 = lat2 * math.pi / 180
    deltaPhi = (lat2 - lat1)  * math.pi / 180
    deltaLambda = (lon2 - lon1)  * math.pi / 180
    a = math.sin(deltaPhi/2) * math.sin(deltaPhi/2) + math.cos(phi1) * math.cos(phi2) * math.sin(deltaLambda/2) * math.sin(deltaLambda/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def getLength(nodes):
    if nodes == None or len(nodes) < 2:
        return 0
    result = 0
    for i in range(len(nodes) - 1):
        result += distance(nodes[i].lat(), nodes[i].lon(), nodes[i+1].lat(), nodes[i+1].lon())
    return result
    

streetRelations = getRelations('Nantes, France', 'street') + getRelations('Nantes, France', 'associatedStreet')
print("found", len(streetRelations), "streets")
maxLength = 0
maxLengthName = ""
maxLengthId = 0
for relation in streetRelations:
    name = relation.tags().get("name")
    streetLength = 0
    for member in relation.members():
        if "highway" in member.tags():
            member._unshallow()
            length = getLength(member.nodes())
            if length == 0:
                print("WARN, a way of", name, "is empty")
            streetLength += length
    #print("\t", "street name", name, "has", len(relation.members()), "members and length", streetLength)
    if streetLength > maxLength:
        maxLength = streetLength
        maxLengthName = name
        maxLengthId = relation.id()
print("Longest is", maxLengthName, "(", maxLengthId, ") with", maxLength, "meters")



