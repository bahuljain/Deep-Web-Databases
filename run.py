# -*- coding: utf-8 -*-
import re
from subprocess import Popen, PIPE
import urllib2
import base64
import json
import pickle

GRAPH = {
    "Root": ["Computers", "Health", "Sports"],
    "Computers": ["Hardware", "Programming"],
    "Sports": ["Basketball", "Soccer"],
    "Health": ["Diseases", "Fitness"]
}

def getBingResult(website, query):
    query = query.replace(' ','%20')
    bingUrl = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3a' + website + '%20' + query + '%27&$top=4&$format=JSON'
    accountKey = '2dyKIv94jDETd7ClbVKoHvJSWFJ73ZvZRc7rjpBdkG8'
    accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
    headers = {'Authorization': 'Basic ' + accountKeyEnc}
    req = urllib2.Request(bingUrl, headers=headers)
    response = urllib2.urlopen(req)
    content = response.read()
    json_result = json.loads(content)
    return json_result['d']['results'][0]

# this method gets the results for every query word in the given category file and stores the number of
# matches for every word and the urls of the top 4 results
def getResults(website, resPath):
    with open(resPath, 'rb') as handle:
        resDict = pickle.load(handle)
    cache = {}
    #queries = reduce(list.__add__, resDict.values())
    #urlSet = set()
    #matches = dict()
    for key in resDict:
        cache[key] = {}
        for query in resDict[key][:3]:
            print query
            result = getBingResult(website, query)
            cache[key][query] = {
                'matches': float(result['WebTotal']),
                'urls': set([result['Url'] for result in result['Web']])
            }
            #urlSet = urlSet.union(urls)
            #webTotal = json_result['d']['results'][0]['WebTotal']
            #matches.update({query:webTotal})
    return cache

# using two threshold values tc and ts, the database is classified to a particular category
# if it successfully finds a category, it tries to further classify the database to a
# more precise domain
def classify(website, tc, ts):
    categories = ["Root"]
    data = {}
    for category in categories:
        keys = GRAPH.get(category)
        if keys:
            cache = getResults(website, 'resources/' + category + '.pickle')
            data.update(cache)
            covDict = categoryCoverage(cache)
            print covDict
            print ""
            specDict = specificity(covDict)
            print specDict
            for key in covDict:
                if (covDict[key] >= tc and specDict[key] >= ts):
                    categories.append(key)
    print data
    print ''
    return categories

# find the coverage of the database for different categories
def categoryCoverage(cache):
    covDict = {}
    for key in cache:
        covDict[key] = sum([cache[key][query]["matches"] for query in cache[key]])
    return covDict

# find the specificity of the database for every category
def specificity(covDict):
    totalCount = sum(covDict.values())
    specDict = {key: covDict[key]/totalCount for key in covDict}
    return specDict

# based on categories stitch url lists and form content summaries
def getUrls():
    return





def getVocabList():
    urls = getResults('fifa.com', 'resources/Root.pickle')[0]
    print urls
    vocabList = [getVocab(url) for url in urls]
    completeVocab = reduce(lambda a,b:a.union(b), vocabList, set())
    writeToFile(getDocFrequency(vocabList, completeVocab), 'contentSummary.txt')
    print ''

    #return completeVocab
def getDocFrequency(vocabList, completeVocab):
    docFreq = dict.fromkeys(completeVocab, 0)
    for word in completeVocab:
        docFreq[word] = sum([1 for vocab in vocabList if word in vocab])
    return docFreq

def getPageContent(url):
    p = Popen(["lynx", "--dump", url], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()
    return output if not err else None

def getVocab(url):
    print "Crawling through : " + url
    content = getPageContent(url)
    end = content.find("\nReferences\n")
    content = content[:end] if (end > 0) else content
    content = re.sub(r'\[(.*?)\]', '', re.sub(r'\n', "", content))
    vocab = set([w.lower() for w in re.split(r'\W+', content) if str.isalpha(w)])
    return vocab

def writeToFile(wordMap, filename):
    with open(filename, 'w') as f:
        for word, count in sorted(wordMap.iteritems()):
            f.write("{0}#{1}#-1.0\n".format(word, count))

#getResults('fifa.com', 'resources/Root.pickle')
#getVocabList()
print classify('fifa.com', 10000, 0.7)
