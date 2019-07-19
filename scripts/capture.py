import org.sikuli.script.SikulixForJython
import math
import sys
sys.path.append("scripts/")
import time
import os
import json
from sikuli.Sikuli import *
from captureHelpers import Helpers

# Sikuli settings
Settings.MoveMouseDelay = 0
Settings.ActionLogs = False
Settings.InfoLogs = False
Settings.DebugLogs = False

# Global variables
cfg = {
    "title": "Skill Capture",
    "radius": 426,
    "offsets": {
        "regular": 8,
        "notable": 12,
        "keystone": 25,
        "poe": 300,
        "radius": 30,
        "jewel": 200
    },
    "sim": {
        "jewel": 0.95,
        "jewelSocketed": 0.9,
        "notable": 0.7,
        "notableAlloc": 0.75,
        "regular": 0.87,
        "regularAlloc": 0.8,
        "zoom": 0.9
    },
    "txtbox": {
        "xOffset": 30,
        "yOffset": 140,
        "width": 680,
        "height": 480
    },
    "mouse": {
        "zoom": {
            "x": 727,
            "y": 69,
            "offset": 37
        }
    }
}

dirs = {
    "images": os.path.join(os.getcwd(), "images"),
    "timeless": os.path.join(os.getcwd(), "data/timeless"),
    "jewel": os.path.join(os.getcwd(), "data/jewel"),
    "jewelDone": os.path.join(os.getcwd(), "data/jewel_done")
}

images = {
    "jewel": os.path.join(dirs["images"], "Jewel.png"),
    "jewelSocketed": os.path.join(dirs["images"], "JewelSocketed.png"),
    "notable": os.path.join(dirs["images"], "Notable.png"),
    "notableAlloc": os.path.join(dirs["images"], "NotableAllocated.png"),
    "regular": os.path.join(dirs["images"], "Skill.png"),
    "regularAlloc": os.path.join(dirs["images"], "SkillAllocated.png"),
    "zoom": os.path.join(dirs["images"], "Zoom.png"),
    "zoomedOut": os.path.join(dirs["images"], "ZoomOut.png"),
    "timelessJewel": os.path.join(dirs["images"], "TimelessJewel.png"),
    "conquered": os.path.join(dirs["images"], "Conquered.png"),
}

regions = {
    "poe": None,
    "radius": None,
    "jewel": None
}

jewel = {
    "id": 0,
    "nodes": [],
    "type": "",
    "variant": "",
    "seed": 0
}

capturedJewels = []

def end(event):
    popup("Script stopped", cfg["title"])
    sys.exit()
    return


