#!/bin/bash

ARCH=$1
RELEASE=$2
TAG=$3
shift 3
ARGS="$@"

source /cvmfs/cms.cern.ch/cmsset_default.sh

export SCRAM_ARCH=$ARCH

if [ -e ${TAG}_${RELEASE}.tar.gz ]
then
  scram p -n ${TAG}_${RELEASE} CMSSW ${RELEASE}
  cd ${TAG}_${RELEASE}
  tar xzf ../${TAG}_${RELEASE}.tar.gz

  if [ -d myext ]
  then
    # we have a custom external
    for EXT in $(ls myext)
    do
      cp myext/$EXT/$EXT.xml config/toolbox/$SCRAM_ARCH/tools/selected
      scram setup $EXT
    done
  fi
else
  scram p CMSSW ${RELEASE}
  cd ${RELEASE}
fi

eval `scram runtime -sh`

cd -

CFG=${TAG}_cfg.py

echo cmsRun $CFG $ARGS
cmsRun $CFG $ARGS
