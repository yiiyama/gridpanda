#!/bin/bash

if [ "$LOCALTEST" = 1 ]
then
  LOCALTEST_CLASSAD='+Submit_LocalTest = 30'
  REQUIREMENTS='requirements = isUndefined(GLIDEIN_Site)'
else
  REQUIREMENTS='requirements = Arch == "X86_64" && ( \
                   isUndefined(IS_GLIDEIN) || \
                   ( OSGVO_OS_STRING == "RHEL 6" && HAS_CVMFS_cms_cern_ch == True ) || \
                   ( HAS_SINGULARITY == true || GLIDEIN_REQUIRED_OS == "rhel6" ) || \
                   ( GLIDEIN_Site == "MIT_CampusFactory" && (BOSCOGroup == "bosco_cms") ) \
                 ) && \
                 '$($(dirname $0)/../tools/exclusions.py)
fi

if [ "$REQUIRED_OS" ]
then
  REQUIRED_OS_CLASSAD='+REQUIRED_OS = "'$REQUIRED_OS'"'
fi

echo ''"$REQUIREMENTS"'
+AccountingGroup = "analysis.'$(id -un)'"
+DESIRED_Sites = "T2_AT_Vienna,T2_BE_IIHE,T2_BE_UCL,T2_BR_SPRACE,T2_BR_UERJ,T2_CH_CERN,T2_CH_CERN_AI,T2_CH_CERN_HLT,T2_CH_CERN_Wigner,T2_CH_CSCS,T2_CH_CSCS_HPC,T2_CN_Beijing,T2_DE_DESY,T2_DE_RWTH,T2_EE_Estonia,T2_ES_CIEMAT,T2_ES_IFCA,T2_FI_HIP,T2_FR_CCIN2P3,T2_FR_GRIF_IRFU,T2_FR_GRIF_LLR,T2_FR_IPHC,T2_GR_Ioannina,T2_HU_Budapest,T2_IN_TIFR,T2_IT_Bari,T2_IT_Legnaro,T2_IT_Pisa,T2_IT_Rome,T2_KR_KISTI,T2_MY_SIFIR,T2_MY_UPM_BIRUNI,T2_PK_NCP,T2_PL_Swierk,T2_PL_Warsaw,T2_PT_NCG_Lisbon,T2_RU_IHEP,T2_RU_INR,T2_RU_ITEP,T2_RU_JINR,T2_RU_PNPI,T2_RU_SINP,T2_TH_CUNSTDA,T2_TR_METU,T2_TW_NCHC,T2_UA_KIPT,T2_UK_London_IC,T2_UK_SGrid_Bristol,T2_UK_SGrid_RALPP,T2_US_Caltech,T2_US_Florida,T2_US_MIT,T2_US_Nebraska,T2_US_Purdue,T2_US_UCSD,T2_US_Vanderbilt,T2_US_Wisconsin,T3_CH_CERN_CAF,T3_CH_CERN_DOMA,T3_CH_CERN_HelixNebula,T3_CH_CERN_HelixNebula_REHA,T3_CH_CMSAtHome,T3_CH_Volunteer,T3_US_HEPCloud,T3_US_NERSC,T3_US_OSG,T3_US_PSC,T3_US_SDSC"
+ProjectName = "CpDarkMatterSimulation"
+MaxWallTimeMins = '$MAXWALLTIME'
'"$REQUIRED_OS_CLASSAD"'
'"$LOCALTEST_CLASSAD"