def start(event):
    global regions
    global jewel

    # Check if PoE is running
    regions["poe"] = App("Path of Exile").window()
    if not regions["poe"]:
        popup("Path of Exile is not running", cfg["title"])
        return

    # Check if PoE is running in 1920x1080 borderless
    if not (regions["poe"].getW() == 1920 and regions["poe"].getH() == 1080):
        popup("Path of Exile must be running in 1920x1080 borderless fullscreen", cfg["title"])
        return

    # Check if zoom is correct
    if not checkZoom():
        popup("Zoom is set incorrectly.\n\nPlease zoom all the way out and press F3 to automatically zoom in correctly.", cfg["title"])
        return

    # If no jewel region has been defined yet, do that
    if not regions["jewel"]:
        print "Locating previously captured jewels..."
        if locateAndStoreCapturedJewel():
            popup("It looks like you capture this jewel before, so you're good to go!\n\nPlease open your inventory, hover over the jewel you want to analyze and press F2.\n\nMake sure to not move the passive skill tree, otherwise the script will attempt to find the a new jewel position.", cfg["title"])
            return

        print "None found, locating empty jewel socket..."
        result = locateEmptyJewel()
        if result:
            jewel["id"] = int(time.time())
            # Find nodes in radius, save node coordinates and type and capture passive text
            jewel["nodes"] = locateAllNodes()
            jewelDirectory = os.path.join(dirs["jewel"], str(jewel["id"]))
            captureTextFromNodes(jewel["nodes"], jewelDirectory)
            mouseMove(Location(100, 100))
            wait(0.1)
            capture(regions["jewel"].nearby(cfg["offsets"]["jewel"]), dirs["jewel"], str(jewel["id"]) + ".png")
            saveNodeData(jewel["nodes"], jewelDirectory, jewel["id"])
            popup("Successfully captured jewel and " + str(len(jewel['nodes'])) + " nodes.\n\nPlease open your inventory, hover over the jewel you want to analyze and press F2.\n\nMake sure to not move the passive skill tree, otherwise the script will attempt to find the a new jewel position.", cfg["title"])
        return

    # If jewel region has been defined
    if regions["jewel"]:
        # If jewel data hasn't been extracted yet
        if jewel["seed"] == 0:
            Env.setClipboard("")
            type('c', KeyModifier.CTRL)
            wait(0.1)
            data = Helpers.extractJewelData(Env.getClipboard())
            Env.setClipboard("")
            if data != False:
                jewel["seed"] = data["seed"]
                jewel["type"] = data["type"]
                jewel["variant"] = data["variant"]
                popup("Successfully extracted Timeless Jewel data.\n\nPlease socket the Timeless Jewel and start the procedure.\n\nMake sure to not move the passive skill tree, otherwise the script will attempt to find the a new jewel position.", cfg["title"])
            else:
                popup("Couldn't extract Timeless Jewel data.\n\nPlease open your inventory, hover over the jewel you want to analyze and press F2.\n\nMake sure to not move the passive skill tree, otherwise the script will attempt to find the a new jewel position.", cfg["title"])
            return

        # If jewel is socketed, read nodes
        if isJewelSocketed():
            jewelId = int(time.time())
            jewelDirectory = os.path.join(dirs["timeless"], str(jewel["id"]) + "_" + str(jewelId))
            captureTextFromNodes(jewel["nodes"], jewelDirectory)
            saveTimelessJewelData(jewel, jewelDirectory)
            jewel["seed"] = 0
            popup("Successfully captured " + str(len(jewel['nodes'])) + " nodes.\n\nYou can now run the analyzer to receive results for your jewel\nor press F2 while hovering over another jewel in your inventory.\n\nYou can also move to another jewel socket and start from the beginning by pressing F2.", cfg["title"])
            return

        # If jewel is not socketed but empty socket is still in correct position
        if isEmptyJewelInCorrectPosition():
            popup("Please socket the timeless jewel into the jewel socket.", cfg["title"])
        else:
            popup("The jewel socket can't be found at its previous location anymore.\n\nThe script will look for the new position next time.\nMake sure you haven't socketed a jewel into your target socket.", cfg["title"])
            regions["jewel"] = None
            jewel["nodes"] = []
            jewel["seed"] = 0
            return
        return
    return

def loadCapturedJewels():
    global dirs

    files = Helpers.getFilesByExtFromDir(dirs["jewelDone"], ".png")
    capturedJewels = []
    for f in files:
        jewelId = f.replace(".png", "")
        result = { "id": jewelId }
        with open(os.path.join(dirs["jewelDone"], jewelId + ".json")) as jsonFile:
            result["json"] = json.load(jsonFile)
        result["image"] = f
        capturedJewels.append(result)
        print "Loaded jewel with ID " + str(jewelId)

    return capturedJewels

