from ocr import OCR
from helpers import Helpers
import os
import re
import json
import shutil
import Levenshtein

dev = False
jewels = {}
data = {}
dirs = {
    "result": os.path.join(os.getcwd(), "result"),
    "data": os.path.join(os.getcwd(), "data"),
    "resource": os.path.join(os.getcwd(), "resource"),
    "jewel": os.path.join(os.getcwd(), "data/jewel"),
    "jewelDone": os.path.join(os.getcwd(), "data/jewel_done"),
    "timeless": os.path.join(os.getcwd(), "data/timeless"),
}
jsonFiles = {
    "jewelSockets": os.path.join(dirs["resource"], "jewelSockets.json"),
    "passives": os.path.join(dirs["resource"], "passives.json"),
    "passivesAlt": os.path.join(dirs["resource"], "passivesAlternatives.json"),
    "passivesAdd": os.path.join(dirs["resource"], "passivesAdditions.json"),
    "passivesVaalAdd": os.path.join(dirs["resource"], "passivesVaalAdditions.json"),
}
valuePattern = "\(([\d.]+)-([\d.]+)\)"
valueRegex = re.compile(valuePattern)

def imagesInDirToStrings(dir):
    files = Helpers.getFilesByExtFromDir(dir, ".png")
    i, texts = 1, []

    for fileName in files:
        image = OCR.getFilteredImage(os.path.join(dir, fileName))
        lines = OCR.imageToStringArray(image)
        texts.append(lines)

        Helpers.progressBar(str(i) + "/" + str(len(files)), i, len(files))
        i += 1
    print ""

    return texts

def loadAnalyzedJewels(dir):
    files = Helpers.getFilesByExtFromDir(dir, ".json")

    for f in files:
        path = os.path.join(dir, f)
        jewelId = f.replace(".json", "")
        print ("Reading jewel socket '" + jewelId + "' data")
        with open(path) as jsonFile:
            jewels[jewelId] = json.load(jsonFile)

def removeUnnecessaryJewels(jewelsDir, timelessDir):
    jewelDirs = Helpers.getSubdirectories(jewelsDir)
    timeless = Helpers.getSubdirectories(timelessDir)

    for jewelId in jewelDirs:
        if not any(jewelId in s for s in timeless) or jewelId in jewels:
            print ("Removing jewel socket directory '" + jewelId + "' because it is not needed for any captured Timeless Jewels or has already been analyzed")
            if not dev:
                shutil.rmtree(os.path.join(jewelsDir, jewelId))
                positionFile = os.path.join(jewelsDir, jewelId + ".png")
                if os.path.isfile(positionFile):
                    os.remove(positionFile)

def determinePassiveVariation(lines, variations):
    line = " ".join(lines)
    score = [0.0] * len(variations)

    i = 0
    for variant in variations:
        passiveString = " ".join(variant)
        score[i] += Levenshtein.ratio(passiveString, line)
        i += 1

    return variations[score.index(max(score))]

def determinePassiveName(lines, passives):
    result = { "name": None, "index": -1, "ratio": 0.0 }
    bestRatio = 0.0

    lineIndex = 0
    for line in lines:
        for passiveName in passives:
            ratio = Levenshtein.ratio(passiveName, line)
            if ratio == 1.0:
                result["ratio"] = ratio
                result["name"] = passiveName
                result["index"] = lineIndex
                break
            elif ratio > result["ratio"]:
                result["ratio"] = ratio
                result["name"] = passiveName
                result["index"] = lineIndex
        if result["ratio"] == 1.0:
            break

        lineIndex += 1
    return result

def replacePassiveValue(line, passive, acceptAny = False):
    match = valueRegex.search(passive)
    if match:
        valueMatch = re.search("[\d.]+", line)
        value = float(match.group(1))
        if valueMatch:
            foundValue = float(valueMatch.group(0))
            # If found value is in range
            if (foundValue >= float(match.group(1)) and foundValue <= float(match.group(2))) or acceptAny:
                value = foundValue
                if value.is_integer():
                    value = int(value)
        passive = re.sub(valuePattern, str(value), passive)
    
    return passive

def getPassiveWithValue(lines, passive):
    bestRatio = 0.0
    passiveIndex = -1
    lineIndex = 0
    for line in lines:
        ratio = Levenshtein.ratio(passive, line)
        if ratio > bestRatio:
            passiveIndex = lineIndex
            bestRatio = ratio

        lineIndex += 1

    passive = replacePassiveValue(lines[passiveIndex], passive)

    return passive

def rectifyJewelLines(lines, jewelInfo):
    name = determinePassiveName(lines, data["passives"])
    result = { "name": name["name"], "passives": [] }

    # Regular nodes have variations of the passives with the same passive name, determine them
    # For notables and keystones, passives don't have variations so just accept them
    passives = data["passives"][result["name"]]["passives"]
    if jewelInfo["type"] == "regular":
        if len(passives) == 1:
            result["passives"] = passives[0]
        else:
            passives = determinePassiveVariation(lines[(name["index"] + 1):], passives)
            result["passives"] = passives
    else:
        result["passives"] = passives[0]

    return result

