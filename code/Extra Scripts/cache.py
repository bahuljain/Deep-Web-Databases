# -*- coding: utf-8 -*-
import urllib2
import base64
import json
import collections
import pickle
#health.com: Root/Health/Fitness
#yahoo.com: Root
#fifa.com: Root/Sports/Soccer
#diabetes.org: Root/Health
#hardwarecentral.com:  Root/Computers
class Cache:

    def readCache(self, path):
        handle = open(path, 'r')
        dictionary = dict()
        for line in iter(handle):
            line = line.strip().strip('\n').split(' ')
            dictionary.update({' '.join(line[0:len(line)-1]):line[len(line)-1]})
        handle.close()
        with open('path.pickle', 'wb') as handle:
            pickle.dump(dictionary, handle)
        return dictionary


    def createDefaultDictionary(self,path):
        handle = open(path, 'r')
        dictionary = collections.defaultdict(list)
        for line in iter(handle):
            line = line.strip().strip('\n').split(' ')
            dictionary[line[0]].append(' '.join(line[1:len(line)]))
        handle.close()
        return dictionary

    def writeCache(self, website, outpath, resPath):
        resDict = self.createDefaultDictionary(resPath);
        handle = open(outpath,'w')
        for key in resDict.keys():
            for queryTerm in resDict[key]:
                query = queryTerm.replace(' ','%20')
                bingUrl = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3a' + website + '%20' + query + '%27&$top=1&$format=JSON'
                accountKey = '2dyKIv94jDETd7ClbVKoHvJSWFJ73ZvZRc7rjpBdkG8'
                accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
                headers = {'Authorization': 'Basic ' + accountKeyEnc}
                req = urllib2.Request(bingUrl, headers=headers)
                response = urllib2.urlopen(req)
                content = response.read()
                json_result = json.loads(content)
                urls = set([result['Url'] for result in json_result['d']['results'][0]['Web']])
                matches = json_result['d']['results'][0]['WebTotal']
                handle.write(queryTerm + ' ' + matches+'\n')
                print queryTerm + ' ' + matches
        handle.close()

#websites = ['health.com','yahoo.com','fifa.com', 'diabetes.org', 'hardwarecentral.com']
#writeCache(websites[4],'cache/hardwarecentral.com.txt')
#website = 'hardwarecentral.com'
#resPath = 'resources/Computers.txt'
#outPath = 'cache/hardwarecentral.com-Computers.txt'
#c = Cache()
#c.writeCache(website, outPath, resPath)
