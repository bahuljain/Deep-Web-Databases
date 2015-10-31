# -*- coding: utf-8 -*- 
from deepWeb import DeepWebDatabase

databases = ['health.com','fifa.com','yahoo.com','diabetes.org','hardwarecentral.com']
for database in databases:
    print database + ': '
    d = DeepWebDatabase('Root', database)
    print 'Class : ' + d.classify(10000,0.6)
    print ''


