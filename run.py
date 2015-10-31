# -*- coding: utf-8 -*-
import re
from subprocess import Popen, PIPE
import urllib2
import base64
import json
import pickle
from hashlib import sha256

GRAPH = {
    "Root": ["Computers", "Health", "Sports"],
    "Computers": ["Hardware", "Programming"],
    "Sports": ["Basketball", "Soccer"],
    "Health": ["Diseases", "Fitness"]
}

# this method takes a website (database) and a query word and returns search results of the query word
# on the given database via bing's search api
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
    for key in resDict:
        cache[key] = {}
        for query in resDict[key][:3]:
            print query
            result = getBingResult(website, query)
            cache[key][query] = {
                'matches': float(result['WebTotal']),
                'urls': set([result['Url'] for result in result['Web']])
            }
    return cache

# using two threshold values tc and ts, the database is classified to a particular category
# if it successfully finds a category, it tries to further classify the database to a
# more precise domain. Lastly it collects the neccessary bunch of urls required to
# prepare content summaries
def classify(website, tc, ts):
    categories = ["Root"]
    data = {}
    for category in categories:
        keys = GRAPH.get(category)
        if keys:
            cache = getResults(website, 'resources/' + category + '.pickle')
            data.update(cache)
            covDict = categoryCoverage(cache)
            specDict = specificity(covDict)
            for key in covDict:
                print key + ": Specificity - " + `specDict[key]` + ", Coverage - " + `covDict[key]`
                if (covDict[key] >= tc and specDict[key] >= ts):
                    print "Adding " + key + " to Categories"
                    categories.append(key)
    classification = categories[0]
    classification = [classification + "/" + category for category in categories if category != "Root"]
    print website + ": " + classification

    urlDict = getUrls(categories, data)
    return urlDict

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

# based on categories stitch url sets and form separate url sets according to
# sub-categorisation (since a set of urls is formed, no duplicate urls will be present)
def getUrls(categories, data):
    urlDict = {}
    urlSet = set()
    for key in data:
        for query in data[key]:
            urlSet = urlSet.union(data[key][query]["urls"])
    urlDict["Root"] = urlSet
    if len(categories) > 1:
        urlSet = set()
        category = categories[1]
        keys = GRAPH.get(category)
        for key in keys:
            #urlSet = [urlSet.union(data[key][query]["urls"]) for query in data[key]]
            for query in data[key]:
                urlSet = urlSet.union(data[key][query]["urls"])
        urlDict[category] = urlSet
    return urlDict

# prepare contentSummaries
def getContentSummary():
    urlDict = classify('fifa.com', 10000, 0.7)
    for key in urlDict:
        print "Fetching " + `len(urlDict[key])` + " documents for category '" + key + "'"
        vocabList = [getVocab(url) for url in urlDict[key]]
        completeVocab = reduce(lambda a,b:a.union(b), vocabList, set())
        writeToFile(getDocFrequency(vocabList, completeVocab), key + '-contentSummary.txt')
    print "...Completed!!"

# gets the entire vocabulary from the contents of the given url (this includes
# cleaning and pre-processing the contents)
def getVocab(url):
    content = getPageContent(url)
    if content:
        end = content.find("\nReferences\n")
        content = content[:end] if (end > 0) else content
        content = re.sub(r'\[(.*?)\]', '', re.sub(r'\n', "", content))
        vocab = set([w.lower() for w in re.split(r'\W+', content) if str.isalpha(w)])
    return vocab

# to keep the file associated with every url unique the files are stored with names
# as hash value of their urls. If the same url is fetched again, the contents of the
# previously created file with that same url is read.
def getPageContent(url):
    print "Crawling through : " + url
    fname = "cache/documents/" + sha256(url).hexdigest()
    output = None
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            output = f.read()
    else:
        p = Popen(["lynx", "--dump", url], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        if output:
            with open(filename, 'w') as f:
                output = f.write(output)
    return output


def writeToFile(wordMap, filename):
    with open(filename, 'w') as f:
        for word, count in sorted(wordMap.iteritems()):
            f.write("{0}#{1}#-1.0\n".format(word, count))

def getDocFrequency(vocabList, completeVocab):
    docFreq = dict.fromkeys(completeVocab, 0)
    for word in completeVocab:
        docFreq[word] = sum([1 for vocab in vocabList if word in vocab])
    return docFreq

#getResults('fifa.com', 'resources/Root.pickle')
#getVocabList()
#print classify('fifa.com', 10000, 0.7)
getContentSummary()