def locateAndStoreCapturedJewel():
    global jewel
    global regions

    for j in capturedJewels:
        imagePath = os.path.join(dirs["jewelDone"], j["image"])
        match = regions["poe"].exists(Pattern(imagePath))
        if match:
            jewel["id"] = j["id"]
            jewel["nodes"] = []
            regions["jewel"] = match.nearby(-cfg["offsets"]["jewel"])
            jewelCenter = regions["jewel"].getCenter()
            for node in j["json"]["nodes"]:
                x = jewelCenter.getX() + int(node["x"] * cfg["radius"])
                y = jewelCenter.getY() + int(node["y"] * cfg["radius"])
                region = Region(x, y, 0, 0).nearby(10)
                jewel["nodes"].append({
                    "type": node["type"],
                    "region": region
                })
            return True
    return False

def locateEmptyJewel():
    global regions
    global images
    global cfg

    image = Pattern(images["jewel"]).similar(cfg["sim"]["jewel"])
    # Use a smaller region than the full window to find jewel
    matches = regions["poe"].nearby(-cfg["offsets"]["poe"]).findAllList(image)
    foundJewel = None

    # If only found 1 match, use it
    if len(matches) == 1:
        foundJewel = matches[0]
    else: # Otherwise, ask user to select correct jewel
        for m in matches:
            m.highlight()
            answer = popAsk("Is the highlighted jewel the jewel you want to use?")
            if answer:
                foundJewel = m
                break

    if foundJewel:
        regions["jewel"] = foundJewel
        jewelCenter = foundJewel.getCenter()
        regions["radius"] = Region(jewelCenter.getX() - cfg["radius"], jewelCenter.getY() - cfg["radius"], cfg["radius"]*2, cfg["radius"]*2)
        # Make the radius region slightly bigger to make sure it also captures "cut off" nodes
        regions["radius"] = regions["radius"].nearby(cfg["offsets"]["radius"])
        return True

    popup("No empty jewel socket found. Make sure the jewel socket is located in the middle region of the screen.", cfg["title"])
    return False

# Checks if a jewel has been socketed into the previously empty jewel socket
def isJewelSocketed():
    global regions
    global images

    image = Pattern(images["jewelSocketed"]).similar(cfg["sim"]["jewelSocketed"])
    return regions["jewel"].exists(image)

# Checks if the empty jewel socket is still in the same position
def isEmptyJewelInCorrectPosition():
    global regions
    global images

    image = Pattern(images["jewel"]).similar(cfg["sim"]["jewel"])
    return regions["jewel"].exists(image)

# Locates all nodes in the radius region, filters nodes outside of circle radius, filters jewel sockets
# and highlights them to prevent them from being detected twice
def locateAllNodes():
    global cfg

    allocNotableRegions = locateNodes("notableAlloc", cfg["sim"]["notableAlloc"])
    allocatedNotables = filterInvalidNodeRegions(allocNotableRegions, "notable")
    highlightNodes(allocatedNotables, "notable")

    notableRegions = locateNodes("notable", cfg["sim"]["notable"])
    notables = filterInvalidNodeRegions(notableRegions, "notable")
    highlightNodes(notables, "notable")

    regularRegions = locateNodes("regular", cfg["sim"]["regular"])
    regulars = filterInvalidNodeRegions(regularRegions, "regular")
    highlightNodes(regulars, "regular")

    allocRegularRegions = locateNodes("regularAlloc", cfg["sim"]["regularAlloc"])
    allocatedRegulars = filterInvalidNodeRegions(allocRegularRegions, "regular")
    highlightNodes(allocatedRegulars, "regular")

    highlightAllOff()
    return notables + allocatedNotables + regulars + allocatedRegulars

# Saves coordinates and type of nodes in circle radius of jewel to a json file
def saveNodeData(nodes, directory, id):
    global regions
    global cfg
    global dirs

    Helpers.createFolder(directory)
    fullPath = os.path.join(directory, "data.json")

    jsonNodes = []
    for n in nodes:
        relativeCoords = Helpers.calcRelativeDistFromPoint(regions["jewel"].getCenter(), n["region"].getCenter(), cfg["radius"])
        jsonNodes.append({
            "x": relativeCoords[0],
            "y": relativeCoords[1],
            "type": n["type"]
        })

    capturedJewels.append({
        "id": id,
        "json": { "nodes": jsonNodes },
        "image": os.path.join(dirs["jewel"], str(id) + ".png")
    })

    with open(fullPath, 'w') as f:
        json.dump(jsonNodes, f, indent=4, sort_keys=True)
    return

