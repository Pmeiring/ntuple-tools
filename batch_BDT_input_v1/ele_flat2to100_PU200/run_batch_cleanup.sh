#!/bin/bash

CLUSTERID=$1
PROCID=$2

echo "Runnin Cluster ${CLUSTERID} Job ${PROCID}"
BATCH_DIR=${PWD}
echo "Current dir: ${BATCH_DIR}"
cd /afs/cern.ch/work/j/jheikkil/tools/ntuple-tools
echo "Now in dir: ${PWD}"

hostname

source ./setup_lxplus.sh
source ./setVirtualEnvWrapper.sh
workon myTest

cd ${BATCH_DIR}
date
rm /eos/user/j/jheikkil/www/triggerStudies/tmp/histos_ele_flat2to100_PU200_eg_v1_*.root
#mv histos_ele_flat2to100_PU200_eg_v1.root /eos/user/j/jheikkil/www/triggerStudies
