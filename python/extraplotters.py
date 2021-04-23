from __future__ import absolute_import
import ROOT
import pandas as pd
import numpy as np
import math
from python.plotters import *
from . import extrafunctions as extrafunc
from . import l1THistos as histos
from . import utils as utils
from . import clusterTools as clAlgo
from . import selections as selections
pd.set_option('display.max_rows', None)


def filter_combinations(tp_sel, gen_sel):
    isGoodCombi = True
    # print ("filtering ", tp_sel.name, gen_sel.name)
    # if ("Pt15" in tp_sel.name or "Pt20"in tp_sel.name) and "Pt15" not in gen_sel.name: isGoodCombi=False
    # if ("Pt5to25" in tp_sel.name or "Pt5to20"in tp_sel.name) and "Pt30" not in gen_sel.name: isGoodCombi=False
    # if "Pt" not in tp_sel.name and "Pt" in gen_sel.name: isGoodCombi=False
    if "EtaBC"   in tp_sel.name and "EtaBC" not in gen_sel.name: isGoodCombi=False
    if "EtaDE"   in tp_sel.name and "EtaDE" not in gen_sel.name: isGoodCombi=False
    if "higheta" in tp_sel.name and "EtaDE" not in gen_sel.name: isGoodCombi=False
    if "loweta"  in tp_sel.name and "EtaBC" not in gen_sel.name: isGoodCombi=False
    return isGoodCombi

def match3DClusterToL1Tracks(clusters, tracks, positional):
    L1Tk_best_match_idx = {}
    if not tracks.empty: 
        # Perform the matching 3DCluster->L1track
        # print ("=========== matching tracks ==========")
        L1Tk_best_match_idx, L1Tk_match_indices = utils.match_etaphi(clusters[['eta','phi']],
                                                        tracks[['caloeta', 'calophi']],
                                                        tracks['pt'],
                                                        deltaR=0.3,
                                                        return_positional=positional)
        for idx_cl,idx_trk in L1Tk_best_match_idx.items():
            if L1Tk_best_match_idx!=None:
                trk= tracks.iloc[[idx_trk]] if positional else tracks.loc[[idx_trk]]
                clusters.at[idx_cl, "tttrack_pt"]=trk.pt
                clusters.at[idx_cl, "tttrack_eta"]=trk.eta
                clusters.at[idx_cl, "tttrack_phi"]=trk.phi
                clusters.at[idx_cl, "tttrack_chi2"]=trk.chi2
                clusters.at[idx_cl, "tttrack_nStubs"]=trk.nStubs
        # print (clusters)
        m_cl = list(L1Tk_match_indices.values())
        # if len(m_cl)!=0:
        #     print ("Found %s tracks that matched to this cluster"%len(m_cl[0]))
        #     print (tracks.loc[m_cl[0]])
        # else:
        #     print ("Found 0 tracks that matched to this cluster")
        # print (list(L1Tk_match_indices.values()))
        # print (tracks.loc[list(L1Tk_match_indices.values())[0]])
        # print ("======================================")                
    return clusters

