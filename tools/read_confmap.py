#!/usr/bin/env python

import os
import sys
import json

keys = sys.argv[1].split('.')

with open(os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/campaign_releases.json') as source:
    maps = json.loads(source.read())

val = maps
for key in keys:
    try:
        val = val[key]
    except KeyError:
        sys.exit(1)

print val
