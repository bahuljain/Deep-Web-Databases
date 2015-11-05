import pickle
import re
from subprocess import Popen, PIPE

class DeepWebDatabase:

    def __init__(self, key, database):
        self.key = key
        self.database = database
        self.category = 'Root'
        self.level = 0

    # computes the total documents in the database
    def totalDocCount(self, covDict):
            totalCount = 0.0
        for key in covDict.keys():
            totalCount = totalCount + covDict[key]
        return totalCount

    # find the specificity of the database for every category
    def specificity(self, covDict):
        totalCount = self.totalDocCount(covDict)
        specDict = dict()
        for key in covDict.keys():
            specDict.update({key : covDict[key]/totalCount})
        return specDict

    # using two threshold values tc and ts, the database is classified to a particular category
    # if it successfully finds a category, it tries to further classify the database to a
    # more precise domain
    def classify(self, tc, ts):
        covDict = self.categoryCoverage()
        print self.key
        print covDict
        specDict = self.specificity(covDict)
        print specDict
        for key in covDict.keys():
            if (covDict[key] >= tc and specDict[key] >= ts):
                self.category = self.category + '/' + key
                self.level = self.level + 1

                # we need not classify beyond two levels
                if self.level < 2:
                    self.key = key
                    self.category = self.classify(tc,ts)
        return self.category

    # find the coverage of the database for different categories
    def categoryCoverage(self):
        #c = Cache()
        resPath = 'resources/' + self.key + '.pickle'
        cachePath = 'cache/' + self.database + '-' + self.key + '.pickle'
        with open(resPath, 'rb') as handle:
            resDict = pickle.load(handle)
        with open(cachePath, 'rb') as handle:
            cacheDict = pickle.load(handle)
        covDict = dict.fromkeys(resDict.keys(),0)
        for key in resDict.keys():
            for queryTerm in resDict[key]:
                covDict[key] = covDict[key] + float(cacheDict[queryTerm])
        return covDict


    def getResults(self, website, query):
        """resDict = self.createDefaultDictionary(resPath);
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
        """
        query = query.replace(' ','%20')
        bingUrl = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3a' + website + '%20' + query + '%27&$top=4&$format=JSON'
        accountKey = '2dyKIv94jDETd7ClbVKoHvJSWFJ73ZvZRc7rjpBdkG8'
        accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
        headers = {'Authorization': 'Basic ' + accountKeyEnc}
        req = urllib2.Request(bingUrl, headers=headers)
        response = urllib2.urlopen(req)
        content = response.read()
        json_result = json.loads(content)
        urls = set([result['Url'] for result in json_result['d']['results'][0]['Web']])
        matches = json_result['d']['results'][0]['WebTotal']
        #handle.write(queryTerm + ' ' + matches+'\n')
        print queryTerm + ' ' + matches

        return urls
