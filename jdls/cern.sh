#!/bin/bash

if [ "$REQUIRED_OS" = "rhel6" ]
then
  OSREQ='OpSysAndVer =?= "SLCern6"'
else
  OSREQ='OpSysAndVer =?= "CentOS7"'
fi

echo 'requirements = '$OSREQ'
+JobFlavour = "longlunch"
accounting_group = group_u_CMST3.all
+AccountingGroup = group_u_CMST3.all'
