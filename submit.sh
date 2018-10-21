#!/bin/bash

## EDIT BELOW
DESTINATION=gsiftp://t3serv010.mit.edu:2811/scratch/yiiyama/gridpanda
LOGDIR=/work/yiiyama/cms/logs/gridpanda
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

TASKDIR=$(cd $(dirname $(readlink -f $0)); pwd)
EXECUTABLE=gridpanda.sh

source $TASKDIR/confs/$TASKNAME/conf.sh || exit 1
# conf.sh can set the following parameters (*=required for all confs, -=required if TASKTYPE is fullsim or fullsimmini, .=depends on the conf, o=optional):
#  * GEN_ARCH: scram arch for the gen step
#  * GEN_RELEASE: CMSSW release (full name) for the gen step
#  - RECO_ARCH: scram arch for the rawsim, recosim, and miniaodsim steps
#  - RECO_RELEASE: CMSSW release (full name) for the rawsim, recosim, and miniaodsim steps
#  * PANDA_ARCH: scram arch for the panda step
#  * PANDA_RELEASE: CMSSW release (full name) for the panda step
#  - MIXDATA: Name of the mixdata list file (minus .list.gz) when 
#  . GEN_CMSSW: CMSSW tarball name (minus .tar.gz) for the gen step, tarball found in the cmssw/ directory
#  . GRIDPACKS: Space-separated list of gridpack URLs
#  o MAXWALLTIME: Estimated maximum wall-clock time (in minutes) of the job. Setting a good value increases the chance of getting a slot.

if [ "$TEST" = true ] || [ "$TEST" = interactive ]
then
  LOCALTEST='+Submit_LocalTest = 30'
  REQUIREMENTS='requirements = isUndefined(GLIDEIN_Site)'
  REQUEST_CPUS=1
  [ $NEVENTS ] || NEVENTS=100
  NJOBS=1
else
  if ! [ "$NEVENTS" ] || ! [ "$NJOBS" ]
  then
    echo "NEVENTS and NJOBS must be set for production run."
    exit 1
  fi

  REQUIREMENTS='requirements = Arch == "X86_64" && ( \
                   isUndefined(IS_GLIDEIN) || \
                   ( OSGVO_OS_STRING == "RHEL 6" && HAS_CVMFS_cms_cern_ch == True ) || \
                   ( HAS_SINGULARITY == true || GLIDEIN_REQUIRED_OS == "rhel6" ) || \
                   ( GLIDEIN_Site == "MIT_CampusFactory" && (BOSCOGroup == "bosco_cms" || BOSCOGroup == "paus") ) \
                 ) && \
                 '$(./exclusions.py)
  REQUEST_CPUS=8
fi

if [ $NJOBS -gt 1000 ]
then
  echo "Don't submit more than 1000 jobs at a time - otherwise lumisection numbers will overlap"
  exit 1
fi

gfal-mkdir -p $DESTINATION/$TASKNAME
if [ $TASKTYPE = "fullsimmini" ]
then
  gfal-mkdir -p $DESTINATION/$TASKNAME/miniaod
  gfal-mkdir -p $DESTINATION/$TASKNAME/panda
fi

gfal-ls $DESTINATION/$TASKNAME > /dev/null
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

tar czf $LOGDIR/certificates.tar.gz -C /etc/grid-security certificates

INPUTFILES="/tmp/x509up_u$(id -u),/var/local/lcg-cp.tar.gz,$LOGDIR/certificates.tar.gz,$TASKDIR/cmssw.sh,$TASKDIR/confs/$TASKNAME/,$TASKDIR/cmssw/panda_${PANDA_RELEASE}.tar.gz"

if [ "$GEN_CMSSW" ] && [ -e $TASKDIR/cmssw/${GEN_CMSSW}.tar.gz ]
then
  INPUTFILES=$INPUTFILES,$TASKDIR/cmssw/${GEN_CMSSW}.tar.gz
fi

