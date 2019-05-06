#!/bin/bash

## EDIT BELOW
DESTINATION=/eos/cms/store/cmst3/user/yiiyama/hgcal_trig
#DESTINATION=gsiftp://se01.cmsaf.mit.edu:2811/cms/store/user/yiiyama/gridpanda
LOGDIR=/afs/cern.ch/work/y/yiiyama/gridpanda
JDLTEMPLATE=cern.sh
## EDIT ABOVE

for ARG in $@
do
  case $ARG in
    -t)
      TEST=true
      shift
      ;;
    -i)
      TEST=interactive
      shift
      ;;
    -h)
      echo "Usage: submit.sh [-t|-i] (gen|fullsim|fullsimmini) TASKNAME [NEVENTS] [NJOBS]"
      exit 0
      ;;
  esac
done

TASKTYPE=$1 # gen, fullsim, fullsimmini
TASKNAME=$2 # confs subdirectory
NEVENTS=$3
NJOBS=$4

function exitmsg() {
  echo $1
  exit $2
}

[ $TASKTYPE ] || exitmsg "Usage: submit.sh (gen|fullsim|fullsimmini) TASKNAME NEVENTS NJOBS" 0

export X509_USER_PROXY=$PWD/x509up_u$(id -u)
if ! [ -e $X509_USER_PROXY ] || [ $(voms-proxy-info --timeleft --file $X509_USER_PROXY) -lt $((3600*24)) ]
then
  voms-proxy-init --valid 192:00 -voms cms --out $X509_USER_PROXY || exit 1
fi

TASKDIR=$(cd $(dirname $(readlink -f $0)); pwd)
EXECUTABLE=gridpanda.sh

source $TASKDIR/confs/$TASKNAME/conf.sh || exit 1
# conf.sh can set the following parameters (*=required for all confs, -=required if TASKTYPE is fullsim or fullsimmini, .=depends on the conf, o=optional):
#  o GEN_ARCH: SCRAM arch for the gensim step
#  . GEN_CAMPAIGN: Production campaign for the gensim step. Required if TASKTYPE is gen
#  . GEN_RELEASE: CMSSW release (full name) for the gensim step. Necesssary if campaign is not mapped in campaign_releases.json
#  . GEN_CMSSW: Name of the custom CMSSW tarball
#  o MINIAOD_ARCH: SCRAM arch for the miniaodsim step
#  - MINIAOD_CAMPAIGN: Production campaign for the miniaod step. If one of the standard campaigns, gen, rawsim, and recosim campaigns can be inferred from the map
#  . MINIAOD_RELEASE: CMSSW release (full name) for the rawsim, recosim, and miniaodsim steps. Necesssary if campaign is not mapped in campaign_releases.json
#  . MINIAOD_CMSSW: Name of the custom CMSSW tarball
#  o RECO_ARCH: SCRAM arch for the rawsim and recosim steps
#  . RECO_CAMPAIGN: CMSSW release (full name) for the rawsim, recosim, and miniaodsim steps. Necesssary if campaign is not mapped in campaign_releases.json
#  . RECO_RELEASE: CMSSW release (full name) for the rawsim, recosim, and miniaodsim steps. Necesssary if campaign is not mapped in campaign_releases.json
#  . RECO_CMSSW: Name of the custom CMSSW tarball
#  o PANDA_VERSION: Panda version
#  o PANDA_CMSSW: Custom tarball name
#  . MIXDATA: Name of the mixdata list file (minus .list.gz), if non-standard
#  . GRIDPACKS: Space-separated list of gridpack URLs
#  o MAXWALLTIME: Estimated maximum wall-clock time (in minutes) of the job. Setting a good value increases the chance of getting a slot.
#  o NCPU: Number of cores per job. Use 1 for powheg jobs.

CONFMAP=$TASKDIR/tools/read_confmap.py

