import math
import requests
import json

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

def getLat(node):
    return node["lat"]

def getLon(node):
    return node["lon"]

def getLength(nodes):
    if nodes == None or len(nodes) < 2:
        return 0
    result = 0
    for i in range(len(nodes) - 1):
        result += distance(getLat(nodes[i]), getLon(nodes[i]), getLat(nodes[i+1]), getLon(nodes[i+1]))
    return result
    

DEBUG = True

relationsQuery = """
[out:json];
(area[name="Nantes"]["admin_type:FR"="commune"]; )->.a;
(
  relation[type=street](area.a);
  relation[type=associatedStreet](area.a);
);
out body;
"""

def getName(element):
    tags = element.getElementsByTagName("tag")
    for tag in tags:
        if tag.getAttribute("k") == "name":
            return tag.getAttribute("v")
    return None

def calculateQueryFromWayIds(wayIds):
    query = "[out:json];("
    for wayId in wayIds:
        query += "way(" + str(wayId) + ");"
    query +=");"
    query += "out body;>;out skel qt;"
    return query

def findNode(nodeId, nodes):
    for i in nodes:
        if i["id"] == nodeId:
            return i
    return None

URL="https://overpass-api.de/api/interpreter"

result=requests.post(URL, data=relationsQuery).content

relations = json.loads(result)["elements"]

maxLength = 0
maxLengthName = ""
maxLengthId = 0
for relation in relations:
    name = relation["tags"]["name"]
    relId = relation["id"]
    streetLength = 0
    if DEBUG: print("calculating for street", name)
    wayIds = [ i["ref"] for i in relation["members"] if i["role"] == "street" and i["type"] == "way"]
    if DEBUG: print("found",len(wayIds), "ways")
    if (len(wayIds)) != 0:
        query = calculateQueryFromWayIds(wayIds)
        streetResult = requests.post(URL, data=query).content
        waysAndNodes =  json.loads(streetResult)
        ways = [ i for i in waysAndNodes["elements"] if i["type"] == "way" ]
        nodes = [ i for i in waysAndNodes["elements"] if i["type"] == "node" ]
        for way in  ways:
            nodesOfWay = [findNode(i, nodes) for i in way["nodes"]]
            streetLength += getLength(nodes)
    if DEBUG: print("street name", name, "length", streetLength)
    if streetLength > maxLength:
        maxLength = streetLength
        maxLengthName = name
        maxLengthId = relId
print("Longest is", maxLengthName, "(", maxLengthId, ") with", maxLength, "meters")
    


