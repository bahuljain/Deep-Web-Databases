# -*- coding: utf-8 -*-
import urllib2
import base64
import json
website = 'health.com'
query = 'fans%20football'
bingUrl = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3a' + website + '%20' + query + '%27&$top=10&$format=JSON'
accountKey = '2dyKIv94jDETd7ClbVKoHvJSWFJ73ZvZRc7rjpBdkG8'
accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
headers = {'Authorization': 'Basic ' + accountKeyEnc}
req = urllib2.Request(bingUrl, headers=headers)
response = urllib2.urlopen(req)
content = response.read()
json_result = json.loads(content)
#print json_result['d']['results'][0]['WebTotal']
matches = json_result['d']['results'][0]['WebTotal']
print matches