if [ $TASKTYPE != "gen" ]
then
  [ $MINIAOD_CAMPAIGN ] || exitmsg "Missing MINIAOD_CAMPAIGN" 1
  [ $MINIAOD_ARCH ] || MINIAOD_ARCH=$($CONFMAP miniaod.${MINIAOD_CAMPAIGN}.arch)
  [ $MINIAOD_ARCH ] || exitmsg "Unknown MINIAOD_ARCH for non-standard campaign" 1
  [ $MINIAOD_RELEASE ] || MINIAOD_RELEASE=$($CONFMAP miniaod.${MINIAOD_CAMPAIGN}.release)
  [ $MINIAOD_RELEASE ] || exitmsg "Unknown MINIAOD_RELEASE for non-standard campaign" 1
  [ $RECO_CAMPAIGN ] || RECO_CAMPAIGN=$($CONFMAP miniaod.${MINIAOD_CAMPAIGN}.parent)
  [ $RECO_CAMPAIGN ] || exitmsg "Unknown RECO_CAMPAIGN for non-standard miniaod" 1
  [ $RECO_ARCH ] || RECO_ARCH=$($CONFMAP digireco.${RECO_CAMPAIGN}.arch)
  [ $RECO_ARCH ] || exitmsg "Unknown RECO_ARCH for non-standard campaign" 1
  [ $RECO_RELEASE ] || RECO_RELEASE=$($CONFMAP digireco.${RECO_CAMPAIGN}.release)
  [ $RECO_RELEASE ] || exitmsg "Unknown RECO_RELEASE for non-standard campaign" 1
  [ $GEN_CAMPAIGN ] || GEN_CAMPAIGN=$($CONFMAP digireco.${RECO_CAMPAIGN}.parent)
  [ $MIXDATA ] || MIXDATA=$($CONFMAP digireco.${RECO_CAMPAIGN}.mix)
  [ $MIXDATA ] || exitmsg "Unknown MIXDATA for non-standard campaign" 1
fi

[ $GEN_CAMPAIGN ] || exitmsg "Missing GEN_CAMPAIGN" 1
[ $GEN_ARCH ] || GEN_ARCH=$($CONFMAP gen.${GEN_CAMPAIGN}.arch)
[ $GEN_ARCH ] || exitmsg "Unknown GEN_ARCH for non-standard campaign" 1
[ $GEN_RELEASE ] || GEN_RELEASE=$($CONFMAP gen.${GEN_CAMPAIGN}.release)
[ $GEN_RELEASE ] || exitmsg "Unknown GEN_RELEASE for non-standard campaign" 1

if [ $PANDA_VERSION ]
then
  PANDA_ARCH=$($CONFMAP panda.${PANDA_VERSION}.arch)
  [ $PANDA_ARCH ] || exitmsg "Invalid PANDA_VERSION" 1
  PANDA_RELEASE=$($CONFMAP panda.${PANDA_VERSION}.release)
  [ $PANDA_CMSSW ] || PANDA_CMSSW=panda_${PANDA_VERSION}
fi

if [ "$TEST" = true ] || [ "$TEST" = interactive ]
then
  export LOCALTEST=1

  NCPU=1
  [ $NEVENTS ] || NEVENTS=100
  NJOBS=1
else
  if ! [ "$NEVENTS" ] || ! [ "$NJOBS" ]
  then
    echo "NEVENTS and NJOBS must be set for production run."
    exit 1
  fi

  export LOCALTEST=0

  [ $NCPU ] || NCPU=8
fi

if [ $NJOBS -gt 1000 ]
then
  echo "Don't submit more than 1000 jobs at a time - otherwise lumisection numbers will overlap"
  exit 1
fi

if [[ $DESTINATION =~ ^gsiftp: ]] || [[ $DESTINATION =~ ^srm: ]]
then
  MKDIRCMD="gfal-mkdir -p"
  LSCMD="gfal-ls"
else
  MKDIRCMD="mkdir -p"
  LSCMD="ls"
fi

$MKDIRCMD $DESTINATION/$TASKNAME
if [ $TASKTYPE = "fullsimmini" ]
then
  $MKDIRCMD $DESTINATION/$TASKNAME/miniaod
  $MKDIRCMD $DESTINATION/$TASKNAME/panda
