#!/bin/bash

TASKTYPE=$1
TASKNAME=$2
NEVENTS=$3
CLUSTERID=$4
PROCESSID=$5

source conf.sh

for GRIDPACK in $GRIDPACKS
do
  if [[ $GRIDPACK =~ http:// ]]
  then
    URL=$GRIDPACK
    GRIDPACK=$(basename "$URL")
    echo "Downloading $GRIDPACK from $URL"
    while true
    do
      wget -O $GRIDPACK "$URL"
      [ $(stat -c %s $GRIDPACK) -ne 0 ] && break
      sleep 60
    done
  elif [[ $GRIDPACK =~ srm:// ]] || [[ $GRIDPACK =~ gsiftp:// ]]
  then
    URL=$GRIDPACK
    GRIDPACK=$(basename "$URL")
    echo "Downloading $GRIDPACK from $URL"

    if which gfal-copy
    then
      COPYCMD="gfal-copy"
    else
      COPYCMD="lcg-cp -v -D srmv2 -b"
      if ! which lcg-cp
      then
        tar xzf lcg-cp.tar.gz
        export PATH=$PWD/lcg-cp:$PATH
        export LD_LIBRARY_PATH=$PWD/lcg-cp:$LD_LIBRARY_PATH
      fi
    fi

    while true
    do
      $COPYCMD "$URL" $GRIDPACK && break
      sleep 60
    done
  fi
done

if [ $CLUSTERID ] && [ $PROCESSID ]
then
  FIRSTLUMI=$(($(($CLUSTERID%100000))*1000+$PROCESSID+1))
  JOBID=$CLUSTERID.$PROCESSID
else
  FIRSTLUMI=1
  JOBID=test
fi

if [ $(readlink /cvmfs/cms.cern.ch/SITECONF/local) = "T3_US_OSG" ]
then
  mkdir SITECONF
  ln -s /cvmfs/cms.cern.ch/SITECONF/T2_US_MIT SITECONF/local
  export CMS_PATH=$PWD
fi

echo "[HOSTNAME]"
hostname
echo ""

tar xzf certificates.tar.gz

export X509_CERT_DIR=$PWD/certificates
export X509_USER_PROXY=$(ls x509up_u*)
export HOME=.

export PATH=/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:$PATH

echo "[ENV]"
env

echo ""
echo "[DIRECTORY CONTENT]"
ls -l

source /cvmfs/cms.cern.ch/cmsset_default.sh

mv gen{,_${GEN_RELEASE}}.py
if [ "$GEN_CMSSW" ]
then
  mv ${GEN_CMSSW}.tar.gz gen_${GEN_RELEASE}.tar.gz
fi

if [ $TASKTYPE = "gen" ]
then

  mv {gen,}panda_${PANDA_RELEASE}.py

  echo ""
  echo "[GEN STEP]"
  ./cmssw.sh $GEN_ARCH $GEN_RELEASE gen maxEvents=$NEVENTS outputFile=gen.root randomizeSeeds=True firstLumi=$FIRSTLUMI || exit $?

  echo ""
  echo "[PANDA STEP]"
  ./cmssw.sh $PANDA_ARCH $PANDA_RELEASE panda inputFiles=file:gen.root outputFile=panda.root || exit $?
  rm gen.root

elif [ $TASKTYPE = "fullsim" ] || [ $TASKTYPE = "fullsimmini" ]
then

  gunzip mixdata_${MIXDATA}.list.gz

  echo ""
  echo "[GEN STEP]"
  ./cmssw.sh $GEN_ARCH $GEN_RELEASE gen maxEvents=$NEVENTS outputFile=gen.root randomizeSeeds=True firstLumi=$FIRSTLUMI simStep=True || exit $?

  echo ""
  echo "[RAW STEP]"
  for att in $(seq 0 9)
  do
    # this step can fail due to pileup IO error
    ./cmssw.sh $RECO_ARCH $RECO_RELEASE rawsim inputFiles=file:gen.root outputFile=rawsim.root randomizeSeeds=True && break
  done
  [ $? -ne 0 ] && exit $?
  rm gen.root
  
  echo ""
  echo "[RECO STEP]"
  ./cmssw.sh $RECO_ARCH $RECO_RELEASE recosim inputFiles=file:rawsim.root outputFile=recosim.root randomizeSeeds=True || exit $?
  rm rawsim.root
  
  echo ""
  echo "[MINIAOD STEP]"
  ./cmssw.sh $RECO_ARCH $RECO_RELEASE miniaodsim inputFiles=file:recosim.root outputFile=miniaodsim.root randomizeSeeds=True || exit $?
  rm recosim.root
  
  echo ""
  echo "[PANDA STEP]"
  ./cmssw.sh $PANDA_ARCH $PANDA_RELEASE panda inputFiles=file:miniaodsim.root outputFile=panda.root || exit $?
  [ $TASKTYPE = "fullsim" ] && rm miniaodsim.root

fi

echo ""
echo "[STAGEOUT]"

if which gfal-copy
then
  COPYCMD="gfal-copy"
else
  COPYCMD="lcg-cp -v -D srmv2 -b"
  if ! which lcg-cp
  then
    tar xzf lcg-cp.tar.gz
    export PATH=$PWD/lcg-cp:$PATH
    export LD_LIBRARY_PATH=$PWD/lcg-cp:$LD_LIBRARY_PATH
  fi
fi

# DESTINATION is set by condor via the "environment" classad

if [ $TASKTYPE = "fullsimmini" ]
then
  for att in $(seq 0 10)
  do
    echo $COPYCMD file://$PWD/panda.root $DESTINATION/$TASKNAME/panda/$JOBID.root
    $COPYCMD file://$PWD/panda.root $DESTINATION/$TASKNAME/panda/$JOBID.root && break
    gfal-rm $DESTINATION/$TASKNAME/panda/$JOBID.root
    sleep 2
  done

  for att in $(seq 0 10)
  do
    echo $COPYCMD file://$PWD/miniaodsim.root $DESTINATION/$TASKNAME/miniaod/$JOBID.root
    $COPYCMD file://$PWD/miniaodsim.root $DESTINATION/$TASKNAME/miniaod/$JOBID.root && break
    gfal-rm $DESTINATION/$TASKNAME/miniaod/$JOBID.root
    sleep 2
  done
else
  for att in $(seq 0 10)
  do
    echo $COPYCMD file://$PWD/panda.root $DESTINATION/$TASKNAME/$JOBID.root
    $COPYCMD file://$PWD/panda.root $DESTINATION/$TASKNAME/$JOBID.root && break
    gfal-rm $DESTINATION/$TASKNAME/$JOBID.root
    sleep 2
  done
fi
