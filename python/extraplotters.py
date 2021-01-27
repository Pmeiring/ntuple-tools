import ROOT
import l1THistos as histos
import utils as utils
import pandas as pd
import numpy as np
import clusterTools as clAlgo
import selections as selections
import math
from plotters import *

def wasMatchedToGEN(match_indices, clusteridx):
    print match_indices
    print "looking for cluster ",clusteridx
    for genIdx,clusterIdcs in match_indices.items():
        print clusterIdcs
        if clusteridx in clusterIdcs:
            return 1
    return 0

class Cluster3DPlotter_AddL1Tracks(BasePlotter):
    def __init__(self, tp_set, l1track_set, tp_selections=[selections.Selection('all')]):
        # self.tp_set = tp_set
        # self.tp_selections = tp_selections
        self.l1track_set=l1track_set
        self.h_tpset = {}
        super(Cluster3DPlotter_AddL1Tracks, self).__init__(tp_set, tp_selections)

    def book_histos(self):
        self.tp_set.activate()
        tp_name = self.tp_set.name
        for selection in self.tp_selections: 
            histo_name='{}_{}_noMatch'.format(tp_name, selection.name)
            #self.h_tpset[selection.name] = histos.HistoSetClusters(name='{}_{}_nomatch'.format(tp_name, selection.name))
            self.h_tpset[histo_name] = histos.HistoSet3DClusters(histo_name)

    def fill_histos(self, debug=False):
        for tp_sel in self.tp_selections:
            tcs = self.tp_set.tc_df
            cl2Ds = self.tp_set.cl2d_df
            cl3Ds = self.tp_set.cl3d_df
            L1tracks=self.l1track_set.df
            if not tp_sel.all:
                cl3Ds = self.tp_set.cl3d_df.query(tp_sel.selection)
            # debug = 4
            # utils.debugPrintOut(debug, '{}_{}'.format(self.tp_set.name, 'TCs'), tcs, tcs[:3])
            # utils.debugPrintOut(debug, '{}_{}'.format(self.tp_set.name, 'CL2D'), cl2Ds, cl2Ds[:3])
            # utils.debugPrintOut(debug, '{}_{}'.format(self.tp_set.name, 'CL3D'), cl3Ds, cl3Ds[:3])
            histo_name='{}_{}_noMatch'.format(self.tp_set.name, tp_sel.name)
            if not cl3Ds.empty:
                All3DClusters=cl3Ds
# ===========================
                # MATCH THE 3D CLUSTERS TO THE L1 TRACKS IN A DELTAR CONE
                L1Tk_match_indices = {}
                for idx, Cluster in All3DClusters.iterrows():
                    # If we have L1tracks, match them to 3Dclusters
                    # print "Do we have tracks? ", not L1tracks.empty
                    if not L1tracks.empty: 
                        # Perform the matching 3DCluster->L1track
                        # match_indices will contain for every cluster (index) the indices of matched L1tracks (sorted on pt of the L1tracks)
                        L1Tk_best_match_idx, L1Tk_match_indices = utils.match_3Dcluster_L1Tk(Cluster[['eta','phi']],
                                                                        Cluster['pt'],
                                                                        L1tracks[['eta', 'phi']],
                                                                        L1tracks['pt'],
                                                                        deltaR=0.2)
                        if L1Tk_best_match_idx==None:
                            All3DClusters.loc[idx,"tttrack_pt"]=-999.
                            All3DClusters.loc[idx,"tttrack_eta"]=-999.
                            All3DClusters.loc[idx,"tttrack_phi"]=-999.
                            All3DClusters.loc[idx,"tttrack_chi2"]=-999.
                            All3DClusters.loc[idx,"tttrack_nStubs"]=-999.
                        else:
                            All3DClusters.loc[idx,"tttrack_pt"]=L1tracks.loc[L1Tk_best_match_idx].pt
                            All3DClusters.loc[idx,"tttrack_eta"]=L1tracks.loc[L1Tk_best_match_idx].eta
                            All3DClusters.loc[idx,"tttrack_phi"]=L1tracks.loc[L1Tk_best_match_idx].phi
                            All3DClusters.loc[idx,"tttrack_chi2"]=L1tracks.loc[L1Tk_best_match_idx].chi2
                            All3DClusters.loc[idx,"tttrack_nStubs"]=L1tracks.loc[L1Tk_best_match_idx].nStubs
