# -*- coding: utf-8 -*-
import urllib2
import base64
import json

def getResult():
    website = 'health.com'
    query = 'fitness'
    bingUrl = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3a' + website + '%20' + query + '%27&$top=4&$format=JSON'
    accountKey = '2dyKIv94jDETd7ClbVKoHvJSWFJ73ZvZRc7rjpBdkG8'
    accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
    headers = {'Authorization': 'Basic ' + accountKeyEnc}
    req = urllib2.Request(bingUrl, headers=headers)
    response = urllib2.urlopen(req)
    content = response.read()
    json_result = json.loads(content)
    
    results = json_result['d']['results'][0]['Web']
    urls = set([result['Url'] for result in results])
    print urls
    print ''

    matches = json_result['d']['results'][0]['WebTotal']
    print matches


getResult()
