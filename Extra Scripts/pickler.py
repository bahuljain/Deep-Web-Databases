# -*- coding: utf-8 -*-
import pickle

resPath = "resources/Root.pickle"

with open(resPath, 'rb') as handle:
  b = pickle.load(handle)

print b
