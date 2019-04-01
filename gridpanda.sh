#!/bin/bash

TASKTYPE=$1
TASKNAME=$2
NEVENTS=$3
CLUSTERID=$4
PROCESSID=$5

source conf.sh

GRIDPACKS_ARG=
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

    GRIDPACKS_ARG="$GRIDPACKS_ARG gridpacks=$PWD/$GRIDPACK"
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

if [ "$(readlink /cvmfs/cms.cern.ch/SITECONF/local)" = "T3_US_OSG" ]
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

[ $GEN_CMSSW ] && mv ${GEN_CMSSW}.tar.gz gen_${GEN_RELEASE}.tar.gz

[ $PANDA_CMSSW ] || PANDA_CMSSW=panda_${PANDA_VERSION}
mv ${PANDA_CMSSW}.tar.gz panda_${PANDA_RELEASE}.tar.gz

mv gen.py _gen.py

if [ $TASKTYPE = "gen" ]
then

  echo ""
  echo "[GEN STEP]"

  if [ -e gen.sh ]
  then
    source gen.sh 
  else
    ./cmssw.sh $GEN_ARCH $GEN_RELEASE gen ncpu=$NCPU maxEvents=$NEVENTS randomizeSeeds=True firstLumi=$FIRSTLUMI $GRIDPACKS_ARG || exit $?
  fi

  mv genpanda_${PANDA_VERSION}.py panda_cfg.py
  mv output_files_gen.list input_files_panda.list

  echo ""
  echo "[PANDA STEP]"
  ./cmssw.sh $PANDA_ARCH $PANDA_RELEASE panda || exit $?

  cat input_files_panda.list | xargs rm

elif [ $TASKTYPE = "fullsim" ] || [ $TASKTYPE = "fullsimmini" ]
then

  [ $RECO_CMSSW ] && mv ${RECO_CMSSW}.tar.gz rawsim_${RECO_RELEASE}.tar.gz
  [ $MINIAOD_CMSSW ] && mv ${MINIAOD_CMSSW}.tar.gz miniaodsim_${MINIAOD_RELEASE}.tar.gz

  echo ""
  echo "[GEN STEP]"
  if [ -e gen.sh ]
  then
    source gen.sh
  else
    ./cmssw.sh $GEN_ARCH $GEN_RELEASE gen ncpu=$NCPU maxEvents=$NEVENTS randomizeSeeds=True firstLumi=$FIRSTLUMI simStep=True $GRIDPACKS_ARG || exit $?
  fi
 
  mv rawsim_${RECO_CAMPAIGN}.py _rawsim.py
  mv output_files_gen.list input_files_rawsim.list

  gunzip mixdata_${MIXDATA}.list.gz
  mv mixdata{_${MIXDATA},}.list

  echo ""
  echo "[RAW STEP]"
  for att in $(seq 0 9)
  do
    # this step can fail due to pileup IO error
    ./cmssw.sh $RECO_ARCH $RECO_RELEASE rawsim ncpu=$NCPU mixdata=$PWD/mixdata.list randomizeSeeds=True && break
  done
  RC=$?
  [ $RC -ne 0 ] && exit $RC

  cat input_files_rawsim.list | xargs rm

  # reuse the release area
  mv {raw,reco}sim_${RECO_RELEASE}

  mv recosim_${RECO_CAMPAIGN}.py _recosim.py
  mv output_files_rawsim.list input_files_recosim.list
  
  echo ""
  echo "[RECO STEP]"
  ./cmssw.sh $RECO_ARCH $RECO_RELEASE recosim ncpu=$NCPU randomizeSeeds=True || exit $?

  cat input_files_recosim.list | xargs rm

  mv miniaodsim_${MINIAOD_CAMPAIGN}.py _miniaodsim.py
  mv output_files_recosim.list input_files_miniaodsim.list
  
  echo ""
  echo "[MINIAOD STEP]"
  ./cmssw.sh $MINIAOD_ARCH $MINIAOD_RELEASE miniaodsim ncpu=$NCPU randomizeSeeds=True || exit $?

  cat input_files_miniaodsim.list | xargs rm

  mv panda_{${PANDA_VERSION},cfg}.py
  mv output_files_miniaodsim.list input_files_panda.list
  
  echo ""
  echo "[PANDA STEP]"
  ./cmssw.sh $PANDA_ARCH $PANDA_RELEASE panda || exit $?
  [ $TASKTYPE = "fullsim" ] && cat input_files_panda.list | xargs rm

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
