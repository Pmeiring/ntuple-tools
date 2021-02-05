import utils as utils
import numpy as np
import math as m
from scipy.spatial import cKDTree

def getPTinterval(pt):
    ipT=0
    pT_intervals = [0,5,10,20,30,40,50,1000]
    while ipT<len(pT_intervals)-1:
        if pt>=float(pT_intervals[ipT]) and pt<float(pT_intervals[ipT+1]):
            interv=str(pT_intervals[ipT]) + "_" + str(pT_intervals[ipT+1])
            return interv #e.g. "5_10" if pT==7 GeV
        ipT+=1

def getnObjectsinCone(L1Objects, dR_cone, refindex):
    nmatched=0
    if L1Objects.empty:
        return nmatched
    refeta = L1Objects.loc[ refindex ]['eta'] # Check if refindex is panda/array index
    refphi = L1Objects.loc[ refindex ]['phi']
    for idx_L1Object, L1Object in L1Objects.iterrows():
        if idx_L1Object==refindex: continue
        dR1 = np.sqrt( pow((L1Object.eta-refeta),2) + pow((L1Object.phi-refphi),2) )
        dR2 = np.sqrt( pow((L1Object.eta-refeta),2) + pow((L1Object.phi-np.sign(L1Object.phi)*2.*m.pi-refphi),2) )
        dR = min(dR1,dR2)
        if dR<dR_cone:
            nmatched+=1
    return nmatched