def findAddedRandomMod(lines, passives):
    bestRatio = 0.0
    matchingPassive = None
    matchingLineIndex = -1
    lineIndex = len(lines) - 1
    for line in reversed(lines):
        for passive in passives:
            ratio = Levenshtein.ratio(passive, line)
            if ratio > bestRatio:
                matchingLineIndex = lineIndex
                matchingPassive = passive
                bestRatio = ratio
        lineIndex -= 1

    return { "passive": matchingPassive, "line": matchingLineIndex, "ratio": bestRatio }

def rectifyTimelessLines(lines, jewelInfo, tJewelInfo):
    result = {
        "name": None,
        "passives": {
            "original": jewelInfo["passives"],
            "new": [],
            "added": []
        }
    }

    if jewelInfo["type"] == "keystone":
        pass
    else:
        # Lethal Pride
        if tJewelInfo["type"] == "Lethal Pride":
            passiveToAdd = findAddedRandomMod(lines, data["passivesAdd"])["passive"]
            result["name"] = jewelInfo["name"]
            result["passives"]["new"] = jewelInfo["passives"] + [ passiveToAdd ]
            result["passives"]["added"] = [ passiveToAdd ]
            return result

        # Brutal Restraint
        if tJewelInfo["type"] == "Brutal Restraint":
            passiveToAdd = findAddedRandomMod(lines, data["passivesAdd"])["passive"]
            result["name"] = jewelInfo["name"]
            result["passives"]["new"] = jewelInfo["passives"] + [ passiveToAdd ]
            result["passives"]["added"] = [ passiveToAdd ]
            return result

        # Elegant Hubris
        if tJewelInfo["type"] == "Elegant Hubris":
            if jewelInfo["type"] == "regular":
                result["name"] = "Price of Glory"
                result["passives"]["new"] = []
                result["passives"]["added"] = []
            else:
                name = determinePassiveName(lines, data["passivesAlt"])
                result["name"] = name["name"]
                result["passives"]["new"] = data["passivesAlt"][result["name"]]["passives"]
                result["passives"]["added"] = data["passivesAlt"][result["name"]]["passives"]
            return result

        # Glorious Vanity
        if tJewelInfo["type"] == "Glorious Vanity":
            name = determinePassiveName(lines, data["passivesAlt"])
            result["name"] = name["name"]
            if name["name"] == "Might of the Vaal":
                passives = []
                while True:
                    foundMod = findAddedRandomMod(lines, data["passivesVaalAdd"])
                    if foundMod["ratio"] > 0.8:
                        line = lines[foundMod["line"]]
                        passive = replacePassiveValue(line, foundMod["passive"], True)
                        passives.append(passive)
                        del lines[foundMod["line"]]
                        if len(lines) == 0:
                            break
                    else:
                        break
                result["passives"]["new"] = passives
                result["passives"]["added"] = passives
            else:
                passives = data["passivesAlt"][name["name"]]["passives"]
                for p in passives:
                    passive = getPassiveWithValue(lines, p)
                    result["passives"]["new"].append(passive)
                    result["passives"]["added"].append(passive)
                return result

        # Militant Faith
        if tJewelInfo["type"] == "Militant Faith":
            if jewelInfo["type"] == "regular":
                # Check if it's a stat node and if it's a regular one (not a +15 regular)
                if jewelInfo["name"] in ["Strength", "Dexterity", "Intelligence"] and \
                any(x in jewelInfo["passives"] for x in ["+10 to Strength", "+10 to Dexterity", "+10 to Intelligence"]):
                    result["name"] = "Devotion"
                    result["passives"]["new"] = [ "+10 to Devotion" ]
                    result["passives"]["added"] = [ "+10 to Devotion" ]
                else:
                    result["name"] = jewelInfo["name"]
                    result["passives"]["new"] = jewelInfo["passives"] + [ "+5 to Devotion" ]
                    result["passives"]["added"] = [ "+5 to Devotion" ]
            else:
                name = determinePassiveName(lines, data["passivesAlt"])
                if name["ratio"] >= 0.85:
                    result["name"] = name["name"]
                    result["passives"]["new"] = data["passivesAlt"][result["name"]]["passives"]
                    result["passives"]["added"] = data["passivesAlt"][result["name"]]["passives"]
                else:
                    result["name"] = jewelInfo["name"]
                    result["passives"]["new"] = jewelInfo["passives"] + [ "+5 to Devotion" ]
                    result["passives"]["added"] = [ "+5 to Devotion" ]
            return result

    return result

