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
for filename in /afs/cern.ch/work/j/jheikkil/tools/ntuple-tools/triggerResults/tmp/histos_ele_flat2to100_PU200_eg_v2_*.root; do
    echo ${filename}
    xrdcp ${filename} .
done
hadd -j 10 -k histos_ele_flat2to100_PU200_eg_v2.root `ls histos_ele_flat2to100_PU200_eg_v2_*.root`
retVal=$?
if [ $retVal -ne 0 ]; then
    echo "****** Error: hadd failed!"
    exit $retVal
fi
rm histos_ele_flat2to100_PU200_eg_v2_*.root
#mv histos_ele_flat2to100_PU200_eg_v2.root /afs/cern.ch/work/j/jheikkil/tools/ntuple-tools/triggerResults
