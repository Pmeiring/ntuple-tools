#!/bin/bash

CLUSTERID=$1
PROCID=$2
ISTMP=$3
echo "Runnin Cluster ${CLUSTERID} Job ${PROCID}"
BATCH_DIR=${PWD}
echo "Current dir: ${BATCH_DIR}"
ls -l

OUTDIR=/afs/cern.ch/work/j/jheikkil/tools/ntuple-tools/triggerResults
if [ "${ISTMP}" == "true" ]; then
  OUTDIR=/afs/cern.ch/work/j/jheikkil/tools/ntuple-tools/triggerResults/tmp/
fi
cp histos_ele_flat2to100_PU200_*.root ${OUTDIR}
