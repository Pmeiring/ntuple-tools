import utils as utils
import numpy as np
import math as m

def getPTinterval(pt):
    ipT=0
    pT_intervals = [0,5,10,20,30,40,50,1000]
    while ipT<len(pT_intervals)-1:
        if pt>=float(pT_intervals[ipT]) and pt<float(pT_intervals[ipT+1]):
            interv=str(pT_intervals[ipT]) + "_" + str(pT_intervals[ipT+1])
            return interv #e.g. "5_10" if pT==7 GeV
        ipT+=1

# There's freedom in which h_custom is passed (i.e. corresponding to specific objects/cases)
def Fill_GENtoL1Obj_CustomHists(genParticles, h_custom, L1Objects, dR_cone, useExtrapolatedGenCoords=False):

    if L1Objects.empty: return

    print "\n\n === NEW EVENT ==="

    getattr(h_custom,"h_nsimtracks").Fill(len(genParticles))
    getattr(h_custom,"h_nL1Objects").Fill(len(L1Objects))
    dR_cones = [0.025, 0.05, 0.1, 0.2, 0.3, 0.4, 1.0, 100]

    for iGP, GP in genParticles.iterrows():
        # print 'GEN ', iGP, ' pT,eta,phi = ',GP.pt, GP.eta, GP.phi

        # FOR THE USE OF GEN VARIABLES EXTRAPOLATED TO CALOSURFACE
        GP_eta=GP.eta
        GP_phi=GP.phi
        if useExtrapolatedGenCoords:
            GP_eta=GP.exeta
            GP_phi=GP.exphi
        pT_range = getPTinterval(GP.pt)


        # PERFORM THE GEN-L1OBJECT MATCHING
        idx_allmatches, idx_closestDRL1object, idx_highestPTL1object, idx_closestPTL1object = utils.do_all_matches(GP, L1Objects, dR_cones, useExtrapolatedGenCoords)
        # nclusters_dR =    {"0.025":0, "0.05":0, "0.1":0, "0.2":0, "0.3":0, "0.4":0, "1.0":0, "100":0}
        sumL1ObjectPT_dR ={"0.025":0, "0.05":0, "0.1":0, "0.2":0, "0.3":0, "0.4":0, "1.0":0, "100":0}

        for idx_L1Object, L1Object in L1Objects.iterrows():

            # COMPUTE DR (GEN,L1OBJECT)
            dR1 = np.sqrt( pow((L1Object.eta-GP_eta),2) + pow((L1Object.phi-GP_phi),2) )
            dR2 = np.sqrt( pow((L1Object.eta-GP_eta),2) + pow((L1Object.phi-np.sign(L1Object.phi)*2.*m.pi-GP_phi),2) )
            dR = min(dR1,dR2)
            # nClusters and pt in slices of dR
            for k,v in sumL1ObjectPT_dR.iteritems():
                if dR<float(k): 
                    # nclusters_dR[k]    +=int(1)
                    sumL1ObjectPT_dR[k]+=L1Object.pt
            
            # FILL HISTOGRAMS WITH EACH L1 OBJECT
            getattr(h_custom,"h_dR_any_GENpt_%s"%pT_range).Fill(dR)
            if idx_L1Object == idx_closestDRL1object[3]: #dR=0.2
                getattr(h_custom,"h_dR_closestdR_GENpt_%s"%pT_range).Fill(dR)
            if idx_L1Object == idx_highestPTL1object[3]: #dR=0.2
                getattr(h_custom,"h_dR_highestPT_GENpt_%s"%pT_range).Fill(dR)
            if idx_L1Object == idx_closestPTL1object[3]: #dR=0.2
                getattr(h_custom,"h_dR_closestPT_GENpt_%s"%pT_range).Fill(dR)                

        # L1Object multiplicity in slices of GEN pt 
        getattr(h_custom,"h_nL1Objects_pt_%s"%pT_range).Fill(len(idx_allmatches[3])) #dR=0.2

        # nClusters per SimTrack in slices of dR
        for k,v in nclusters_dR.iteritems():
            dR = k.replace(".","p")
            getattr(h_custom,"h_nclusters_dR%s"%dR).Fill(v)


            if len(idx_allmatches[k])!=0# only take the matched simtracks
                # print "filling dR%s with "%dR,pt_dR[k]/GP.pt, " where GP.pt = ",GP.pt
                getattr(self.h_custom["HMvDR_GEN"],"h_ptAllCl_over_ptGEN_vs_ptGEN_dR%s"%dR).Fill(GP.pt,(sumL1ObjectPT_dR[k]/GP.pt))






        # # =====================================================================================================================================
        # # =====================================================================================================================================

        #     # perform the GP->Cluster matching with each dR cone
        #     best_match_indexes_dR = {"0.025":{}, "0.05":{}, "0.1":{}, "0.2":{}, "0.3":{}, "0.4":{}, "1.0":{}, "100":{}}
        #     for k,v in best_match_indexes_dR.iteritems():
        #         dR=float(k)
        #         dummy_BMI={}
        #         dummy_AM ={}
        #         if not trigger3DClusters.empty:
        #             dummy_BMI, dummy_AM = utils.custom_match(genParticles[['exeta','exphi']],
        #                                                     genParticles['pt'],
        #                                                     trigger3DClusters[['eta', 'phi']],
        #                                                     trigger3DClusters['pt'],
        #                                                     deltaR=dR)
        #         best_match_indexes_dR[k]=dummy_BMI
        #         # print dR, dummy_BMI

        #     getattr(self.h_custom["HMvDR_GEN"],"h_nsimtracks").Fill(len(genParticles.index))
        #     getattr(self.h_custom["HMvDR_GEN"],"h_nclusters").Fill(len(trigger3DClusters.index))

        #     for iGP, GP in genParticles.iterrows():
        #         nclusters_dR =  {"0.025":0, "0.05":0, "0.1":0, "0.2":0, "0.3":0, "0.4":0, "1.0":0, "100":0}
        #         pt_dR =         {"0.025":0, "0.05":0, "0.1":0, "0.2":0, "0.3":0, "0.4":0, "1.0":0, "100":0}
        #         pT_intervals = [0,5,10,20,30,40,50,1000]
        #         nClusters_pT = 0

        #         # print iGP, GP.reachedEE

        #         getattr(self.h_custom["HMvDR_GEN"],"h_fBrem_vs_ptGEN").Fill(GP.pt,GP.fbrem)

        #         for iCL,CL in trigger3DClusters.iterrows():
        #             dR=deltar(CL.eta, CL.phi, GP.eta, GP.phi)

        #             # Count the number of clusters around this GP.
        #             if dR<0.2: nClusters_pT+=1

        #             # nClusters and pt in slices of dR
        #             for k,v in nclusters_dR.iteritems():
        #                 if dR<float(k): 
        #                     nclusters_dR[k]+=int(1)
        #                     pt_dR[k]+=CL.pt
        #                     # Check if this cluster is the best match to the simtrack
        #                     if iGP in best_match_indexes_dR[k]:
        #                         # print "best_match_indexes_dR[%s] = "%k, best_match_indexes_dR[k], "iGP=",iGP," iCL=",iCL
        #                         if iCL==best_match_indexes_dR[k][iGP]:
        #                             # print "found it"
        #                             dr = k.replace(".","p")
        #                             getattr(self.h_custom["HMvDR_GEN"],"h_ptBestCl_over_ptGEN_vs_ptGEN_dR%s"%dr).Fill(GP.pt,(CL.pt/GP.pt))

        #             # dR in slices of GEN pT
        #             ipT=0
        #             while ipT<len(pT_intervals)-1:
        #                 if GP.pt>=float(pT_intervals[ipT]) and GP.pt<float(pT_intervals[ipT+1]):
        #                     interv=str(pT_intervals[ipT]) + "_" + str(pT_intervals[ipT+1])
        #                     getattr(self.h_custom["HMvDR_GEN"],"h_dR_any_GENpt_%s"%interv).Fill(dR)

        #                     if iGP in best_match_indexes:
        #                         if iCL==best_match_indexes[iGP]:
        #                             getattr(self.h_custom["HMvDR_GEN"],"h_dR_GENpt_%s"%interv).Fill(dR)
        #                 ipT+=1

        #         # nClusters per SimTrack in slices of dR
        #         for k,v in nclusters_dR.iteritems():
        #             dR = k.replace(".","p")
        #             getattr(self.h_custom["HMvDR_GEN"],"h_nclusters_dR%s"%dR).Fill(v)
        #             # print iGP, best_match_indexes_dR[k]
        #             if iGP in best_match_indexes_dR[k]: # only take the matched simtracks
        #                 # print "filling dR%s with "%dR,pt_dR[k]/GP.pt, " where GP.pt = ",GP.pt
        #                 getattr(self.h_custom["HMvDR_GEN"],"h_ptAllCl_over_ptGEN_vs_ptGEN_dR%s"%dR).Fill(GP.pt,(pt_dR[k]/GP.pt))


        #         # nClusters per SimTrack in slices of GEN pt
        #         ipT=0
        #         while ipT<len(pT_intervals)-1:
        #             if GP.pt>=float(pT_intervals[ipT]) and GP.pt<float(pT_intervals[ipT+1]):
        #                 interv=str(pT_intervals[ipT]) + "_" + str(pT_intervals[ipT+1])
        #                 getattr(self.h_custom["HMvDR_GEN"],"h_nclusters_pt_%s"%interv).Fill(nClusters_pT)
        #             ipT+=1


        #     # dR GEN-GEN in slices of (leading GEN) pT
        #     if len(genParticles.index)==2:
        #         GP1=genParticles.iloc[0]
        #         GP2=genParticles.iloc[1]
        #         GPleading=GP1 if GP1.pt>GP2.pt else GP2
        #         dR=deltar(GP1.eta, GP1.phi, GP2.eta, GP2.phi)
        #         # print dR
        #         ipT=0
        #         while ipT<len(pT_intervals)-1:
        #             if GPleading.pt>=float(pT_intervals[ipT]) and GPleading.pt<float(pT_intervals[ipT+1]):
        #                 interv=str(pT_intervals[ipT]) + "_" + str(pT_intervals[ipT+1])
        #                 getattr(self.h_custom["HMvDR_GEN"],"h_dR_GENGENpt_%s"%interv).Fill(dR)
        #             ipT+=1
        # # =====================================================================================================================================
        # # =====================================================================================================================================