fi

$LSCMD $DESTINATION/$TASKNAME > /dev/null
if [ $? -ne 0 ]
then
  echo "Could not create destination directory. Check your grid credentials."
  exit 1
fi

mkdir -p $LOGDIR/$TASKNAME

if [ "$TEST" = interactive ]
then
  rm -rf $LOGDIR/$TASKNAME/test
  mkdir $LOGDIR/$TASKNAME/test
fi

if [ -e $TASKDIR/certificates.tar.gz ]
then
  cp $TASKDIR/certificates.tar.gz $LOGDIR/$TASKNAME/certificates.tar.gz
else
  tar czf $LOGDIR/$TASKNAME/certificates.tar.gz -C /etc/grid-security certificates
fi

cp $TASKDIR/confs/$TASKNAME/conf.sh $LOGDIR/$TASKNAME/conf.sh

if [ $TASKTYPE != "gen" ]
then
  echo "MINIAOD_CAMPAIGN=$MINIAOD_CAMPAIGN" >> $LOGDIR/$TASKNAME/conf.sh
  echo "MINIAOD_ARCH=$MINIAOD_ARCH" >> $LOGDIR/$TASKNAME/conf.sh
  echo "MINIAOD_RELEASE=$MINIAOD_RELEASE" >> $LOGDIR/$TASKNAME/conf.sh
  echo "RECO_CAMPAIGN=$RECO_CAMPAIGN" >> $LOGDIR/$TASKNAME/conf.sh
  echo "RECO_ARCH=$RECO_ARCH" >> $LOGDIR/$TASKNAME/conf.sh
  echo "RECO_RELEASE=$RECO_RELEASE" >> $LOGDIR/$TASKNAME/conf.sh
  echo "MIXDATA=$MIXDATA" >> $LOGDIR/$TASKNAME/conf.sh
fi

echo "GEN_CAMPAIGN=$GEN_CAMPAIGN" >> $LOGDIR/$TASKNAME/conf.sh
echo "GEN_ARCH=$GEN_ARCH" >> $LOGDIR/$TASKNAME/conf.sh
echo "GEN_RELEASE=$GEN_RELEASE" >> $LOGDIR/$TASKNAME/conf.sh
if [ $PANDA_VERSION ]
then
  echo "PANDA_VERSION=$PANDA_VERSION" >> $LOGDIR/$TASKNAME/conf.sh
  echo "PANDA_ARCH=$PANDA_ARCH" >> $LOGDIR/$TASKNAME/conf.sh
  echo "PANDA_RELEASE=$PANDA_RELEASE" >> $LOGDIR/$TASKNAME/conf.sh
fi
echo "NCPU=$NCPU" >> $LOGDIR/$TASKNAME/conf.sh

INPUTFILES="$X509_USER_PROXY,$LOGDIR/$TASKNAME/certificates.tar.gz,$LOGDIR/$TASKNAME/conf.sh,$TASKDIR/tools/cmssw.sh,$TASKDIR/tools/cmssw_singularity.sh,$TASKDIR/confs/$TASKNAME/gen.py"

#INPUTFILES=$INPUTFILES,'/var/local/lcg-cp.tar.gz'

[ $PANDA_VERSION ] && INPUTFILES=$INPUTFILES,$TASKDIR/cmssw/${PANDA_CMSSW}.tar.gz

[ -e $TASKDIR/confs/$TASKNAME/gen.sh ] && INPUTFILES=$INPUTFILES,$TASKDIR/confs/$TASKNAME/gen.sh

if [ $TASKTYPE != "gen" ]
then
  [ $RECO_CMSSW ] && INPUTFILES=$INPUTFILES,$TASKDIR/cmssw/${RECO_CMSSW}.tar.gz
  [ $MINIAOD_CMSSW ] && INPUTFILES=$INPUTFILES,$TASKDIR/cmssw/${MINIAOD_CMSSW}.tar.gz
fi

