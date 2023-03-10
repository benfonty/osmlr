import math
import requests
import json
import os
import hashlib
import codecs

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
        dist = distance(nodes[i]["lat"], nodes[i]["lon"], nodes[i+1]["lat"], nodes[i+1]["lon"])
        if DEBUG_RELATION: print("distance between", nodes[i]["id"], "and", nodes[i+1]["id"], dist)
        result += dist
    return result
    

DEBUG = False

DEBUG_RELATION = None

CACHE_DIR="./cache"

if DEBUG_RELATION:
    relationsQuery = """
    [out:json];
    relation({});
    out body;
    """.format(DEBUG_RELATION)    
else:
    relationsQuery = """
    [out:json];
    (area[name="Nantes"]["admin_type:FR"="commune"]; )->.a;
    (
        relation[type=street](area.a);
        relation[type=associatedStreet](area.a);
    );
    out body;
    """

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

def hash(query):
    h = hashlib.sha1()
    h.update(query.encode('utf-8'))
    return h.hexdigest()

def cachedRequest(query):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR) 
    cacheFileName = CACHE_DIR + "/" + "request_" + hash(query)
    if os.path.exists(cacheFileName):
        if DEBUG: print(cacheFileName, "already exists")
        with codecs.open(cacheFileName, 'r', "utf-8") as file:
            return file.read()
    else:
        result = requests.post(URL, data=query)
        if result.status_code != 200:
            raise Exception("ERROR calling api: " + str(result.status_code) + " " + result.text )
        with codecs.open(cacheFileName, 'w', "utf-8") as file:
            file.write(result.text)
        return result.content




URL="https://overpass-api.de/api/interpreter"


result=cachedRequest(relationsQuery)

relations = json.loads(result)["elements"]

result = {}
def addResult(streetType, length, name, streetId):
    if result.get(streetType) == None:
        result[streetType] = []
    result[streetType].append({
        "length": length,
        "name": name,
        "id": streetId
    })

def sortGetLength(item):
    return item["length"]

def sortResults():
    for streetType in result:
        result[streetType].sort(reverse=True, key=sortGetLength)
        result[streetType] = result[streetType][:10]

def getName(relation):
    result = "unknown"
    if "tags" in relation:
        if "name" in relation["tags"]:
            result = relation["tags"]["name"]
        elif "note" in relation["tags"]:
            result = relation["tags"]["note"]
    return result

index = 0
for relation in relations:
    index += 1
    name = getName(relation)
    relId = relation["id"]
    streetLength = 0
    if DEBUG: print("calculating for street", name, relId)
    wayIds = [ i["ref"] for i in relation["members"] if i["role"] == "street" and i["type"] == "way"]
    if (len(wayIds)) != 0:
        query = calculateQueryFromWayIds(wayIds)
        streetResult = cachedRequest(query)
        waysAndNodes =  json.loads(streetResult)
        ways = [ i for i in waysAndNodes["elements"] if i["type"] == "way" and "tags" in i and "highway" in i["tags"]]
        nodes = [ i for i in waysAndNodes["elements"] if i["type"] == "node" ]
        if DEBUG_RELATION:
            print(ways)
            print(nodes)
        for way in  ways:
            nodesOfWay = [findNode(i, nodes) for i in way["nodes"]]
            streetLength += getLength(nodesOfWay)
        if streetLength > 0:
            addResult(ways[0]["tags"]["highway"], streetLength, name, relId)
    if DEBUG: print("street name", name, "length", streetLength)
    if index %50 == 0: print(index, "over", len(relations))
sortResults()
print(result)
    


