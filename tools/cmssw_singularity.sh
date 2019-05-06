#!/bin/bash

ARCH=$1
RELEASE=$2
STEP=$3
shift 3
ARGS="$@"

if [[ $ARCH =~ ^slc6 ]]
then
  REQUIRED_OS=rhel6
  REQUIRED_UNAME=el6
elif [[ $ARCH =~ ^slc7 ]]
then
  REQUIRED_OS=rhel7
  REQUIRED_UNAME=el7
else
  echo "Unknown ARCH: $ARCH"
  exit 1
fi

if [[ $(uname -r) =~ $REQUIRED_UNAME ]]
then
  $PWD/cmssw.sh $ARCH $RELEASE $STEP $ARGS || exit $?
else
  OPTS="--bind $PWD --bind /cvmfs --pwd $PWD"
  IMG="/cvmfs/singularity.opensciencegrid.org/cmssw/cms:$REQUIRED_OS"
  
  singularity exec $OPTS $IMG $PWD/cmssw.sh $ARCH $RELEASE $STEP $ARGS || exit $?
fi