# Saves type, seed and variant of timeless jewel to a json file
def saveTimelessJewelData(data, directory):
    Helpers.createFolder(directory)
    fullPath = os.path.join(directory, "data.json")

    newData = {
        "type": data["type"],
        "seed": data["seed"],
        "variant": data["variant"]
    }

    with open(fullPath, 'w') as f:
        json.dump(newData, f, indent=4, sort_keys=True)
    return

# Captures the text boxes of passives and saves them into a directory
def captureTextFromNodes(nodes, directory):
    global cfg

    Helpers.createFolder(directory)

    cnt = 0
    for n in nodes:
        mouseMove(n["region"])
        wait(0.1)
        nodeCenter = n["region"].getCenter()

        y = nodeCenter.getY() - cfg["txtbox"]["yOffset"]
        if y + cfg["txtbox"]["height"] > regions["poe"].getH():
            y = regions["poe"].getH() - cfg["txtbox"]["height"]

        textRegion = Region(nodeCenter.getX() + cfg["txtbox"]["xOffset"], y, cfg["txtbox"]["width"], cfg["txtbox"]["height"])
        capture(textRegion, directory, str(cnt))
        cnt += 1

# Checks if the passive skill tree zoom is set correctly
def checkZoom():
    global images
    global cfg

    image = Pattern(images["zoom"]).similar(cfg["sim"]["zoom"])
    if regions["poe"].exists(image):
        return True

    return False


def adjustZoom(event):
    global regions

    if not regions["poe"]:
        # Check if PoE is running
        regions["poe"] = App("Path of Exile").window()
        if not regions["poe"]:
            popup("Path of Exile is not running", cfg["title"])
            return

    if regions["poe"].exists(images["zoomedOut"]):
        mouseMove(Location(cfg["mouse"]["zoom"]["x"], cfg["mouse"]["zoom"]["y"]))
        wait(0.1)
        mouseDown(Button.LEFT)
        mouseMove(Location(cfg["mouse"]["zoom"]["x"] + cfg["mouse"]["zoom"]["offset"], cfg["mouse"]["zoom"]["y"]))
        wait(0.1)
        mouseUp(Button.LEFT)

# Locate all nodes in the jewel radius rectangle
def locateNodes(id, similarity):
    global regions

    image = Pattern(images[id]).similar(similarity)
    matches = regions["radius"].findAllList(image)
    return matches

# Filters nodes that are either the jewel node or not in jewel radius
def filterInvalidNodeRegions(nodeRegions, type):
    global regions
    nodeData = []

    for n in nodeRegions:
        # Skip node if it is the jewel
        if Helpers.doRectsOverlap(n, regions["jewel"]) == False:
            continue

        # Check if node is in circle radius
        if Helpers.isPointInsideCircle(n.getCenter(), regions["jewel"].getCenter(), cfg["radius"]):
            nodeData.append({"region": n, "type": type})

    return nodeData

# Highlights all nodes passed to the method
def highlightNodes(nodes, type, color="cyan"):
    global cfg

    for n in nodes:
        n["region"].highlightOn(color)
        n["region"].nearby(-(int(cfg["offsets"][type]) / 2)).highlightOn(color)
        n["region"].nearby(-int(cfg["offsets"][type])).highlightOn(color)

# Hotkeys
Env.addHotkey(Key.F2, 0, start)
Env.addHotkey(Key.F3, 0, adjustZoom)
Env.addHotkey(Key.F4, 0, end)

if __name__ == '__main__':
    print "Loading captured jewels"
    capturedJewels = loadCapturedJewels()

    print "Ready"
    while True:
        wait(0.1)
