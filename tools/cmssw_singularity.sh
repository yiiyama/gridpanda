#!/bin/bash

ARCH=$1
RELEASE=$2
STEP=$3
shift 3
ARGS="$@"

if [[ $ARCH =~ ^slc6 ]]
then
  REQUIRED_OS=rhel6
elif [[ $ARCH =~ ^slc7 ]]
then
  REQUIRED_OS=rhel7
fi

OPTS="--bind $PWD --bind /cvmfs --pwd $PWD"
IMG="/cvmfs/singularity.opensciencegrid.org/cmssw/cms:$REQUIRED_OS"

singularity exec $OPTS $IMG $PWD/cmssw.sh $ARCH $RELEASE $STEP $ARGS || exit $?
