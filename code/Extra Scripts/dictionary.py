# -*- coding: utf-8 -*-
import collections
# this one is more like a list. At every entry it stores the category(key) and its associated
# query key words
def createDictionary(path):
    handle = open(path, 'r')
    dictionary = []
    for line in iter(handle):
        line = line.strip().strip('\n').split(' ')
        entry = []
        entry.append(line[0])
        entry.append(' '.join(line[1:len(line)]))
        dictionary.append(entry)
    handle.close()
    return dictionary

# this one is a proper dictionary that stores a list of query keywords associated with a 
# a particular category (key)
def createDefaultDictionary(path):
    handle = open(path, 'r')
    dictionary = collections.defaultdict(list)
    for line in iter(handle):
        line = line.strip().strip('\n').split(' ')
        dictionary[line[0]].append(' '.join(line[1:len(line)]))
    handle.close()
    return dictionary

rootPath = 'resources/Root.txt'
#ComputersPath = 'resources/Computers.txt'
#HealthPath = 'resources/Health.txt'
#SportsPath = 'resources/SportsPath'
#
#rootDict = createDictionary(rootPath)
#ComputersDict = createDefaultDictionary(ComputersPath)
#
#print rootDict

#print ComputersDict['Hardware']

