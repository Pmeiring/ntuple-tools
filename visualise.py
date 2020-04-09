
import ROOT
import os, shutil
from array import array
ROOT.gROOT.SetBatch(True)
from ROOT import TH1D, TLegend
from ROOT import gDirectory, TCanvas, gStyle

file = ROOT.TFile( '/eos/user/j/jheikkil/www/triggerStudies/histos_ele_flat2to100_PU200_eg_v5.root', 'read' )

version = 'v5'

outputDir = '/eos/user/j/jheikkil/www/triggerStudies/'+version+'/'

if os.path.isdir(outputDir)==False:
    os.mkdir(outputDir)
    shutil.copy('/eos/user/j/jheikkil/www/index.php', outputDir)    

tps_s = ['all'] #, 'Pt10EtaDE', 'Pt10EtaBC', 'Pt20EtaDE', 'Pt20EtaBC'] #'Pt10', 'Pt20', 'EtaDE', 'EtaBC', 'Pt10EtaDE', 'Pt10EtaBC', 'Pt20EtaDE', 'Pt20EtaBC']
gen_s = ['GEN'] #, 
         #'GENPt0to5', 'GENPt5to10', 'GENPt10to15', 'GENPt15to20', 'GENPt20to30', 'GENPt30to40', 'GENPt40', 'GENPt20', 
         #'GENEtaDE', 'GENEtaBC', 
         #'GENEtaDEGENPt0to5', 'GENEtaDEGENPt5to10', 'GENEtaDEGENPt10to15', 'GENEtaDEGENPt15to20', 'GENEtaDEGENPt20to30', 'GENEtaDEGENPt30to40', 'GENEtaDEGENPt40', 'GENEtaDEGENPt20', 
         #'GENEtaBCGENPt0to5', 'GENEtaBCGENPt5to10', 'GENEtaBCGENPt10to15', 'GENEtaBCGENPt15to20', 'GENEtaBCGENPt20to30', 'GENEtaBCGENPt30to40', 'GENEtaBCGENPt40', 'GENEtaBCGENPt20']

variables = ['HoE', 'abseta', 'bdtEg', 'coreshowlenght', 'eMaxOverE', 'energy', 
             'firstlayer', 'layer10', 'layer50', 'layer90', 'maxlayer', 'meanZ', 'nclu', 
              'npt05', 'npt20', 'ntc67', 'ntc90', 'phi', 'pt', 'sEtaEtaMax', 'sEtaEtaTot',
              'sPhiPhiMax', 'sPhiPhiTot', 'sRRMax', 'sRRMean', 'sRRTot', 'sZZ', 'showlenght']
             #'bdtPU', 'bdtPi','iso0p2', 'isoRel0p2', 'eta', 'ncluVpt'

current = ['coreshowlenght', 'firstlayer', 'maxlayer', 'showlenght',
            'sEtaEtaTot', 'sPhiPhiTot', 'sRRMean', 'sRRTot', 'sZZ']


cluster=True
dir = ''
tp_name = ''
tp_sel = ''
gen_sel = ''

if cluster == True:
    tp_name = 'h_cl3d_HMvDR'
    dir = 'Cluster3DHistos/'	    
else:
    gen_num = 'h_effNum_HMvDR'
    gen_denom = 'h_effDen_HMvDR'
    dir = 'GenParticleHistos/'

histo_name = '{}_{}_{}'.format(tp_name, tp_sel, gen_sel)
histo_name_NOMATCH = '{}_{}_{}_{}'.format(tp_name, tp_sel, gen_sel, "noMatch")
output = ''
#print histo_name
#print histo_name_NOMATCH

c = TCanvas("c", "canvas", 800, 800)
c.cd()