# ===========================


                for index, row in cl3Ds.iterrows():
                    self.h_tpset[histo_name].fill(row)



class GENto3DClusterMatch_AddL1Tracks(BasePlotter):
    def __init__(self, tp_set, l1track_set, gen_set,
                 tp_selections=[selections.Selection('all')], gen_selections=[selections.Selection('all')]):
        # self.tp_set = tp_set
        # self.tp_selections = tp_selections
        # self.gen_set = gen_set
        # self.gen_selections = gen_selections
        self.l1track_set=l1track_set
        self.h_tpset = {}
        self.h_resoset = {}
        self.h_effset = {}
        self.h_trackmatching = {}
        self.h_custom = {}        
        super(GENto3DClusterMatch_AddL1Tracks, self).__init__(tp_set, tp_selections, gen_set, gen_selections)

    def plot3DMatch(self,
                           genParticles, 
                           trigger3DClusters,
                           triggerClusters,
                           triggerCells,
                           L1tracks,
                           histoGen,
                           histoGenMatched,
                           histo3DClMatch,
                           histo3DClNOMatch,
                           histoTrackMatching,
                           algoname,
                           debug):
        def computeIsolation(all3DClusters, idx_best_match, idx_incone, dr):
            ret = pd.DataFrame()
            # print 'index best match: {}'.format(idx_best_match)
            # print 'indexes all in cone: {}'.format(idx_incone)
            components = all3DClusters[(all3DClusters.index.isin(idx_incone)) & ~(all3DClusters.index == idx_best_match)]
            # print 'components indexes: {}'.format(components.index)
            compindr = components[np.sqrt((components.eta-all3DClusters.loc[idx_best_match].eta)**2 + (components.phi-all3DClusters.loc[idx_best_match].phi)**2) < dr]
            if not compindr.empty:
                # print 'components indexes in dr: {}'.format(compindr.index)
                ret['energy'] = [compindr.energy.sum()]
                ret['eta'] = [np.sum(compindr.eta*compindr.energy)/compindr.energy.sum()]
                ret['pt'] = [(ret.energy/np.cosh(ret.eta)).values[0]]
            else:
                ret['energy'] = [0.]
                ret['eta'] = [0.]
                ret['pt'] = [0.]
            return ret

        def sumClustersInCone(all3DClusters, idx_incone, debug=0):
            components = all3DClusters[all3DClusters.index.isin(idx_incone)]
            ret = clAlgo.sum3DClusters(components)
            if debug > 0:
                print '-------- in cone:'
                print components.sort_values(by='pt', ascending=False)
                print '   - Cone sum:'
                print ret
            return ret

        # MATCH THE 3D CLUSTERS TO THE GENPARTICLES IN A DELTAR CONE
        All3DClusters = trigger3DClusters
        best_match_indexes = {}
        allmatches = {}
        if not trigger3DClusters.empty:
            # {0: array([0]), 1: array([1, 2])}
            # Means genPart 0 matched to ref 0
            best_match_indexes, allmatches = utils.custom_match(genParticles[['exeta','exphi']],
                                                            genParticles['pt'],
                                                            trigger3DClusters[['eta', 'phi']],
                                                            trigger3DClusters['pt'],
                                                            deltaR=0.2)

        # =====================================================================================================================================
        # =====================================================================================================================================
        # Fill the "custom Hists"
        dummysplit = histoGen.name_.split("_")
        targethist = dummysplit[2]+"_"+dummysplit[3]+"_"+dummysplit[4]
        # print histoGen.name_, targethist
        if "_EtaBCD_GENEtaBCD" in targethist:

            # perform the GP->Cluster matching with each dR cone
            best_match_indexes_dR = {"0.025":{}, "0.05":{}, "0.1":{}, "0.2":{}, "0.3":{}, "0.4":{}, "1.0":{}, "100":{}}
            for k,v in best_match_indexes_dR.iteritems():
                dR=float(k)
                dummy_BMI={}
                dummy_AM ={}
                if not trigger3DClusters.empty:
                    dummy_BMI, dummy_AM = utils.custom_match(genParticles[['exeta','exphi']],
                                                            genParticles['pt'],
                                                            trigger3DClusters[['eta', 'phi']],
                                                            trigger3DClusters['pt'],
                                                            deltaR=dR)
                best_match_indexes_dR[k]=dummy_BMI
                # print dR, dummy_BMI

            getattr(self.h_custom["HMvDR_GEN"],"h_nsimtracks").Fill(len(genParticles.index))
            getattr(self.h_custom["HMvDR_GEN"],"h_nclusters").Fill(len(trigger3DClusters.index))

            for iGP, GP in genParticles.iterrows():
                nclusters_dR =  {"0.025":0, "0.05":0, "0.1":0, "0.2":0, "0.3":0, "0.4":0, "1.0":0, "100":0}
                pt_dR =         {"0.025":0, "0.05":0, "0.1":0, "0.2":0, "0.3":0, "0.4":0, "1.0":0, "100":0}
                pT_intervals = [0,5,10,20,30,40,50,1000]
                nClusters_pT = 0

                # print iGP, GP.reachedEE

                getattr(self.h_custom["HMvDR_GEN"],"h_fBrem_vs_ptGEN").Fill(GP.pt,GP.fbrem)

                for iCL,CL in trigger3DClusters.iterrows():
                    dR=deltar(CL.eta, CL.phi, GP.eta, GP.phi)

                    # Count the number of clusters around this GP.
                    if dR<0.2: nClusters_pT+=1

                    # nClusters and pt in slices of dR
                    for k,v in nclusters_dR.iteritems():
                        if dR<float(k): 
                            nclusters_dR[k]+=int(1)
                            pt_dR[k]+=CL.pt
                            # Check if this cluster is the best match to the simtrack
                            if iGP in best_match_indexes_dR[k]:
                                # print "best_match_indexes_dR[%s] = "%k, best_match_indexes_dR[k], "iGP=",iGP," iCL=",iCL
                                if iCL==best_match_indexes_dR[k][iGP]:
                                    # print "found it"
                                    dr = k.replace(".","p")
                                    getattr(self.h_custom["HMvDR_GEN"],"h_ptBestCl_over_ptGEN_vs_ptGEN_dR%s"%dr).Fill(GP.pt,(CL.pt/GP.pt))

                    # dR in slices of GEN pT
                    ipT=0
                    while ipT<len(pT_intervals)-1:
                        if GP.pt>=float(pT_intervals[ipT]) and GP.pt<float(pT_intervals[ipT+1]):
                            interv=str(pT_intervals[ipT]) + "_" + str(pT_intervals[ipT+1])
                            getattr(self.h_custom["HMvDR_GEN"],"h_dR_any_GENpt_%s"%interv).Fill(dR)

                            if iGP in best_match_indexes:
                                if iCL==best_match_indexes[iGP]:
                                    getattr(self.h_custom["HMvDR_GEN"],"h_dR_GENpt_%s"%interv).Fill(dR)
                        ipT+=1

                # nClusters per SimTrack in slices of dR
                for k,v in nclusters_dR.iteritems():
                    dR = k.replace(".","p")
                    getattr(self.h_custom["HMvDR_GEN"],"h_nclusters_dR%s"%dR).Fill(v)
                    # print iGP, best_match_indexes_dR[k]
                    if iGP in best_match_indexes_dR[k]: # only take the matched simtracks
                        # print "filling dR%s with "%dR,pt_dR[k]/GP.pt, " where GP.pt = ",GP.pt
                        getattr(self.h_custom["HMvDR_GEN"],"h_ptAllCl_over_ptGEN_vs_ptGEN_dR%s"%dR).Fill(GP.pt,(pt_dR[k]/GP.pt))


                # nClusters per SimTrack in slices of GEN pt
                ipT=0
                while ipT<len(pT_intervals)-1:
                    if GP.pt>=float(pT_intervals[ipT]) and GP.pt<float(pT_intervals[ipT+1]):
                        interv=str(pT_intervals[ipT]) + "_" + str(pT_intervals[ipT+1])
                        getattr(self.h_custom["HMvDR_GEN"],"h_nclusters_pt_%s"%interv).Fill(nClusters_pT)
                    ipT+=1


            # dR GEN-GEN in slices of (leading GEN) pT
            if len(genParticles.index)==2:
                GP1=genParticles.iloc[0]
                GP2=genParticles.iloc[1]
                GPleading=GP1 if GP1.pt>GP2.pt else GP2
                dR=deltar(GP1.eta, GP1.phi, GP2.eta, GP2.phi)
                # print dR
                ipT=0
                while ipT<len(pT_intervals)-1:
                    if GPleading.pt>=float(pT_intervals[ipT]) and GPleading.pt<float(pT_intervals[ipT+1]):
                        interv=str(pT_intervals[ipT]) + "_" + str(pT_intervals[ipT+1])
                        getattr(self.h_custom["HMvDR_GEN"],"h_dR_GENGENpt_%s"%interv).Fill(dR)
                    ipT+=1
        # =====================================================================================================================================
        # =====================================================================================================================================


        # FILL HISTOGRAMS
        if histoGen is not None: 
            histoGen.fill(genParticles) 
        if histoTrackMatching is not None: 
            histoTrackMatching.fill(genParticles,L1tracks,trigger3DClusters)


        # MATCH THE 3D CLUSTERS TO THE L1 TRACKS IN A DELTAR CONE
        L1Tk_match_indices = {}
        for idx, Cluster in All3DClusters.iterrows():
            # If we have L1tracks, match them to 3Dclusters
            # print "Do we have tracks? ", not L1tracks.empty
            if not L1tracks.empty: 
                # Perform the matching 3DCluster->L1track
                # match_indices will contain for every cluster (index) the indices of matched L1tracks (sorted on pt of the L1tracks)
                L1Tk_best_match_idx, L1Tk_match_indices = utils.match_3Dcluster_L1Tk(Cluster[['eta','phi']],
                                                                Cluster['pt'],
                                                                L1tracks[['eta', 'phi']],
                                                                L1tracks['pt'],
                                                                deltaR=0.2)
                # print L1Tk_best_match_idx, L1Tk_match_indices


                if L1Tk_best_match_idx==None:
                    All3DClusters.loc[idx,"tttrack_pt"]=-999.
                    All3DClusters.loc[idx,"tttrack_eta"]=-999.
                    All3DClusters.loc[idx,"tttrack_phi"]=-999.
                    All3DClusters.loc[idx,"tttrack_chi2"]=-999.
                    All3DClusters.loc[idx,"tttrack_nStubs"]=-999.
                else:
                    All3DClusters.loc[idx,"tttrack_pt"]=L1tracks.loc[L1Tk_best_match_idx].pt
                    All3DClusters.loc[idx,"tttrack_eta"]=L1tracks.loc[L1Tk_best_match_idx].eta
                    All3DClusters.loc[idx,"tttrack_phi"]=L1tracks.loc[L1Tk_best_match_idx].phi
                    All3DClusters.loc[idx,"tttrack_chi2"]=L1tracks.loc[L1Tk_best_match_idx].chi2
                    All3DClusters.loc[idx,"tttrack_nStubs"]=L1tracks.loc[L1Tk_best_match_idx].nStubs

        # FIND ALL CLUSTERS THAT DID NOT MATCH TO A GENPARTICLE
        for match in allmatches.values():
            for k in match:
                All3DClusters = All3DClusters.drop(k)
        unmatchedClusters = All3DClusters

        # LOOP OVER ALL CLUSTERS
        # for index,row in All3DClusters.iterrows():
        #     # IF IT MATCHED TO GEN (WE HAVE TO FILL THE MATCHEDHISTO)
        #     if wasMatchedToGEN(allmatches, index):
        #         # IF IT MATCHED TO 0 L1TRACKS
        #         if len(L1Tk_match_indices)==0:
        #             histo3DClMatch.fill(row)
        #         # IF IT MATCHED TO 1 L1TRACKS
        #         if len(L1Tk_match_indices)==1:
        #             histo3DClMatch.fill(row, L1tracks.iloc[L1Tk_match_indices[index][0]])
        #         # ELSE
        #         if len(L1Tk_match_indices)>1:
        #             histo3DClMatch.fill(row, L1tracks.iloc[L1Tk_match_indices[index][0]], L1tracks.iloc[L1Tk_match_indices[index][0]])
        #     # ELSE (WE HAVE TO FILL THE UNMATCHEDHIST)
        #     else:
        #         # IF IT MATCHED TO 0 L1TRACKS
        #         if len(L1Tk_match_indices)==0:
        #             histo3DClNOMatch.fill(row)
        #         # IF IT MATCHED TO 1 L1TRACKS
        #         if len(L1Tk_match_indices)==1:
        #             histo3DClNOMatch.fill(row, L1tracks.iloc[L1Tk_match_indices[index][0]])
        #         # ELSE
        #         if len(L1Tk_match_indices)>1:
        #             histo3DClNOMatch.fill(row, L1tracks.iloc[L1Tk_match_indices[index][0]], L1tracks.iloc[L1Tk_match_indices[index][0]])


