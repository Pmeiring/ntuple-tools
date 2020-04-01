#!/bin/bash

CLUSTERID=$1
PROCID=$2

echo "Runnin Cluster ${CLUSTERID} Job ${PROCID}"
BATCH_DIR=${PWD}
echo "Current dir: ${BATCH_DIR}"
# cd /afs/cern.ch/work/j/jheikkil/tools/ntuple-tools
# echo "Now in dir: ${PWD}"
#
hostname

tar xfz ntuple-tools.tar.gz

source ./setup_lxplus.sh
source ./setVirtualEnvWrapper.sh
workon myTest
# cd ${BATCH_DIR}
date
python runHarvesting.py -i /eos/user/j/jheikkil/www/triggerStudies/tmp/ -s histos_ele_flat2to100_PU200_eg_v1 -v v1 -o /eos/user/j/jheikkil/www/triggerStudies
