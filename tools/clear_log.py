#!/usr/bin/env python

LOGDIR = '/work/yiiyama/cms/logs/gridpanda'

import os
import sys
import htcondor
import classad

schedd = htcondor.Schedd()

job_ids = {}
for job in schedd.xquery(projection=['ClusterId', 'ProcId']):
    try:
        job_ids[job['ClusterId']].add(job['ProcId'])
    except KeyError:
        job_ids[job['ClusterId']] = set([job['ProcId']])

for link in os.listdir(LOGDIR):
    if not os.path.islink(LOGDIR + '/' + link):
        continue

    ilink = int(link)

    if ilink in job_ids:
        prefix = link + '.'
        for fname in os.listdir(LOGDIR + '/' + link):
            if not fname.startswith(prefix):
                continue

            procid = int(fname[len(prefix):fname.rfind('.')])
            if procid not in job_ids[ilink]:
                os.unlink(LOGDIR + '/' + link + '/' + fname)
    else:
        prefix = link + '.'
        for fname in os.listdir(LOGDIR + '/' + link):
            if fname.startswith(prefix):
                os.unlink(LOGDIR + '/' + link + '/' + fname)

        os.unlink(LOGDIR + '/' + link)
