
import ROOT
import os, shutil
from array import array
ROOT.gROOT.SetBatch(True)
from ROOT import TH1D, TLegend
from ROOT import gDirectory, TCanvas, gStyle

file = ROOT.TFile( '/eos/user/j/jheikkil/www/triggerStudies/histos_ele_flat2to100_PU200_eg_v14.root', 'read' )
bkg_file = ROOT.TFile( '/eos/user/j/jheikkil/www/triggerStudies/histos_nugun_10_PU200_ng_bkg_v2.root', 'read' )

#bkg_file = ROOT.TFile( '/eos/user/j/jheikkil/www/triggerStudies/histos_ele_flat2to100_PU200_eg_v11.root', 'read' )


currentBDT = False

version = 'v12'

if currentBDT:
    hist_sig = ['h_cl3d_HMvDR_Pt10_GENPt20', 'h_cl3d_HMvDR_Pt10EtaBC_GENPt20' , 'h_cl3d_HMvDR_Pt10EtaDE_GENPt20'] #, 'h_cl3d_HMvDR_Pt10EtaBC_GENPt20', 'h_cl3d_HMvDR_Pt10EtaDE_GENPt20'] 
    hist_bkg = ['h_cl3d_HMvDR_Pt20_noMatch', 'h_cl3d_HMvDR_Pt20EtaBC_noMatch', 'h_cl3d_HMvDR_Pt20EtaDE_noMatch'] #, 'h_cl3d_HMvDR_Pt20EtaBC_GEN_noMatch', 'h_cl3d_HMvDR_Pt20EtaDE_GEN_noMatch']
else:
    hist_sig = ['h_cl3d_HMvDR_Pt5to30_GENPt5to20', 'h_cl3d_HMvDR_Pt5to30EtaBC_GENPt5to20' , 'h_cl3d_HMvDR_Pt5to30EtaDE_GENPt5to20'] 
    hist_bkg = ['h_cl3d_HMvDR_Pt5to20_noMatch', 'h_cl3d_HMvDR_Pt5to20EtaBC_noMatch', 'h_cl3d_HMvDR_Pt5to20EtaDE_noMatch']
    version = version+'_lowPt'

#hist_bkg = ['h_cl3d_HMvDR_Pt20_GEN_noMatch', 'h_cl3d_HMvDR_Pt20EtaBC_noMatch', 'h_cl3d_HMvDR_Pt20EtaDE_noMatch'] #, 'h_cl3d_HMvDR_Pt20EtaBC_GEN_noMatch', 'h_cl3d_HMvDR_Pt20EtaDE_GEN_noMatch']


outputDir = '/eos/user/j/jheikkil/www/triggerStudies/'+version+'/'

if os.path.isdir(outputDir)==False:
    os.mkdir(outputDir)
    shutil.copy('/eos/user/j/jheikkil/www/index.php', outputDir)



variables = ['HoE', 'abseta', 'bdtEg', 'coreshowlenght', 'eMaxOverE', 'energy', 'eta',
             'firstlayer', 'layer10', 'layer50', 'layer90', 'maxlayer', 'meanZ', 'nclu', 
              #'npt05', 'npt20', 
              'ntc67', 'ntc90', 'phi', 'pt', 'sEtaEtaMax', 'sEtaEtaTot',
              'sPhiPhiMax', 'sPhiPhiTot', 'sRRMax', 'sRRMean', 'sRRTot', 'sZZ', 'showlenght']
             #'bdtPU', 'bdtPi','iso0p2', 'isoRel0p2', 'eta', 'ncluVpt'

current = ['coreshowlenght', 'firstlayer', 'maxlayer', 'showlenght',
            'sEtaEtaTot', 'sPhiPhiTot', 'sRRMean', 'sRRTot', 'sZZ']

dir = 'Cluster3DHistos/'
output = ''
#print histo_name
#print histo_name_NOMATCH

c = TCanvas("c", "canvas", 800, 800)
c.cd()

numbers = [0, 1, 2]

for i in numbers:
        print i
        for variable in variables:
            histo_name = hist_sig[i]+"_"+variable
            histo_name_NOMATCH = hist_bkg[i]+"_"+variable

            if variable in current:
                if i==1:
                   output = variable+"_current_etaLow.png"
                elif i==2:
                   output = variable+"_current_etaHigh.png"
                else:
                   output = variable+"_current_inc.png"
            else:
                if i==1:
                   output = variable+"_new_etaLow.png"
       	       	elif i==2:
       	       	   output = variable+"_new_etaHigh.png"
                else:
                   output = variable+"_new_inc.png"

            print histo_name
            print histo_name_NOMATCH
            matched = file.Get(dir+'/'+histo_name)
            NOmatched = bkg_file.Get(dir+'/'+histo_name_NOMATCH)

            matched.Scale(1.0/matched.Integral(), "width")
            NOmatched.Scale(1.0/NOmatched.Integral(), "width")           

            matched.SetLineColor(1)
            matched.SetLineStyle(1)
            matched.SetLineWidth(3)
  
            NOmatched.SetLineColor(2)
            NOmatched.SetLineStyle(1)
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
 

            if matched.GetMaximum()>NOmatched.GetMaximum():
                matched.Draw("HIST L")
                NOmatched.Draw("HIST LSAME")
            else:
                NOmatched.Draw("HIST L")
                matched.Draw("HIST L SAME")
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
file.Close()
bkg_file.Close()
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