# There's freedom in which h_custom is passed (i.e. corresponding to specific objects/cases)
def Fill_GENtoL1Obj_CustomHists(genParticles, h_custom, L1Objects, dR_cone, useExtrapolatedGenCoords=False):
    # print "==================="
    # print "\n\n==== NEW EVENT ===="
    # print "==================="
    # print('{:^8} {:^8} {:^8} {:^8} {:^8} {:^8} {:^8} {:^9} {:^9} {:^8}'.format("type","index", "pT", "eta", "phi", "dR", "z0", "chi2", "chi2red", "nStubs"))

    getattr(h_custom,"h_nsimtracks").Fill(len(genParticles))
    getattr(h_custom,"h_nL1Objects").Fill(len(L1Objects))
    # if L1Objects.empty: return

    dR_cones = [0.025, 0.05, 0.1, 0.2, 0.3, 0.4, 1.0, 100]

    for iGP, GP in genParticles.iterrows():
        # print "-------------------"
        # print "==================="
        # print('{:^8} {:^8} {:8.3f} {:> 8.4f} {:> 8.4f}'.format("SimTrk",iGP, GP.pt, GP.eta, GP.phi))

        # FOR THE USE OF GEN VARIABLES EXTRAPOLATED TO CALOSURFACE
        GP_eta=GP.eta
        GP_phi=GP.phi
        if useExtrapolatedGenCoords:
            GP_eta=GP.exeta
            GP_phi=GP.exphi
        pT_range = getPTinterval(GP.pt)

        getattr(h_custom,"h_simtrack_pT").Fill(GP.pt)

        # PERFORM THE GEN-L1OBJECT MATCHING
        idx_allmatches, idx_closestDRL1object, idx_highestPTL1object, idx_closestPTL1object = utils.do_all_matches(GP, L1Objects, dR_cones, useExtrapolatedGenCoords)
        nclusters_dR =    {"0.025":0, "0.05":0, "0.1":0, "0.2":0, "0.3":0, "0.4":0, "1.0":0, "100":0}
        sumL1ObjectPT_dR ={"0.025":0, "0.05":0, "0.1":0, "0.2":0, "0.3":0, "0.4":0, "1.0":0, "100":0}

        for idx_L1Object, L1Object in L1Objects.iterrows():

            # COMPUTE DR (GEN,L1OBJECT)
            dR1 = np.sqrt( pow((L1Object.eta-GP_eta),2) + pow((L1Object.phi-GP_phi),2) )
            dR2 = np.sqrt( pow((L1Object.eta-GP_eta),2) + pow((L1Object.phi-np.sign(L1Object.phi)*2.*m.pi-GP_phi),2) )
            dR = min(dR1,dR2)
            # nClusters and pt in slices of dR
            for k,v in sumL1ObjectPT_dR.iteritems():
                if dR<float(k): 
                    nclusters_dR[k]    +=int(1)
                    sumL1ObjectPT_dR[k]+=L1Object.pt

            if iGP==0:
                getattr(h_custom,"h_L1Object_pT").Fill(L1Object.pt)

            # if (dR<1): 
            #     print('{:^8} {:^8} {:8.3f} {:> 8.4f} {:> 8.4f} {:> 8.4f} {:> 8.4f} {:> 9.3f} {:> 9.4f} {:> 8.0f}'.format("Track",idx_L1Object, L1Object.pt, L1Object.eta, L1Object.phi, dR, L1Object.z0, L1Object.chi2, L1Object.chi2Red, L1Object.nStubs))
            
            # FILL HISTOGRAMS WITH EACH L1 OBJECT
            getattr(h_custom,"h_dR_any_GENpt_%s"%pT_range).Fill(dR)
            if idx_L1Object == idx_closestDRL1object[3]: #dR=0.2
                getattr(h_custom,"h_dR_closestdR_GENpt_%s"%pT_range).Fill(dR)
            if idx_L1Object == idx_highestPTL1object[3]: #dR=0.2
                getattr(h_custom,"h_dR_highestPT_GENpt_%s"%pT_range).Fill(dR)
            if idx_L1Object == idx_closestPTL1object[3]: #dR=0.2
                getattr(h_custom,"h_dR_closestPT_GENpt_%s"%pT_range).Fill(dR)                
      
            # Do this only for the L1Tracks
            if not useExtrapolatedGenCoords:
                if dR<0.05:
                   getattr(h_custom,"h_nStubs_allTracks_dR0p05_GENpt_%s"%pT_range).Fill(L1Object.nStubs) 
                   getattr(h_custom,"h_chi2Red_allTracks_dR0p05_GENpt_%s"%pT_range).Fill(L1Object.chi2Red) 
                   getattr(h_custom,"h_ptresolution_allTracks_dR0p05_GENpt_%s"%pT_range).Fill(L1Object.pt / GP.pt) 
                if idx_L1Object == idx_highestPTL1object[1]: #dR=0.05
                   getattr(h_custom,"h_nStubs_highestPT_dR0p05_GENpt_%s"%pT_range).Fill(L1Object.nStubs) 
                   getattr(h_custom,"h_chi2Red_highestPT_dR0p05_GENpt_%s"%pT_range).Fill(L1Object.chi2Red) 
                   getattr(h_custom,"h_ptresolution_highestPT_dR0p05_GENpt_%s"%pT_range).Fill(L1Object.pt / GP.pt)                 


        # L1Object multiplicity within dR=0.2 of GEN, in slices of GEN pt 
        getattr(h_custom,"h_nL1Objects_pt_%s"%pT_range).Fill(len(idx_allmatches[3])) 

        # nClusters per SimTrack in slices of dR
        for idR, dR_cone in enumerate(dR_cones):
            dR = str(dR_cone).replace(".","p")

            getattr(h_custom,"h_nL1Objects_dR%s"%dR).Fill(nclusters_dR[str(dR_cone)])
            if dR=="0p05":
                getattr(h_custom,"h_nL1Objects_dR0p05_vs_ptGEN").Fill(   GP.pt,    nclusters_dR[str(dR_cone)] )
                getattr(h_custom,"h_nL1Objects_dR0p05_vs_fbremGEN").Fill(GP.fbrem, nclusters_dR[str(dR_cone)] )

            if len(idx_allmatches[idR])!=0:# only take the matched simtracks
                getattr(h_custom,"h_ptAllCl_over_ptGEN_vs_ptGEN_dR%s"%dR).Fill(GP.pt,(sumL1ObjectPT_dR[str(dR_cone)] / GP.pt))
                getattr(h_custom,"h_ptHighestPT_over_ptGEN_vs_ptGEN_dR%s"%dR).Fill(GP.pt,( L1Objects.loc[ idx_highestPTL1object[idR] ]['pt'] / GP.pt))
                getattr(h_custom,"h_ptClosestPT_over_ptGEN_vs_ptGEN_dR%s"%dR).Fill(GP.pt,( L1Objects.loc[ idx_closestPTL1object[idR] ]['pt'] / GP.pt))
                getattr(h_custom,"h_ptClosestDR_over_ptGEN_vs_ptGEN_dR%s"%dR).Fill(GP.pt,( L1Objects.loc[ idx_closestDRL1object[idR] ]['pt'] / GP.pt))

                # L1Object multiplicity within dR=0.2 of GEN, as function of best matched L1Object pT 
                if idR==3: #dR=0.2
                    getattr(h_custom,"h_nL1Objects_ClosestdR_dR0p2").Fill( L1Objects.loc[ idx_closestDRL1object[idR] ]['pt'] , nclusters_dR[str(dR_cone)])
                    getattr(h_custom,"h_nL1Objects_HighestPT_dR0p2").Fill( L1Objects.loc[ idx_highestPTL1object[idR] ]['pt'] , nclusters_dR[str(dR_cone)])
                    getattr(h_custom,"h_nL1Objects_ClosestPT_dR0p2").Fill( L1Objects.loc[ idx_closestPTL1object[idR] ]['pt'] , nclusters_dR[str(dR_cone)])

                if idR==1: #dR=0.5
                    getattr(h_custom,"h_ptresponse_dR0p05_ptGEN").Fill(     GP.pt                     ,( L1Objects.loc[ idx_highestPTL1object[idR] ]['pt'] / GP.pt))
                    getattr(h_custom,"h_ptresponse_dR0p05_fbremGEN").Fill(  GP.fbrem                  ,( L1Objects.loc[ idx_highestPTL1object[idR] ]['pt'] / GP.pt))
                    getattr(h_custom,"h_ptresponse_dR0p05_nL1Objects").Fill(nclusters_dR[str(dR_cone)],( L1Objects.loc[ idx_highestPTL1object[idR] ]['pt'] / GP.pt))