class Cluster3DGenMatchHybrid(BasePlotter):
    def __init__(self, tp_set, l1track_set, gen_set,
                 tp_selections=[selections.Selection('all')], tp_IDselections=[selections.Selection('all')],
                 gen_selections=[selections.Selection('all')], ObjectHistoClass=histos.Cluster3DHistos,
                 includeTracks=False, saveEffPlots=False, saveNtuples=False):
        # self.tp_set = tp_set
        # self.tp_selections = tp_selections
        # self.gen_set = gen_set
        # self.gen_selections = gen_selections
        self.tp_IDselections=tp_IDselections
        self.ObjectHistoClass=ObjectHistoClass
        self.l1track_set=l1track_set
        self.h_tpset = {}
        self.h_dataset= {}
        self.h_effset = {}
        self.saveNtuples = saveNtuples
        self.saveEffPlots = saveEffPlots
        self.includeTracks = includeTracks
        self.gen_eta_phi_columns = ['exeta', 'exphi']

        super(Cluster3DGenMatchHybrid, self).__init__(tp_set, tp_selections, gen_set, gen_selections)


    def plotObjectMatch(self,
                        genParticles,
                        objects,
                        L1tracks,
                        h_gen,
                        h_gen_matched,
                        ntuple3DClMatch,
                        ntuple3DClNOMatch,
                        h_object_matched,
                        algoname,
                        tp_IDsel,
                        debug):

        # print ("\n======  NEW EVENT ====== \n")

        gen_filler = histos.HistoLazyFiller(genParticles)
        den_sel = np.full(genParticles.shape[0], True, dtype=bool)
        num_sel = np.full(genParticles.shape[0], False, dtype=bool)
        
        # fill histo with all selected GEN particles before any match
        gen_filler.add_selection('den', den_sel)
        if h_gen:
            h_gen.fill_lazy(gen_filler, 'den')

        best_match_indexes = {}
        positional = True
        if not objects.empty:
            # obj_filler = histos.HistoLazyFiller(objects)
            obj_ismatch = np.full(objects.shape[0], False, dtype=bool)

            best_match_indexes, allmatches = utils.match_etaphi(
                genParticles[self.gen_eta_phi_columns],
                objects[['eta', 'phi']],
                objects['pt'],
                deltaR=0.2,
                return_positional=positional)
     

            for idx in list(best_match_indexes.keys()):
                if positional:
                    obj_matched = objects.iloc[[best_match_indexes[idx]]]
                    obj_ismatch[best_match_indexes[idx]] = True
                else: 
                    obj_matched = objects.loc[[best_match_indexes[idx]]]
                    obj_ismatch[objects.index.get_loc(best_match_indexes[idx])] = True
            
                # DECORATE THE 3D CLUSTERS WITH QUANTITIES OF MATCHED L1 TRACKS IN A DELTAR CONE
                if self.includeTracks:
                    obj_matched = match3DClusterToL1Tracks(obj_matched, L1tracks, positional)

                # Remove the matched clusters that do not pass the ID                
                if not tp_IDsel.selection == "":
                    obj_matched = obj_matched.query(tp_IDsel.selection)
                if not obj_matched.empty:
                    num_sel[genParticles.index.get_loc(idx)] = True

                # print ("====== using as match ======")
                # print (genParticles.pt, (obj_matched.pt))
                # print ("============================")

                # FILL THE OUTPUT NTUPLES AND HISTOGRAMS
                if self.saveNtuples:
                    ntuple3DClMatch.fill(obj_matched)
            
                if h_object_matched:
                    h_object_matched.fill(obj_matched)
                
            # obj_filler.add_selection('match', obj_ismatch)
            # h_object_matched.fill_lazy(obj_filler, 'match')
            # obj_filler.fill()

        if h_gen_matched is not None:
            gen_filler.add_selection('num', num_sel)
            h_gen_matched.fill_lazy(gen_filler, 'num')
            gen_filler.fill()


    def book_histos(self):
        self.gen_set.activate()
        self.tp_set.activate()
        self.l1track_set.activate()        
        for tp_sel in self.tp_selections:
            for tp_IDsel in self.tp_IDselections:
                for gen_sel in self.gen_selections:
                    histo_name = '{}_{}_{}'.format(self.tp_set.name,
                                                   tp_sel.name+tp_IDsel.name,
                                                   gen_sel.name)
                    histo_name_NOMATCH = '{}_{}_{}_{}'.format(self.tp_set.name, tp_sel.name+tp_IDsel.name, gen_sel.name, "noMatch")

                    # Exclude some combinations of GENsel and TPsel
                    isGoodCombi = filter_combinations(tp_sel+tp_IDsel, gen_sel) #<-  + might be wrong
                    if not isGoodCombi: continue

                    if self.saveNtuples:
                        self.h_tpset[histo_name]         = histos.HistoSet3DClusters(histo_name)
                        self.h_tpset[histo_name_NOMATCH] = histos.HistoSet3DClusters(histo_name_NOMATCH)
                    if self.saveEffPlots:
                        # self.h_efftp[histo_name] = histos.HistoSetEff(histo_name)
                        # self.h_efftp[histo_name].h_num = histos.Cluster3DHistos('h_effNum_'+histo_name)
                        # self.h_efftp[histo_name].h_den = histos.Cluster3DHistos('h_effDen_'+histo_name)
                        self.h_dataset[histo_name]= self.ObjectHistoClass(histo_name)
                        self.h_effset[histo_name] = histos.HistoSetEff(histo_name, extended_range=True)


    def fill_histos(self, debug=0):
        pass

    def fill_histos_event(self, idx, debug=0):
        # print ("================== new event ==================")
        for tp_sel in self.tp_selections:
            cl3Ds = self.tp_set.query_event(tp_sel, idx)
            l1tks = self.l1track_set.query_event(selections.Selection('all'), idx)
            for tp_IDsel in self.tp_IDselections:
                for gen_sel in self.gen_selections:
                    # Exclude some combinations of GENsel and TPsel
                    isGoodCombi = filter_combinations(tp_sel+tp_IDsel, gen_sel)#<-  + might be wrong
                    if not isGoodCombi: continue

                    genReference = self.gen_set.query_event(gen_sel, idx)
                    if genReference.empty:
                        continue

                    # print (tp_sel.name, tp_IDsel.name, gen_sel.name)

                    # Fill all other histograms and ntuples
                    histo_name = '{}_{}_{}'.format(self.tp_set.name, tp_sel.name+tp_IDsel.name, gen_sel.name)
                    histo_name_NOMATCH = '{}_{}_{}_{}'.format(self.tp_set.name, tp_sel.name+tp_IDsel.name, gen_sel.name, "noMatch")

                    hcl3d_matched   = None if not self.saveNtuples else self.h_tpset[histo_name].hcl3d
                    hcl3d_unmatched = None if not self.saveNtuples else self.h_tpset[histo_name_NOMATCH].hcl3d
                    # h_tpset_match =   None if not self.saveNtuples else self.h_tpset[histo_name]
                    # h_tpset_NOmatch = None if not self.saveNtuples else self.h_tpset[histo_name_NOMATCH]
                    h_genseleff_den =     None if not self.saveEffPlots else self.h_effset[histo_name].h_den
                    h_genseleff_num =     None if not self.saveEffPlots else self.h_effset[histo_name].h_num
                    h_obj_match =         None if not self.saveEffPlots else self.h_dataset[histo_name]

                    # h_tpseleff_den =     None if not self.saveEffPlots else self.h_efftp[histo_name].h_den
                    # h_tpseleff_num =     None if not self.saveEffPlots else self.h_efftp[histo_name].h_num

                    self.plotObjectMatch(genReference,
                                            cl3Ds,
                                            l1tks,
                                            h_genseleff_den,
                                            h_genseleff_num,
                                            # h_tpseleff_den,
                                            # h_tpseleff_num,                                        
                                            hcl3d_matched,
                                            hcl3d_unmatched,
                                            h_obj_match,
                                            self.tp_set.name,
                                            tp_IDsel,
                                            debug)

    def __repr__(self):
        for sel in self.tp_selections:
            print (sel)
        return '<{} tps: {}, tps_s: {}, gen:{}, gen_s:{}> '.format(self.__class__.__name__,
                                                                   self.tp_set.name,
                                                                   [sel.name for sel in self.tp_selections],
                                                                   self.gen_set.name,
                                                                   [sel.name for sel in self.gen_selections])






