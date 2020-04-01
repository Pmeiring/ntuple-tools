#!/bin/bash

CLUSTERID=$1
PROCID=$2
echo $PATH
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
python analyzeHgcalL1Tntuple.py -f myselection.yaml -c BDT_input -s ele_flat2to100_PU200 -n -1 -o ${BATCH_DIR} -r ${PROCID} -b