[ $GEN_CMSSW ] && INPUTFILES=$INPUTFILES,$TASKDIR/cmssw/${GEN_CMSSW}.tar.gz

INPUTFILES=$INPUTFILES,$TASKDIR/pycfg/gen_cfg.py

if [ $TASKTYPE = "gen" ]
then
  INPUTFILES=$INPUTFILES
  [ $PANDA_VERSION ] && INPUTFILES=$INPUTFILES,$TASKDIR/pycfg/genpanda_${PANDA_VERSION}.py
  [ "$MAXWALLTIME" ] || MAXWALLTIME=180
elif [ $TASKTYPE = "fullsim" ] || [ $TASKTYPE = "fullsimmini" ]
then
  for STEP in rawsim recosim miniaodsim
  do
    INPUTFILES=$INPUTFILES,$TASKDIR/pycfg/${STEP}_cfg.py
  done
  INPUTFILES=$INPUTFILES,$TASKDIR/pycfg/rawsim_${RECO_CAMPAIGN}.py,$TASKDIR/pycfg/recosim_${RECO_CAMPAIGN}.py,$TASKDIR/pycfg/miniaodsim_${MINIAOD_CAMPAIGN}.py,$TASKDIR/mixdata/mixdata_${MIXDATA}.list.gz
  [ $PANDA_VERSION ] && INPUTFILES=$INPUTFILES,$TASKDIR/pycfg/panda_${PANDA_VERSION}.py
  [ "$MAXWALLTIME" ] || MAXWALLTIME=480
fi

if [ "$TEST" = interactive ]
then
  IFS_ORIG=$IFS
  IFS=","
  for FILE in $INPUTFILES
  do
    if [ -d $FILE ]
    then
      if [[ $FILE =~ /$ ]]
      then
        cp ${FILE}* $LOGDIR/$TASKNAME/test/
      else
        cp -r $FILE $LOGDIR/$TASKNAME/test/
      fi
    else
      cp $FILE $LOGDIR/$TASKNAME/test/
    fi
  done
  IFS="$IFS_ORIG"
  cp $TASKDIR/$EXECUTABLE $LOGDIR/$TASKNAME/test/
  chmod +x $LOGDIR/$TASKNAME/test/$EXECUTABLE

  echo "Job set up in $LOGDIR/$TASKNAME/test"
  echo "Execute:"
  echo "  DESTINATION='$DESTINATION' time ./$EXECUTABLE $TASKTYPE $TASKNAME $NEVENTS 12345 0"
  exit 0
fi

# environments that may be used in jdltemplate
export MAXWALLTIME
export REQUIRED_OS
if [[ $PANDA_ARCH =~ ^slc6 ]]
then
  REQUIRED_OS=rhel6
elif [[ $PANDA_ARCH =~ ^slc7 ]]
then
  REQUIRED_OS=rhel7
fi

JDL=$(mktemp)

echo 'universe = vanilla
executable = '$TASKDIR/$EXECUTABLE'
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files = '$INPUTFILES'
transfer_output_files = ""
output = '$LOGDIR/$TASKNAME/'$(ClusterId).$(Process).out
error = '$LOGDIR/$TASKNAME/'$(ClusterId).$(Process).err
log = '$LOGDIR/$TASKNAME/'$(ClusterId).$(Process).log
environment = "DESTINATION='$DESTINATION'"
request_cpus = '$NCPU'
rank = Mips
arguments = "'$TASKTYPE' '$TASKNAME' '$NEVENTS' $(ClusterId) $(Process)"
on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)
use_x509userproxy = True
x509userproxy = '$X509_USER_PROXY >> $JDL

$TASKDIR/jdls/$JDLTEMPLATE >> $JDL

echo "queue $NJOBS" >> $JDL

MSG=$(mktemp)
condor_submit $JDL | tee $MSG

CLUSTER=$(sed -n 's/.*submitted to cluster \([0-9]*\)./\1/p' $MSG)
rm $MSG
rm $JDL

[ $CLUSTER ] && ln -s $LOGDIR/$TASKNAME $LOGDIR/$CLUSTER
