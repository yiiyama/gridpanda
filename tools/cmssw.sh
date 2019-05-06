#!/bin/bash

ARCH=$1
RELEASE=$2
STEP=$3
shift 3
ARGS="$@"

source /cvmfs/cms.cern.ch/cmsset_default.sh

export SCRAM_ARCH=$ARCH

WORKAREA=${STEP}_${RELEASE}

[ -e $WORKAREA ] || scram p -n $WORKAREA CMSSW ${RELEASE}
cd $WORKAREA

if [ -e ../${WORKAREA}.tar.gz ]
then
  tar xzf ../${WORKAREA}.tar.gz

  if [ -d myext ]
  then
    # we have a custom external
    for EXT in $(ls myext)
    do
      cp myext/$EXT/$EXT.xml config/toolbox/$SCRAM_ARCH/tools/selected
      scram setup $EXT
    done
  fi
fi

# in case the work area was renamed
scram b ProjectRename
eval `scram runtime -sh`

cd ..

if [ -e input_files_${STEP}.list ]
then
  while read LINE
  do
    ARGS="$ARGS inputFiles=file:$LINE"
  done < input_files_${STEP}.list
fi

ARGS="$ARGS outputFile=${STEP}.root"

CFG=${STEP}_cfg.py

echo cmsRun $CFG $ARGS
cmsRun $CFG $ARGS || exit $?

echo ${STEP}.root > output_files_${STEP}.list