class Cluster3DHybrid(BasePlotter):
    def __init__(self, tp_set, l1track_set,
                 tp_selections=[selections.Selection('all')], includeTracks=False, saveEffPlots=False, saveNtuples=False):
        # self.tp_set = tp_set
        # self.tp_selections = tp_selections
        self.l1track_set=l1track_set
        self.h_tpset = {}
        self.h_effset = {}
        self.saveNtuples = saveNtuples
        self.saveEffPlots = saveEffPlots
        self.includeTracks = includeTracks
        super(Cluster3DHybrid, self).__init__(tp_set, tp_selections)

    def plotObject(self,
                   objects,
                   L1tracks,
                   ntuple3DClNOMatch,
                   algoname,
                   debug):

        if not objects.empty:

            # DECORATE THE 3D CLUSTERS WITH QUANTITIES OF MATCHED L1 TRACKS IN A DELTAR CONE
            if self.includeTracks:
                objects = match3DClusterToL1Tracks(objects, L1tracks, True)

            # SAVE CLUSTERS TO NTUPLE
            if self.saveNtuples:
                ntuple3DClNOMatch.fill(objects)

        
    def book_histos(self):
        self.tp_set.activate()
        self.l1track_set.activate()        
        tp_name = self.tp_set.name
        for selection in self.tp_selections: 
            histo_name_NOMATCH='{}_{}_noMatch'.format(tp_name, selection.name)
            #self.h_tpset[selection.name] = histos.HistoSetClusters(name='{}_{}_nomatch'.format(tp_name, selection.name))
            if self.saveNtuples:
                self.h_tpset[histo_name_NOMATCH] = histos.HistoSet3DClusters(histo_name_NOMATCH)
            if self.saveEffPlots:
                self.h_effset[histo_name] = histos.HistoSetEff(histo_name)

    def fill_histos(self, debug=0):
        pass

    def fill_histos_event(self, idx, debug=0):
        # print ("idx = ",idx)
        for tp_sel in self.tp_selections:
            cl3Ds = self.tp_set.query_event(tp_sel, idx)
            l1tks = self.l1track_set.query_event(selections.Selection('all'), idx)
            # l1tks = self.l1track_set.df

            # if not tp_sel.all:
            #     cl3Ds = cl3Ds.query(tp_sel.selection)
            
            histo_name_NOMATCH='{}_{}_noMatch'.format(self.tp_set.name, tp_sel.name)
            hcl3d_unmatched = None if not self.saveNtuples else self.h_tpset[histo_name_NOMATCH].hcl3d

            self.plotObject(cl3Ds,
                            l1tks,
                            hcl3d_unmatched,
                            self.tp_set.name,
                            debug)