for tp_sel in tps_s:
    print tp_sel
    for gen_sel in gen_s:
        print gen_sel
        for variable in variables:
            histo_name = '{}_{}_{}_{}'.format(tp_name, tp_sel, gen_sel, variable)
            histo_name_NOMATCH = '{}_{}_{}_{}_{}'.format(tp_name, tp_sel, gen_sel, "noMatch", variable)
            if variable in current:
                output = histo_name+"_current.png"
            else:
                output = histo_name+"_new.png"
            print histo_name
            print histo_name_NOMATCH
            matched = file.Get(dir+'/'+histo_name)
            NOmatched = file.Get(dir+'/'+histo_name_NOMATCH)

            matched.Scale(1.0/matched.Integral(), "width")
            NOmatched.Scale(1.0/NOmatched.Integral(), "width")           

            matched.SetLineColor(1)
            matched.SetLineWidth(3)
  
            NOmatched.SetLineColor(2)
            NOmatched.SetLineWidth(3)

            x1 = 0.15
            x2 = x1 + 0.24
            y2 = 0.90
            y1 = 0.79
            legend = TLegend(x1,y1,x2,y2)
            legend.SetFillStyle(0)
            legend.SetBorderSize(0)
            legend.SetTextSize(0.041)
            legend.SetTextFont(42)
            legend.AddEntry(matched, "Signal",'L')
            legend.AddEntry(NOmatched, "Background",'L')


            #c.SetLogy(0)

            if variable in ['showlenght', 'maxlayer', 'coreshowlenght']:
               matched.GetXaxis().SetRangeUser(0.0,50)
               NOmatched.GetXaxis().SetRangeUser(0.0,50)

            if variable in ['ntc67']:
               matched.GetXaxis().SetRangeUser(0.0,40)
               NOmatched.GetXaxis().SetRangeUser(0.0,40)
  
            if variable in ['ntc90']:
               matched.GetXaxis().SetRangeUser(0.0,70)
               NOmatched.GetXaxis().SetRangeUser(0.0,70)



            if variable in ['meanZ']:
               matched.GetXaxis().SetRangeUser(300,400)
               NOmatched.GetXaxis().SetRangeUser(300,400)

            if variable in ['layer10']:
               matched.GetXaxis().SetRangeUser(0.0,20)
               NOmatched.GetXaxis().SetRangeUser(0.0,20)


            if variable in ['layer50', 'layer90']:
               matched.GetXaxis().SetRangeUser(0.0,40)
               NOmatched.GetXaxis().SetRangeUser(0.0,40)

            if variable in ['sRRMax', 'sRRMean', 'sRRTot']:
               matched.GetXaxis().SetRangeUser(0.0,0.03)
               NOmatched.GetXaxis().SetRangeUser(0.0,0.03)
 
            if variable in ['sPhiPhiTot', 'sPhiPhiMax']:
               matched.GetXaxis().SetRangeUser(0.0,0.2)
               NOmatched.GetXaxis().SetRangeUser(0.0,0.2)
 

            if matched.GetMaximum()>NOmatched.GetMaximum() or 'bdtEg' in variable:
                matched.Draw()
                NOmatched.Draw("SAME")
            else:
                NOmatched.Draw()
                matched.Draw("SAME")
            legend.Draw() 

            gStyle.SetOptStat(0)#("ne")
            c.SaveAs(outputDir+output)

            #if 'bdtEg' in variable:
            #    c.SetLogy()    
            #    output = histo_name+"_log.png"
            #    c.SaveAs(outputDir+output)
            #output = histo_name+"_log.png"
            #c.SetLogy()
            #NOmatched.Draw()
            #matched.Draw("SAME")
            #legend.Draw()
            #c.SaveAs(outputDir+output) 
        
c.Close()

#dir = file.GetDirectory("Cluster3DHistos")
#file.cd("Cluster3DHistos")
#dir.cd()
#gDirectory.ls()
#file.Reset()
#file.SetDirectory(0)
#dirList = file.GetListOfKeys()
#print dirList
#file.cd("Cluster3DHistos")
#file.GetListOfKeys().Print()
#for key in file.GetListOfKeys():
#    print "-------------------------"
#    kname = key.GetName()
#    print kname
#    hists = key.ReadObj().GetListOfKeys()
#    for histo in hists:
#        print histo.GetName()
    #key.ls()	
    #key.ReadObj().GetName()
    #kname.GetList()
    #for hah in key.GetListOfKeys():
    #    print "jes"
    #   print histo.GetName()