####################################################### add here as argument the first three l1tracks #######################################################        
        for index, row in unmatchedClusters.iterrows():
            histo3DClNOMatch.fill(row)
#############################################################################################################################################################



        for idx, genParticle in genParticles.iterrows():
            if idx in best_match_indexes.keys():

                matched3DCluster = trigger3DClusters.loc[[best_match_indexes[idx]]]
                matchedClusters = triggerClusters[triggerClusters.id.isin(matched3DCluster.clusters.item())]
                matchedTriggerCells = triggerCells[triggerCells.id.isin(np.concatenate(matchedClusters.cells.values))]

                if 'energyCentral' not in matched3DCluster.columns:
                    calib_factor = 1.084
                    matched3DCluster['energyCentral'] = [matchedClusters[(matchedClusters.layer > 9) & (matchedClusters.layer < 21)].energy.sum()*calib_factor]

                iso_df = computeIsolation(trigger3DClusters,
                                          idx_best_match=best_match_indexes[idx],
                                          idx_incone=allmatches[idx], dr=0.2)
                matched3DCluster['iso0p2'] = iso_df.energy
                matched3DCluster['isoRel0p2'] = iso_df.pt/matched3DCluster.pt

####################################################### add here as argument the first three l1tracks #######################################################
                # fill the plots
                histo3DClMatch.fill(matched3DCluster)
