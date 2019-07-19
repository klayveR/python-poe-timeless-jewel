import os
import json
import sys
import re

class Helpers:
    @staticmethod
    def doRectsOverlap(r1, r2):
        return r1.getX() + r1.getW() < r2.getX() or r1.getY() + r1.getH() < r2.getY() or r1.getX() > r2.getX() + r2.getW() or r1.getY() > r2.getY() + r2.getH()

    @staticmethod
    def isPointInsideCircle(point, circleCenter, r):
        x = point.getX()
        y = point.getY()
        a = circleCenter.getX()
        b = circleCenter.getY()
        return (x - a)*(x - a) + (y - b)*(y - b) < r*r

    @staticmethod
    def calcCirclePoints(radius, points, location):
        slice = 2 * math.pi / points
        result = []

        for i in range(0, points):
            angle = slice * i
            x = int(location.getX() + radius * math.cos(angle))
            y = int(location.getY() + radius * math.sin(angle))
            result.append((x, y))
        return result

    @staticmethod
    def extractJewelData(cb):
        data = {}

        if "Timeless Jewel" and "Passives in radius are Conquered" in cb:
            lines = cb.split("\n")
            data["type"] = lines[1].encode('ascii','ignore')

            idx = -1
            cnt = 0
            for l in lines:
                if "Passives in radius are Conquered" in l:
                    idx = cnt - 1
                    break
                cnt += 1

            if idx != -1:
                data["seed"] = int(re.search(r'\d+', lines[idx]).group(0))
                data["variant"] = lines[idx].split()[-1].encode('ascii','ignore')

            return data
        return False

    @staticmethod
    def calcRelativeDistFromPoint(centerPoint, point, r = 0):
        x = float(point.getX() - centerPoint.getX())
        y = float(point.getY() - centerPoint.getY())

        if r != 0:
            x = float(x / r)
            y = float(y / r)

        return (x, y)

    @staticmethod
    def getFilesByExtFromDir(dir, ext):
        files = os.listdir(dir)
        files = [ x for x in files if ext in x ]
        files.sort(key=lambda f: int(filter(str.isdigit, f)))
        return files

    @staticmethod
    def getSubdirectories(d):
        return filter(lambda x: os.path.isdir(os.path.join(d, x)), os.listdir(d))

    @staticmethod
    def getFilesByExtFromDir(dir, ext):
        files = os.listdir(dir)
        files = [ x for x in files if ext in x ]
        files.sort(key=lambda f: int(filter(str.isdigit, f)))
        return files

    @staticmethod
    def createDirectory(directory):
        current_directory = os.getcwd()
        directory = os.path.join(current_directory, directory)
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print ('Creating directory ' + directory)
        except OSError:
            print ('Error: Creating directory. ' + directory)

    @staticmethod
    def readJsonFiles(files):
        d = {}
        for name in files:
            path = files[name]
            with open(path) as jsonFile:
                d[name] = json.load(jsonFile)
        return d

    @staticmethod
    def progressBar(title, value, endvalue, bar_length = 50):
        percent = float(value) / endvalue
        arrow = '-' * int(round(percent * bar_length) - 1) + '>'
        spaces = ' ' * (bar_length - len(arrow))

        sys.stdout.write("\r{0}: [{1}] {2}%".format(title, arrow + spaces, int(round(percent * 100))))
        sys.stdout.flush()
