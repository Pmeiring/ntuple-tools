eval `scram runtime -sh`
source /cvmfs/cms.cern.ch/crab3/crab.sh
voms-proxy-init --voms cms --valid 168:00
cp /tmp/x509up_u49345 /afs/cern.ch/user/j/jheikkil
export X509_USER_PROXY=/afs/cern.ch/user/j/jheikkil/x509up_u49345 
echo $X509_USER_PROXY