def determineJewelSocket(passives):
    names = []
    for passive in passives:
        names.append(passive["name"])

    socketIndex = 0
    for socket in data["jewelSockets"]:
        found = True
        for passiveName in socket["passives"]:
            if passiveName not in names:
                found = False
        if found:
            return { "name": socket["name"], "index": socketIndex }
        socketIndex += 1

    return { "name": "Unknown", "index": -1 }

def analyzeJewels(jewelsDir):
    jewelIds = Helpers.getSubdirectories(jewelsDir)

    # Loop through each folder in jewels folder
    for jewelId in jewelIds:
        jewelDir = os.path.join(jewelsDir, jewelId)

        if jewelId in jewels:
            continue

        print ("Analyzing jewel socket '" + jewelId + "'")

        # Read data that was saved from capturing
        with open(os.path.join(jewelDir, "data.json")) as jsonFile:
            jewelInfo = json.load(jsonFile)

        # Convert all images into an array of string arrays
        nodes = imagesInDirToStrings(jewelDir)

        # Try to rectify misread texts by using stored passive data
        result = { "socket": "", "nodes": [] }
        i = 0
        for lines in nodes:
            rectifiedLines = rectifyJewelLines(lines, jewelInfo[i])
            result["nodes"].append({
                "name": rectifiedLines["name"],
                "x": jewelInfo[i]["x"],
                "y": jewelInfo[i]["y"],
                "type": jewelInfo[i]["type"],
                "passives": rectifiedLines["passives"]
                })
            i += 1

        # Determine jewel socket
        result["socket"] = determineJewelSocket(result["nodes"])

        # Write jewels results to global var
        jewels[jewelId] = result

        # Write jewel results
        with open(os.path.join(dirs["jewelDone"], jewelId + ".json"), 'w') as f:
            json.dump(result, f, indent=4, sort_keys=True)

        # Move position image to finished jewel
        positionFilePath = os.path.join(dirs["jewel"], jewelId + ".png")
        resultFilePath = os.path.join(dirs["jewelDone"], jewelId + ".png")
        if os.path.isfile(resultFilePath):
            os.remove(resultFilePath)
        shutil.move(positionFilePath, resultFilePath)

        # Remove folder with images
        if not dev:
            shutil.rmtree(jewelDir)

def analyzeTimelessJewels(jewelsDir):
    timelessDirs = Helpers.getSubdirectories(jewelsDir)

    # Loop through each folder in jewels folder
    for dir in timelessDirs:
        tJewelDir = os.path.join(jewelsDir, dir)
        idSplit = dir.split("_")
        jewelId = idSplit[0]
        timelessId = idSplit[1]

        # Make sure corresponding jewel data is available for this jewel
        if jewelId in jewels:
            jewelInfo = jewels[jewelId]
        else:
            print "Couldn't find corresponding jewel socket data for this Timeless Jewel, skipping"
            continue

        # Read data that was saved from capturing
        with open(os.path.join(tJewelDir, "data.json")) as jsonFile:
            tJewelInfo = json.load(jsonFile)

        print ("Analyzing Timeless Jewel '" + timelessId + "'")
        print ("Type:\t\t" + tJewelInfo["type"])
        print ("Seed:\t\t" + str(tJewelInfo["seed"]))
        print ("Variant:\t" + tJewelInfo["variant"])
        print ("Jewel socket:\t" + jewelId)

        # Convert all images into an array of string arrays
        nodes = imagesInDirToStrings(tJewelDir)

        result = {
            "info": {
                "socket": jewelInfo["socket"],
                "seed": tJewelInfo["seed"],
                "type": tJewelInfo["type"],
                "variant": tJewelInfo["variant"],
            },
            "nodes": [] }
        i = 0
        for lines in nodes:
            rectifiedLines = rectifyTimelessLines(lines, jewelInfo["nodes"][i], tJewelInfo)
            result["nodes"].append({
                "name": {
                    "original": jewelInfo["nodes"][i]["name"],
                    "new": rectifiedLines["name"]
                },
                "x": jewelInfo["nodes"][i]["x"],
                "y": jewelInfo["nodes"][i]["y"],
                "type": jewelInfo["nodes"][i]["type"],
                "passives": rectifiedLines["passives"]
                })
            i += 1

        # Write jewel results
        fileName = tJewelInfo["type"] + "_" + str(tJewelInfo["seed"]) + "_" + tJewelInfo["variant"] + "_" + jewelInfo["socket"]["name"]
        with open(os.path.join(dirs["result"], fileName + ".json"), 'w') as f:
            json.dump(result, f, indent=4, sort_keys=True)

        # Remove folder with images
        if not dev:
            shutil.rmtree(tJewelDir)


if __name__ == '__main__':
    for dir in dirs:
        Helpers.createDirectory(dirs[dir])
    data = Helpers.readJsonFiles(jsonFiles)
    loadAnalyzedJewels(dirs["jewelDone"])
    removeUnnecessaryJewels(dirs["jewel"], dirs["timeless"])
    analyzeJewels(dirs["jewel"])
    analyzeTimelessJewels(dirs["timeless"])
