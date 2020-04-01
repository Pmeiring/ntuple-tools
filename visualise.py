import ROOT
from array import array
ROOT.gROOT.SetBatch(True)
from ROOT import TH1D
from ROOT import gDirectory


file = ROOT.TFile( '/eos/user/j/jheikkil/www/triggerStudies/histos_ele_flat2to100_PU200_eg_v1.root', 'read' )
#    hist_400 = file.Get(hist_name_400)

dir = file.GetDirectory("Cluster3DHistos")
#file.cd("Cluster3DHistos")
dir.cd()
#gDirectory.ls()
#file.Reset()
#file.SetDirectory(0)
#dirList = file.GetListOfKeys()
#print dirList
#file.cd("Cluster3DHistos")
#file.GetListOfKeys().Print()
for key in file.GetListOfKeys():
    kname = key.GetName()
    print kname
    hists = key.ReadObj().GetListOfKeys()
    for histo in hists:
        print histo.GetName()
    #key.ls()	
    #key.ReadObj().GetName()
    #kname.GetList()
    #for hah in key.GetListOfKeys():
    #    print "jes"
    #   print histo.GetName()