#############################################################################################################################################################


                if histoGenMatched is not None: 
                    histoGenMatched.fill(genParticles.loc[[idx]]) 

                if debug >= 6:
                    print ('--- Dump match for algo {} ---------------'.format(algoname))
                    print ('GEN particle: idx: {}'.format(idx))
                    print (genParticle)
                    print ('Matched to 3D cluster:')
                    print (matched3DCluster)


            else:
                if debug >= 5:
                    print ('==== Warning no match found for algo {}, idx {} ======================'.format(algoname,
                                                                                                           idx))
                    if debug >= 2:
                        print (genParticle)
                        print (trigger3DClusters)
        
    def book_histos(self):
        self.gen_set.activate()
        self.tp_set.activate()
        for tp_sel in self.tp_selections:
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}_{}'.format(self.tp_set.name,
                                               tp_sel.name,
                                               gen_sel.name)
                histo_name_NOMATCH = '{}_{}_{}_{}'.format(self.tp_set.name, tp_sel.name, gen_sel.name, "noMatch")
                self.h_tpset[histo_name] = histos.HistoSet3DClusters(histo_name)
                self.h_tpset[histo_name_NOMATCH] = histos.HistoSet3DClusters(histo_name_NOMATCH)
                #self.h_resoset[histo_name] = histos.HistoSetReso(histo_name)
                self.h_effset[histo_name] = histos.HistoSetEff(histo_name)
                self.h_trackmatching[histo_name] = histos.TrackMatchingHistos(histo_name)
               
        # Custom histograms that will be filled using all simtracks/3dclusters
        # To do so (for now) check that the selection indeed takes simply all objects (when filling the histograms)
        histname = '{}_{}'.format(self.tp_set.name,self.gen_set.name)
        self.h_custom[histname] = histos.CustomHistos(histname)




    def fill_histos(self, debug=False):
        # print "================== new event =================="
        for tp_sel in self.tp_selections:
            tcs = self.tp_set.tc_df
            cl2Ds = self.tp_set.cl2d_df
            cl3Ds = self.tp_set.cl3d_df
            l1tks = self.l1track_set.df

            # print self.l1track_set
            # print self.l1track_set.df

            if not tp_sel.all:
                cl3Ds = self.tp_set.cl3d_df.query(tp_sel.selection)
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}_{}'.format(self.tp_set.name, tp_sel.name, gen_sel.name)
                histo_name_NOMATCH = '{}_{}_{}_{}'.format(self.tp_set.name, tp_sel.name, gen_sel.name, "noMatch")
                genReference = self.gen_set.df[(self.gen_set.df.gen > 0)] 
                # genReference = self.gen_set.df
                # for ig,g in genReference.iterrows():
                #     print g.gen
                if not gen_sel.all:
                    genReference = self.gen_set.df[(self.gen_set.df.gen > 0)].query(gen_sel.selection) 
                    # print gen_sel.selection
                    # genReference = self.gen_set.df.query(gen_sel.selection) 
                    # FIXME: this doesn't work for pizeros since they are never listed in the genParticles...we need a working solution
                    # elif  particle.pdgid == PID.pizero:
                    #     genReference = genParts[(genParts.pid == particle.pdgid)]
                # for ig,g in genReference.iterrows():
                    # print "gen value is ",g.gen
                h_tpset_match = self.h_tpset[histo_name]
                h_tpset_NOmatch = self.h_tpset[histo_name_NOMATCH]
                h_genseleff = self.h_effset[histo_name]
                h_trackmatching = self.h_trackmatching[histo_name]

                self.plot3DMatch(genReference,
                                        cl3Ds,
                                        cl2Ds,
                                        tcs,
                                        l1tks,
                                        h_genseleff.h_den,
                                        h_genseleff.h_num,
                                        h_tpset_match.hcl3d,
                                        h_tpset_NOmatch.hcl3d,
                                        h_trackmatching,
                                        self.tp_set.name,
                                        debug)

    def __repr__(self):
        return '<{} tps: {}, tps_s: {}, gen:{}, gen_s:{}> '.format(self.__class__.__name__,
                                                                   self.tp_set.name,
                                                                   [sel.name for sel in self.tp_selections],
                                                                   self.gen_set.name,
                                                                   [sel.name for sel in self.gen_selections])
