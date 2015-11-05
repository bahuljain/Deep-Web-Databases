# -*- coding: utf-8 -*-
import re
from subprocess import Popen, PIPE
import urllib2
import base64
import json
import pickle
from hashlib import sha256
import os

# this method takes a website (database) and a query word and returns search results of the query word
# on the given database via bing's search api
def getBingResult(website, query, accountKey):
    query = query.replace(' ','%20')
    bingUrl = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3a' + website + '%20' + query + '%27&$top=4&$format=JSON'
    accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
    headers = {'Authorization': 'Basic ' + accountKeyEnc}
    req = urllib2.Request(bingUrl, headers=headers)
    response = urllib2.urlopen(req)
    content = response.read()
    json_result = json.loads(content)
    return json_result['d']['results'][0]

# this method gets the results for every query word in the given category file and stores the number of
# matches for every word and the urls of the top 4 results
def getResults(website, resPath, accountKey):
    with open(resPath, 'rb') as handle:
        resDict = pickle.load(handle)
    cache = {}
    for key in resDict:
        cache[key] = {}
        for query in resDict[key]:
            print "Getting Results for Query: " + query
            result = getBingResult(website, query, accountKey)
            cache[key][query] = {
                'matches': float(result['WebTotal']),
                'urls': set([result['Url'] for result in result['Web']])
            }
    return cache

GRAPH = {
    "Root": ["Computers", "Health", "Sports"],
    "Computers": ["Hardware", "Programming"],
    "Sports": ["Basketball", "Soccer"],
    "Health": ["Diseases", "Fitness"]
}

# using two threshold values tc and ts, the database is classified to a particular category
# if it successfully finds a category, it tries to further classify the database to a
# more precise domain. Lastly it collects the neccessary bunch of urls required to
# prepare content summaries
def classify(website, tc, ts, accountKey):
    categories = ["Root"]
    data = {}
    classification = "Root"
    for category in categories:
        print "\nAdding " + category + " to Categories\n" if category != "Root" else ""
        keys = GRAPH.get(category)
        if keys:
            cache = getResults(website, 'resources/' + category + '.pickle', accountKey)
            data.update(cache)
            covDict = categoryCoverage(cache)
            specDict = specificity(covDict)
            print ''
            for key in covDict:
                print key + ": Specificity - " + `specDict[key]` + ", Coverage - " + `covDict[key]`
                if (covDict[key] >= tc and specDict[key] >= ts):
                    classification = classification + "/" + key
                    categories.append(key)
    print '\nClassifcation for ' + website + ': ' + classification + '\n'
    urlDict = getUrls(categories, data)
    return data, urlDict

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

# based on categories stitch url sets and form separate url set according to
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
            for query in data[key]:
                urlSet = urlSet.union(data[key][query]["urls"])
        urlDict[category] = urlSet
    return urlDict

# prepare contentSummaries
def getContentSummary():
    accountKey = raw_input("Enter Bing Account Key (by default - author's key): ")  or '2dyKIv94jDETd7ClbVKoHvJSWFJ73ZvZRc7rjpBdkG8'
    website = raw_input('Enter Database Name: ')
    tc = float(raw_input('Enter Coverage Threshold (by default - 100): ') or '100')
    ts = float(raw_input('Enter Specificity Threshold (by default - 0.6): ') or '0.6')

    data, urlDict = classify(website, tc, ts, accountKey)
    finalData = dict()
    for key in data:
        finalData.update(data[key])

    for key in urlDict:
        print "\nFetching " + `len(urlDict[key])` + " documents for category '" + key + "'\n"
        vocabList = [getVocab(url) for url in urlDict[key]]
        completeVocab = reduce(lambda a,b:a.union(b), vocabList, set())
        print '\nTotal Words in Content Summary of Category ' + key + ': ' + `len(completeVocab)` + '\n'
        writeToFile(getDocFrequency(vocabList, completeVocab), finalData, key + '-' + website + '.txt')
    print "...Completed!!"

# gets the entire vocabulary from the contents of the given url (this includes
# cleaning and pre-processing the contents)
def getVocab(url):
    content = getPageContent(url)
    vocab = set()
    if content:
        end = content.find("\nReferences\n")
        content = content[:end] if (end > 0) else content
        content = re.sub(r'\[(.*?)\]', '', re.sub(r'\n', "", content))
        vocab = set([w.lower() for w in re.split(r'\W+', content) if str.isalpha(w)])
    return vocab

cachePath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'cache/documents'))
# to keep the file associated with every url unique the files are stored with names
# as hash value of their urls. If the same url is fetched again, the contents of the
# previously created file with that same url is read.
def getPageContent(url):
    if not os.path.exists(cachePath):
        os.makedirs(cachePath)

    print "Crawling through : " + url
    fname = os.path.join(cachePath, sha256(url.encode("ascii", "ignore")).hexdigest())
    output = None
    if os.path.isfile(fname):
        with open(fname, 'r') as f:
            output = f.read()
    else:
        p = Popen(["lynx", "--dump", url], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        if output:
            with open(fname, 'w') as f:
                f.write(output)
    return output

resultPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'results'))
# this method writes the content summary in a text file
def writeToFile(wordMap, finalData, fname):
    if not os.path.exists(resultPath):
        os.makedirs(resultPath)

    with open(fname, 'w') as f:
        for word, count in sorted(wordMap.iteritems()):
            if word in finalData.keys():
                f.write("{0}#{1}#{2}\n".format(word, count, finalData[word]['matches']))
            else:
                f.write("{0}#{1}#-1.0\n".format(word, count))

# retrurns the document frequency of every word in completeVocab in vocabList which contains
# the vocabList of the individual documents.
def getDocFrequency(vocabList, completeVocab):
    docFreq = dict.fromkeys(completeVocab, 0)
    for word in completeVocab:
        docFreq[word] = float(sum([1 for vocab in vocabList if word in vocab]))
    return docFreq

#begin
getContentSummary()