class CustomHistPlotter(BasePlotter):
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
        super(CustomHistPlotter, self).__init__(tp_set, tp_selections, gen_set, gen_selections)

        
    def book_histos(self):
        self.gen_set.activate()
        self.tp_set.activate()
        self.l1track_set.activate()        
        for tp_sel in self.tp_selections:
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}_{}'.format(self.tp_set.name,
                                               tp_sel.name,
                                               gen_sel.name)
                histo_name_NOMATCH = '{}_{}_{}_{}'.format(self.tp_set.name, tp_sel.name, gen_sel.name, "noMatch")

                # Exclude some combinations of GENsel and TPsel
                isGoodCombi = filter_combinations(tp_sel, gen_sel)
                if not isGoodCombi: continue

                # Custom histograms that will be filled using all simtracks/3dclusters
                # To do so (for now) check that the selection indeed takes simply all objects (when filling the histograms)
                if self.tp_set.name=="HMvDR" and tp_sel.name=="EtaBCDE" and gen_sel.name=="GEN":

                # histname = '{}_{}'.format(self.tp_set.name,self.gen_set.name)
                    self.h_custom["HMvDR_GEN"] = histos.CustomHistos("HMvDR_GEN")
                    self.h_custom["l1Trk_GEN"] = histos.CustomHistos("l1Trk_GEN")
                # histname = '{}_{}'.format(self.l1track_set.name,self.gen_set.name)
                # self.h_custom[histname] = histos.CustomHistos(histname)



    def fill_histos(self, debug=False):
        # print "================== new event =================="
        for tp_sel in self.tp_selections:
            cl3Ds = self.tp_set.df
            l1tks = self.l1track_set.df

            if not tp_sel.all:
                cl3Ds = cl3Ds.query(tp_sel.selection)
            for gen_sel in self.gen_selections:
                
                genReference = self.gen_set.df[(self.gen_set.df.gen > 0)] 
                if not gen_sel.all:
                    genReference = self.gen_set.df[(self.gen_set.df.gen > 0)].query(gen_sel.selection) 
                
                # Exclude some combinations of GENsel and TPsel
                isGoodCombi = filter_combinations(tp_sel, gen_sel)
                if not isGoodCombi: continue

                # Fill the custom histograms used to study matching and preselection
                if self.tp_set.name=="HMvDR" and tp_sel.name=="EtaBCDE" and gen_sel.name=="GEN":
                    h_custom = self.h_custom["HMvDR_GEN"]
                    extrafunc.Fill_GENtoL1Obj_CustomHists(genReference, h_custom, cl3Ds, 0.2, useExtrapolatedGenCoords=True)
                if self.l1track_set.name=="l1Trk" and tp_sel.name=="EtaBCDE" and gen_sel.name=="GENEtaBCD":
                    h_custom = self.h_custom["l1Trk_GEN"]
                    extrafunc.Fill_GENtoL1Obj_CustomHists(genReference, h_custom, l1tks, 0.2, useExtrapolatedGenCoords=False)


    def __repr__(self):
        for sel in self.tp_selections:
            print (sel)
        return '<{} tps: {}, tps_s: {}, gen:{}, gen_s:{}> '.format(self.__class__.__name__,
                                                                   self.tp_set.name,
                                                                   [sel.name for sel in self.tp_selections],
                                                                   self.gen_set.name,
                                                                   [sel.name for sel in self.gen_selections])