if [ $TASKTYPE = "gen" ]
then
  INPUTFILES=$INPUTFILES,$TASKDIR/pycfg/genpanda_${PANDA_RELEASE}.py
  [ "$MAXWALLTIME" ] || MAXWALLTIME=180
elif [ $TASKTYPE = "fullsim" ] || [ $TASKTYPE = "fullsimmini" ]
then
  INPUTFILES=$INPUTFILES,$TASKDIR/pycfg/rawsim_${RECO_RELEASE}.py,$TASKDIR/pycfg/recosim_${RECO_RELEASE}.py,$TASKDIR/pycfg/miniaodsim_${RECO_RELEASE}.py,$TASKDIR/pycfg/panda_${PANDA_RELEASE}.py,$TASKDIR/mixdata/mixdata_${MIXDATA}.list.gz
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
  echo "  DESTINATION='$DESTINATION' ./$EXECUTABLE $TASKTYPE $TASKNAME $NEVENTS 12345 0"
  exit 0
fi

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
'"$REQUIREMENTS"'
request_cpus = '$REQUEST_CPUS'
rank = Mips
arguments = "'$TASKTYPE' '$TASKNAME' '$NEVENTS' $(ClusterId) $(Process)"
on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)
use_x509userproxy = True
x509userproxy = /tmp/x509up_u'$(id -u)'
+AccountingGroup = "analysis.'$(id -un)'"
+REQUIRED_OS = "rhel6"
+DESIRED_Sites = "T2_AT_Vienna,T2_BE_IIHE,T2_BE_UCL,T2_BR_SPRACE,T2_BR_UERJ,T2_CH_CERN,T2_CH_CERN_AI,T2_CH_CERN_HLT,T2_CH_CERN_Wigner,T2_CH_CSCS,T2_CH_CSCS_HPC,T2_CN_Beijing,T2_DE_DESY,T2_DE_RWTH,T2_EE_Estonia,T2_ES_CIEMAT,T2_ES_IFCA,T2_FI_HIP,T2_FR_CCIN2P3,T2_FR_GRIF_IRFU,T2_FR_GRIF_LLR,T2_FR_IPHC,T2_GR_Ioannina,T2_HU_Budapest,T2_IN_TIFR,T2_IT_Bari,T2_IT_Legnaro,T2_IT_Pisa,T2_IT_Rome,T2_KR_KISTI,T2_MY_SIFIR,T2_MY_UPM_BIRUNI,T2_PK_NCP,T2_PL_Swierk,T2_PL_Warsaw,T2_PT_NCG_Lisbon,T2_RU_IHEP,T2_RU_INR,T2_RU_ITEP,T2_RU_JINR,T2_RU_PNPI,T2_RU_SINP,T2_TH_CUNSTDA,T2_TR_METU,T2_TW_NCHC,T2_UA_KIPT,T2_UK_London_IC,T2_UK_SGrid_Bristol,T2_UK_SGrid_RALPP,T2_US_Caltech,T2_US_Florida,T2_US_MIT,T2_US_Nebraska,T2_US_Purdue,T2_US_UCSD,T2_US_Vanderbilt,T2_US_Wisconsin,T3_CH_CERN_CAF,T3_CH_CERN_DOMA,T3_CH_CERN_HelixNebula,T3_CH_CERN_HelixNebula_REHA,T3_CH_CMSAtHome,T3_CH_Volunteer,T3_US_HEPCloud,T3_US_NERSC,T3_US_OSG,T3_US_PSC,T3_US_SDSC"
+ProjectName = "CpDarkMatterSimulation"
+MaxWallTimeMins = '$MAXWALLTIME'
'"$LOCALTEST"'
queue '$NJOBS | condor_submit | tee _message

CLUSTER=$(sed -n 's/.*submitted to cluster \([0-9]*\)./\1/p' _message)
rm _message

[ $CLUSTER ] && ln -s $LOGDIR/$TASKNAME $LOGDIR/$CLUSTER
