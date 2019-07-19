import os
import json
import sys
import numpy as np

class Helpers: 
    @staticmethod
    def progressBar(title, value, endvalue, bar_length = 50):
        percent = float(value) / endvalue
        arrow = '-' * int(round(percent * bar_length) - 1) + '>'
        spaces = ' ' * (bar_length - len(arrow))

        sys.stdout.write("\r{0}: [{1}] {2}%".format(title, arrow + spaces, int(round(percent * 100))))
        sys.stdout.flush()

    @staticmethod
    def getSubdirectories(d):
        return filter(lambda x: os.path.isdir(os.path.join(d, x)), os.listdir(d))

    @staticmethod
    def readJsonFiles(files):
        d = {}
        for name in files:
            path = files[name]
            with open(path) as jsonFile:
                d[name] = json.load(jsonFile)
        return d

    @staticmethod
    def getFilesByExtFromDir(dir, ext):
        files = os.listdir(dir)
        files = [ x for x in files if ext in x ]
        files.sort(key=lambda f: int(filter(str.isdigit, f)))
        return files

    @staticmethod
    def createFolder(directory):
        current_directory = os.getcwd()
        print current_directory
        directory = os.path.join(current_directory, directory)
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print ('Error: Creating directory. ' + directory)