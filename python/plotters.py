"""
Definines and instantiate the plotter classes.

These are the classes where the analysis logic is implemented.
The plotter classes need to implement a standard interface:
init:
    accept one or more DFCollection (or TPSet) and a corresponding list of selections.

book_histos:
    activates the relevant DFCollection instances and books the HistoClasses defined in the
    `l1THistos` module for each combination of the object and selections.
     The naming convention of the histograms uses the namse of the objects,
     the name of the selection and the name of the gen-matched object (if any).

fill_histos:
    actually implements the analysis logic, running the selections on the input
    collections and filling the histograms.

Several collections of plotters are also instantiated. Which one will actually be run
is steered via the configuration file.
"""
import ROOT
import l1THistos as histos
import utils as utils
import pandas as pd
import numpy as np
import clusterTools as clAlgo
import selections as selections
# import collections as collections


class BasePlotter(object):
    def __init__(self, data_set, data_selections, gen_set=None, gen_selections=None):
        self.data_set = data_set
        self.data_selections = data_selections
        self.gen_set = gen_set
        self.gen_selections = gen_selections

    @property
    def tp_set(self):
        return self.data_set

    @property
    def tp_selections(self):
        return self.data_selections

    def get_histo_primitives(self):
        histo_primitives = pd.DataFrame(columns=['data', 'data_sel', 'gen_sel', 'data_label', 'data_sel_label', 'gen_sel_label'])
        gen_sel_names = ['nomatch']
        gen_sel_labels = ['']
        if self.gen_selections is not None:
            gen_sel_names = [sel.name for sel in self.gen_selections]
            gen_sel_labels = [sel.label for sel in self.gen_selections]

        for data_sel in self.data_selections:
            for idx,gen_sel_name in enumerate(gen_sel_names):
                histo_primitives = histo_primitives.append({'data': self.data_set.name,
                                                            'data_sel': data_sel.name,
                                                            'gen_sel': gen_sel_name,
                                                            'data_label': self.data_set.label,
                                                            'data_sel_label': data_sel.label,
                                                            'gen_sel_label': gen_sel_labels[idx]},
                                                           ignore_index=True)
        return histo_primitives

    # def change_genpart_selection(self, newselection):
    #     """Allow customization of gen selection per sample."""
    #     if self.gen_selections is not None:
    #         self.gen_selections = newselection
    #
    # def __repr__(self):
    #     if  self.gen_selections is not None:
    #         return '<{}, tp: {}, gen_sel: {}>'.format(self.__class__.__name__,
    #                                                   self.data_set.name,
    #                                                   self.gen_selections[0].selection)
    #     else:
    #         return '<{}, tp: {}>'.format(self.__class__.__name__,
    #                                      self.data_set.name)


class RatePlotter(BasePlotter):
    def __init__(self, tp_set, tp_selections=[selections.Selection('all')]):
        self.h_rate = {}
        super(RatePlotter, self).__init__(tp_set, tp_selections)

    def book_histos(self):
        self.tp_set.activate()
        tp_name = self.tp_set.name
        for selection in self.tp_selections:
            self.h_rate[selection.name] = histos.RateHistos(name='{}_{}'.format(tp_name,
                                                                                selection.name))

    def fill_histos(self, debug=False):
        # print '------------------'
        # print self.tp_set.name
        for selection in self.tp_selections:
            # print selection.selection
            if not selection.all and not self.tp_set.df.empty:
                sel_clusters = self.tp_set.df.query(selection.selection)
            else:
                sel_clusters = self.tp_set.df
            # print sel_clusters
            trigger_clusters = sel_clusters[['pt', 'eta']].sort_values(by='pt',
                                                                       ascending=False)
            # print trigger_clusters[:5]

            if not trigger_clusters.empty:
                # print trigger_clusters.iloc[0]
                self.h_rate[selection.name].fill(trigger_clusters.iloc[0].pt,
                                                 trigger_clusters.iloc[0].eta)
            self.h_rate[selection.name].fill_norm()


class GenericDataFramePlotter(BasePlotter):
    def __init__(self, HistoClass, data_set, selections=[selections.Selection('all')]):
        self.HistoClass = HistoClass
        self.h_set = {}
        super(GenericDataFramePlotter, self).__init__(data_set, selections)

    def book_histos(self):
        self.data_set.activate()
        data_name = self.data_set.name
        for selection in self.data_selections:
            self.h_set[selection.name] = self.HistoClass(name='{}_{}_nomatch'.format(data_name,
                                                                                     selection.name))

    def fill_histos(self, debug=False):
        for data_sel in self.data_selections:
            data = self.data_set.df
            if not data_sel.all and not self.data_set.df.empty:
                data = self.data_set.df.query(data_sel.selection)
            self.h_set[data_sel.name].fill(data)


class TkEGPlotter(GenericDataFramePlotter):
    def __init__(self, tkeg_set, tkeg_selections=[selections.Selection('all')]):
        super(TkEGPlotter, self).__init__(histos.TkEGHistos, tkeg_set, tkeg_selections)


class TrackPlotter(GenericDataFramePlotter):
    def __init__(self, trk_set, track_selections=[selections.Selection('all')]):
        super(TrackPlotter, self).__init__(histos.TrackHistos, trk_set, track_selections)


class EGPlotter(GenericDataFramePlotter):
    def __init__(self, eg_set, eg_selections=[selections.Selection('all')]):
        super(EGPlotter, self).__init__(histos.EGHistos, eg_set, eg_selections)


class TTPlotter(GenericDataFramePlotter):
    def __init__(self, tt_set, tt_selections=[selections.Selection('all')]):
        super(TTPlotter, self).__init__(histos.TriggerTowerHistos, tt_set, tt_selections)


class TPPlotter(BasePlotter):
    def __init__(self, tp_set, tp_selections=[selections.Selection('all')]):
        # self.tp_set = tp_set
        # self.tp_selections = tp_selections
        self.h_tpset = {}
        super(TPPlotter, self).__init__(tp_set, tp_selections)

    def book_histos(self):
        self.tp_set.activate()
        tp_name = self.tp_set.name
        for selection in self.tp_selections:
            self.h_tpset[selection.name] = histos.HistoSetClusters(name='{}_{}_nomatch'.format(tp_name, selection.name))

    def fill_histos(self, debug=False):
        for tp_sel in self.tp_selections:
            tcs = self.tp_set.tc_df
            cl2Ds = self.tp_set.cl2d_df
            cl3Ds = self.tp_set.cl3d_df
            if not tp_sel.all:
                cl3Ds = self.tp_set.cl3d_df.query(tp_sel.selection)
            # debug = 4
            # utils.debugPrintOut(debug, '{}_{}'.format(self.tp_set.name, 'TCs'), tcs, tcs[:3])
            # utils.debugPrintOut(debug, '{}_{}'.format(self.tp_set.name, 'CL2D'), cl2Ds, cl2Ds[:3])
            # utils.debugPrintOut(debug, '{}_{}'.format(self.tp_set.name, 'CL3D'), cl3Ds, cl3Ds[:3])
            if not cl3Ds.empty and not cl2Ds.empty and not tcs.empty:
                self.h_tpset[tp_sel.name].fill(tcs, cl2Ds, cl3Ds)


class GenPlotter:
    def __init__(self, gen_set, gen_selections=[selections.Selection('all')]):
        self.gen_set = gen_set
        self.gen_selections = gen_selections
        self.h_gen = {}

    def book_histos(self):
        self.gen_set.activate()
        for selection in self.gen_selections:
            self.h_gen[selection.name] = histos.GenParticleHistos(name='h_genParts_{}'.format(selection.name))

    def fill_histos(self, debug=False):
        gen_parts_all = self.gen_set.df[self.gen_set.df.gen > 0]
        for gen_sel in self.gen_selections:
            gen_parts = gen_parts_all
            if not gen_sel.all:
                gen_parts = gen_parts_all.query(gen_sel.selection)
            self.h_gen[gen_sel.name].fill(gen_parts)


class TPGenMatchPlotterDebugger:
    def __init__(self, tp_set, gen_set, mc_set,
                 tp_selections=[selections.Selection('all')], gen_selections=[selections.Selection('all')]):
        self.tp_set = tp_set
        self.tp_selections = tp_selections
        self.gen_set = gen_set
        self.mc_set = mc_set
        self.gen_selections = gen_selections
        self.h_tpset = {}
        self.h_resoset = {}
        self.h_effset = {}
        self.h_conecluster = {}

    def plot3DClusterMatch(self,
                           genParticles,
                           trigger3DClusters,
                           triggerClusters,
                           triggerCells,
                           histoGen,
                           histoGenMatched,
                           histoTCMatch,
                           histoClMatch,
                           histo3DClMatch,
                           histoReso,
                           histoResoCone,
                           histoReso2D,
                           histoConeClusters,
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

        best_match_indexes = {}
        if not trigger3DClusters.empty:
            best_match_indexes, allmatches = utils.match_etaphi(genParticles[['eta', 'phi']],
                                                                trigger3DClusters[['eta', 'phi']],
                                                                trigger3DClusters['pt'],
                                                                deltaR=0.1)
        # print ('------ best match: ')
        # print (best_match_indexes)
        # print ('------ all matches:')
        # print (allmatches)

        # allmatched2Dclusters = list()
        # matchedClustersAll = pd.DataFrame()
        if histoGen is not None: #COMMENT THIS
            histoGen.fill(genParticles) #COMMENT THIS
        orig_debug = debug
        for idx, genParticle in genParticles.iterrows():
            if idx in best_match_indexes.keys():
                # print ('-----------------------')
                #  print(genParticle)
                matched3DCluster = trigger3DClusters.loc[[best_match_indexes[idx]]]
                # print (matched3DCluster)
                # allMatches = trigger3DClusters.iloc[allmatches[idx]]
                # print ('--')
                # print (allMatches)
                # print (matched3DCluster.clusters.item())
                # print (type(matched3DCluster.clusters.item()))
                # matchedClusters = triggerClusters[ [x in matched3DCluster.clusters.item() for x in triggerClusters.id]]
                matchedClusters = triggerClusters[triggerClusters.id.isin(matched3DCluster.clusters.item())]

                # we now build real 2D clusters per layer for furhter tests (e.g. layer by layer position resolution)
                print (matchedClusters)
                print matchedClusters.layer.unique()
                for layer in matchedClusters.layer.unique():
                    histoReso2D.fill(reference=genParticle, target=clAlgo.build2D(matchedClusters[matchedClusters.layer == layer]))

                matchedTriggerCells = triggerCells[triggerCells.id.isin(np.concatenate(matchedClusters.cells.values))]
                # allmatched2Dclusters. append(matchedClusters)

                if 'energyCentral' not in matched3DCluster.columns:
                    calib_factor = 1.084
                    matched3DCluster['energyCentral'] = [matchedClusters[(matchedClusters.layer > 9) & (matchedClusters.layer < 21)].energy.sum()*calib_factor]

                iso_df = computeIsolation(trigger3DClusters, idx_best_match=best_match_indexes[idx], idx_incone=allmatches[idx], dr=0.2)
                matched3DCluster['iso0p2'] = iso_df.energy
                matched3DCluster['isoRel0p2'] = iso_df.pt/matched3DCluster.pt

                # fill the plots
                histoTCMatch.fill(matchedTriggerCells)
                histoClMatch.fill(matchedClusters)
                histo3DClMatch.fill(matched3DCluster)
                # print 'HERE'
                # print matched3DCluster
                # print genParticle
                # if matched3DCluster.iloc[0].pt/genParticle.pt > 1.5:
                #     debug = 7
                histoReso.fill(reference=genParticle, target=matched3DCluster.iloc[0])

                if False:
                    # now we fill the reso plot for all the clusters in the cone
                    clustersInCone = sumClustersInCone(trigger3DClusters, allmatches[idx])

                    def fill_cluster_incone_histos(cl3ds,
                                                   idx_allmatches,
                                                   idx_bestmatch,
                                                   charge,
                                                   h_clustersInCone,
                                                   debug=0):
                        if debug > 4:
                            print '- best match: {}, all matches: {}'.format(idx_bestmatch,
                                                                             idx_allmatches)
                        bestcl = cl3ds.loc[idx_bestmatch]
                        h_clustersInCone.fill_n(len(idx_allmatches)-1)
                        for idx in idx_allmatches:
                            if idx == idx_bestmatch:
                                continue
                            clincone = cl3ds.loc[idx]
                            h_clustersInCone.fill(reference=bestcl,
                                                  target=clincone,
                                                  charge=charge)
                    # print genParticle
                    # print genParticle.pid/abs(genParticle.pid)
                    fill_cluster_incone_histos(trigger3DClusters,
                                               allmatches[idx],
                                               best_match_indexes[idx],
                                               genParticle.pid/abs(genParticle.pid),
                                               histoConeClusters)

                    # print ('----- in cone sum:')
                    # print (clustersInCone)
                    # histoResoCone.fill(reference=genParticle, target=clustersInCone.iloc[0])

                if histoGenMatched is not None:
                    histoGenMatched.fill(genParticles.loc[[idx]])

                if debug >= 6:
                    print ('--- Dump match for algo {} ---------------'.format(algoname))
                    print ('GEN particle: idx: {}'.format(idx))
                    print (genParticle)
                    print ('Matched to 3D cluster:')
                    print (matched3DCluster)
                    print ('Matched 2D clusters:')
                    print (matchedClusters)
                    print ('matched cells:')
                    print (matchedTriggerCells)

                    print ('3D cluster energy: {}'.format(matched3DCluster.energy.sum()))
                    print ('3D cluster pt: {}'.format(matched3DCluster.pt.sum()))
                    calib_factor = 1.084
                    print ('sum 2D cluster energy: {}'.format(matchedClusters.energy.sum()*calib_factor))
                    # print ('sum 2D cluster pt: {}'.format(matchedClusters.pt.sum()*calib_factor))
                    print ('sum TC energy: {}'.format(matchedTriggerCells.energy.sum()))
                    # print ('Sum of matched clusters in cone:')
                    # print (clustersInCone)
                    print 'MC truth:'
                    print self.mc_set.df
                    print 'Other GEN particles:'
                    print self.gen_set.df[['phi', 'eta', 'pt', 'mother', 'fbrem', 'pid', 'gen' ,'reachedEE', 'fromBeamPipe']]
                    print 'Other clusters in cone:'
                    print trigger3DClusters[trigger3DClusters.index.isin(allmatches[idx])]
            else:
                if debug >= 5:
                    print ('==== Warning no match found for algo {}, idx {} ======================'.format(algoname,
                                                                                                           idx))
                    if debug >= 2:
                        print (genParticle)
                        print (trigger3DClusters)
            debug = orig_debug
        # if len(allmatched2Dclusters) != 0:
        #     matchedClustersAll = pd.concat(allmatched2Dclusters)
        # return matchedClustersAll

    def book_histos(self):
        self.gen_set.activate()
        self.tp_set.activate()
        self.mc_set.activate()
        for tp_sel in self.tp_selections:
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}_{}'.format(self.tp_set.name,
                                               tp_sel.name,
                                               gen_sel.name)
                self.h_tpset[histo_name] = histos.HistoSetClusters(histo_name)
                self.h_resoset[histo_name] = histos.HistoSetReso(histo_name)
                self.h_effset[histo_name] = histos.HistoSetEff(histo_name)
                self.h_conecluster[histo_name] = histos.ClusterConeHistos(histo_name)

    def fill_histos(self, debug=False):
        for tp_sel in self.tp_selections:
            tcs = self.tp_set.tc_df
            cl2Ds = self.tp_set.cl2d_df
            cl3Ds = self.tp_set.cl3d_df
            if not tp_sel.all:
                cl3Ds = self.tp_set.cl3d_df.query(tp_sel.selection)
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}_{}'.format(self.tp_set.name, tp_sel.name, gen_sel.name)
                genReference = self.gen_set.df[(self.gen_set.df.gen > 0)]
                if not gen_sel.all:
                    genReference = self.gen_set.df[(self.gen_set.df.gen > 0)].query(gen_sel.selection)
                    # FIXME: this doesn't work for pizeros since they are never listed in the genParticles...we need a working solution
                    # elif  particle.pdgid == PID.pizero:
                    #     genReference = genParts[(genParts.pid == particle.pdgid)]

                h_tpset_match = self.h_tpset[histo_name]
                h_resoset = self.h_resoset[histo_name]
                h_genseleff = self.h_effset[histo_name]
                h_conecl = self.h_conecluster[histo_name]
                # print 'TPsel: {}, GENsel: {}'.format(tp_sel.name, gen_sel.name)
                self.plot3DClusterMatch(genReference,
                                        cl3Ds,
                                        cl2Ds,
                                        tcs,
                                        h_genseleff.h_den,
                                        h_genseleff.h_num,
                                        h_tpset_match.htc,
                                        h_tpset_match.hcl2d,
                                        h_tpset_match.hcl3d,
                                        h_resoset.hreso,
                                        h_resoset.hresoCone,
                                        h_resoset.hreso2D,
                                        h_conecl,
                                        self.tp_set.name,
                                        debug)


class TPGenMatchPlotter(BasePlotter):
    def __init__(self, tp_set, gen_set,
                 tp_selections=[selections.Selection('all')], gen_selections=[selections.Selection('all')]):
        # self.tp_set = tp_set
        # self.tp_selections = tp_selections
        # self.gen_set = gen_set
        # self.gen_selections = gen_selections
        self.h_tpset = {}
        self.h_resoset = {}
        self.h_effset = {}
        self.h_conecluster = {}
        super(TPGenMatchPlotter, self).__init__(tp_set, tp_selections, gen_set, gen_selections)

    def plot3DClusterMatch(self,
                           genParticles,
                           trigger3DClusters,
                           triggerClusters,
                           triggerCells,
                           histoGen,
                           histoGenMatched,
                           histoTCMatch,
                           histoClMatch,
                           histo3DClMatch,
                           histoReso,
                           histoResoCone,
                           histoReso2D,
                           histoConeClusters,
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

        best_match_indexes = {}
        if not trigger3DClusters.empty:
            best_match_indexes, allmatches = utils.match_etaphi(genParticles[['eta', 'phi']],
                                                                trigger3DClusters[['eta', 'phi']],
                                                                trigger3DClusters['pt'],
                                                                deltaR=0.1)
        # print ('------ best match: ')
        # print (best_match_indexes)
        # print ('------ all matches:')
        # print (allmatches)

        # allmatched2Dclusters = list()
        # matchedClustersAll = pd.DataFrame()
        if histoGen is not None:
            histoGen.fill(genParticles)

        for idx, genParticle in genParticles.iterrows():
            if idx in best_match_indexes.keys():
                # print ('-----------------------')
                #  print(genParticle)
                matched3DCluster = trigger3DClusters.loc[[best_match_indexes[idx]]]
                # print (matched3DCluster)
                # allMatches = trigger3DClusters.iloc[allmatches[idx]]
                # print ('--')
                # print (allMatches)
                # print (matched3DCluster.clusters.item())
                # print (type(matched3DCluster.clusters.item()))
                # matchedClusters = triggerClusters[ [x in matched3DCluster.clusters.item() for x in triggerClusters.id]]
                matchedClusters = triggerClusters[triggerClusters.id.isin(matched3DCluster.clusters.item())]
                # print (matchedClusters)
                matchedTriggerCells = triggerCells[triggerCells.id.isin(np.concatenate(matchedClusters.cells.values))]
                # allmatched2Dclusters. append(matchedClusters)

                if 'energyCentral' not in matched3DCluster.columns:
                    calib_factor = 1.084
                    matched3DCluster['energyCentral'] = [matchedClusters[(matchedClusters.layer > 9) & (matchedClusters.layer < 21)].energy.sum()*calib_factor]

                iso_df = computeIsolation(trigger3DClusters,
                                          idx_best_match=best_match_indexes[idx],
                                          idx_incone=allmatches[idx], dr=0.2)
                matched3DCluster['iso0p2'] = iso_df.energy
                matched3DCluster['isoRel0p2'] = iso_df.pt/matched3DCluster.pt

                # fill the plots
                histoTCMatch.fill(matchedTriggerCells)
                histoClMatch.fill(matchedClusters)
                histo3DClMatch.fill(matched3DCluster)

                # print matchedClusters
                # print matchedClusters.layer.unique()
                for layer in matchedClusters.layer.unique():
                    if histoReso2D is not None:
                        histoReso2D.fill(reference=genParticle,
                                         target=clAlgo.build2D(matchedClusters[matchedClusters.layer == layer]))

                if False:
                    histoReso2D.fill(reference=genParticle, target=matchedClusters)
                histoReso.fill(reference=genParticle, target=matched3DCluster.iloc[0])

                if True:
                    # now we fill the reso plot for all the clusters in the cone
                    clustersInCone = sumClustersInCone(trigger3DClusters, allmatches[idx])

                    def fill_cluster_incone_histos(cl3ds,
                                                   idx_allmatches,
                                                   idx_bestmatch,
                                                   charge,
                                                   h_clustersInCone,
                                                   debug=0):
                        if debug > 4:
                            print '- best match: {}, all matches: {}'.format(idx_bestmatch,
                                                                             idx_allmatches)
                        bestcl = cl3ds.loc[idx_bestmatch]
                        h_clustersInCone.fill_n(len(idx_allmatches)-1)
                        for idx in idx_allmatches:
                            if idx == idx_bestmatch:
                                continue
                            clincone = cl3ds.loc[idx]
                            h_clustersInCone.fill(reference=bestcl,
                                                  target=clincone,
                                                  charge=charge)
                    # print genParticle
                    # print genParticle.pid/abs(genParticle.pid)
                    fill_cluster_incone_histos(trigger3DClusters,
                                               allmatches[idx],
                                               best_match_indexes[idx],
                                               genParticle.pid/abs(genParticle.pid),
                                               histoConeClusters)

                    # print ('----- in cone sum:')
                    # print (clustersInCone)
                    # histoResoCone.fill(reference=genParticle, target=clustersInCone.iloc[0])

                if histoGenMatched is not None:
                    histoGenMatched.fill(genParticles.loc[[idx]])

                if debug >= 6:
                    print ('--- Dump match for algo {} ---------------'.format(algoname))
                    print ('GEN particle: idx: {}'.format(idx))
                    print (genParticle)
                    print ('Matched to 3D cluster:')
                    print (matched3DCluster)
                    print ('Matched 2D clusters:')
                    print (matchedClusters)
                    print ('matched cells:')
                    print (matchedTriggerCells)

                    print ('3D cluster energy: {}'.format(matched3DCluster.energy.sum()))
                    print ('3D cluster pt: {}'.format(matched3DCluster.pt.sum()))
                    calib_factor = 1.084
                    print ('sum 2D cluster energy: {}'.format(matchedClusters.energy.sum()*calib_factor))
                    # print ('sum 2D cluster pt: {}'.format(matchedClusters.pt.sum()*calib_factor))
                    print ('sum TC energy: {}'.format(matchedTriggerCells.energy.sum()))
                    print ('Sum of matched clusters in cone:')
                    print (clustersInCone)
            else:
                if debug >= 5:
                    print ('==== Warning no match found for algo {}, idx {} ======================'.format(algoname,
                                                                                                           idx))
                    if debug >= 2:
                        print (genParticle)
                        print (trigger3DClusters)

        # if len(allmatched2Dclusters) != 0:
        #     matchedClustersAll = pd.concat(allmatched2Dclusters)
        # return matchedClustersAll

    def book_histos(self):
        self.gen_set.activate()
        self.tp_set.activate()
        for tp_sel in self.tp_selections:
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}_{}'.format(self.tp_set.name,
                                               tp_sel.name,
                                               gen_sel.name)
                self.h_tpset[histo_name] = histos.HistoSetClusters(histo_name)
                self.h_resoset[histo_name] = histos.HistoSetReso(histo_name)
                self.h_effset[histo_name] = histos.HistoSetEff(histo_name)
                self.h_conecluster[histo_name] = histos.ClusterConeHistos(histo_name)

    def fill_histos(self, debug=False):
        for tp_sel in self.tp_selections:
            tcs = self.tp_set.tc_df
            cl2Ds = self.tp_set.cl2d_df
            cl3Ds = self.tp_set.cl3d_df
            if not tp_sel.all:
                cl3Ds = self.tp_set.cl3d_df.query(tp_sel.selection)
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}_{}'.format(self.tp_set.name, tp_sel.name, gen_sel.name)
                genReference = self.gen_set.df[(self.gen_set.df.gen > 0)]
                if not gen_sel.all:
                    genReference = self.gen_set.df[(self.gen_set.df.gen > 0)].query(gen_sel.selection)
                    # FIXME: this doesn't work for pizeros since they are never listed in the genParticles...we need a working solution
                    # elif  particle.pdgid == PID.pizero:
                    #     genReference = genParts[(genParts.pid == particle.pdgid)]

                h_tpset_match = self.h_tpset[histo_name]
                h_resoset = self.h_resoset[histo_name]
                h_genseleff = self.h_effset[histo_name]
                h_conecl = self.h_conecluster[histo_name]
                # print 'TPsel: {}, GENsel: {}'.format(tp_sel.name, gen_sel.name)
                # print cl3Ds
                # print cl2Ds
                # print tcs
                self.plot3DClusterMatch(genReference,
                                        cl3Ds,
                                        cl2Ds,
                                        tcs,
                                        h_genseleff.h_den,
                                        h_genseleff.h_num,
                                        h_tpset_match.htc,
                                        h_tpset_match.hcl2d,
                                        h_tpset_match.hcl3d,
                                        h_resoset.hreso,
                                        h_resoset.hresoCone,
                                        h_resoset.hreso2D,
                                        h_conecl,
                                        self.tp_set.name,
                                        debug)

    def __repr__(self):
        return '<{} tps: {}, tps_s: {}, gen:{}, gen_s:{}> '.format(self.__class__.__name__,
                                                                   self.tp_set.name,
                                                                   [sel.name for sel in self.tp_selections],
                                                                   self.gen_set.name,
                                                                   [sel.name for sel in self.gen_selections])


class GenericGenMatchPlotter(BasePlotter):
    def __init__(self, ObjectHistoClass, ResoHistoClass,
                 data_set, gen_set,
                 data_selections=[selections.Selection('all')], gen_selections=[selections.Selection('all')]):
        self.ObjectHistoClass = ObjectHistoClass
        self.ResoHistoClass = ResoHistoClass
        # self.data_set = data_set
        # self.data_selections = data_selections
        # self.gen_set = gen_set
        # self.gen_selections = gen_selections
        self.h_dataset = {}
        self.h_resoset = {}
        self.h_effset = {}
        super(GenericGenMatchPlotter, self).__init__(data_set, data_selections, gen_set, gen_selections)

        # print self
        # print gen_selections

    def plotObjectMatch(self,
                        genParticles,
                        objects,
                        h_gen,
                        h_gen_matched,
                        h_object_matched,
                        h_reso,
                        algoname,
                        debug):
        # fill histo with all selected GEN particles before any match
        if h_gen:
            h_gen.fill(genParticles)

        best_match_indexes = {}
        if not objects.empty:
            best_match_indexes, allmatches = utils.match_etaphi(genParticles[['eta', 'phi']],
                                                                objects[['eta', 'phi']],
                                                                objects['pt'],
                                                                deltaR=0.1)

        for idx, genParticle in genParticles.iterrows():
            if idx in best_match_indexes.keys():
                # print ('-----------------------')
                #  print(genParticle)
                obj_matched = objects.loc[[best_match_indexes[idx]]]
                h_object_matched.fill(obj_matched)
                h_reso.fill(reference=genParticle, target=obj_matched)

                if h_gen_matched is not None:
                    h_gen_matched.fill(genParticles.loc[[idx]])

                if debug >= 4:
                    print ('--- Dump match for algo {} ---------------'.format(algoname))
                    print ('GEN particle: idx: {}'.format(idx))
                    print (genParticle)
                    print ('Matched to track object:')
                    print (obj_matched)
            else:
                if debug >= 5:
                    print ('==== Warning no match found for algo {}, idx {} ======================'.format(algoname, idx))
                    print (genParticle)
                    print (objects)

    def book_histos(self):
        self.gen_set.activate()
        self.data_set.activate()
        for tp_sel in self.data_selections:
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}_{}'.format(self.data_set.name, tp_sel.name, gen_sel.name)
                self.h_dataset[histo_name] = self.ObjectHistoClass(histo_name)
                self.h_resoset[histo_name] = self.ResoHistoClass(histo_name)
                self.h_effset[histo_name] = histos.HistoSetEff(histo_name)

    def fill_histos(self, debug=False):
        for tp_sel in self.data_selections:
            objects = self.data_set.df
            if not tp_sel.all and not self.data_set.df.empty:
                objects = self.data_set.df.query(tp_sel.selection)
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}_{}'.format(self.data_set.name, tp_sel.name, gen_sel.name)
                genReference = self.gen_set.df[(self.gen_set.df.gen > 0)]
                if not gen_sel.all:
                    genReference = self.gen_set.df[(self.gen_set.df.gen > 0)].query(gen_sel.selection)
                    # FIXME: this doesn't work for pizeros since they are never listed in the genParticles...we need a working solution
                    # elif  particle.pdgid == PID.pizero:
                    #     genReference = genParts[(genParts.pid == particle.pdgid)]

                h_obj_match = self.h_dataset[histo_name]
                h_resoset = self.h_resoset[histo_name]
                h_genseleff = self.h_effset[histo_name]
                # print 'TPsel: {}, GENsel: {}'.format(tp_sel.name, gen_sel.name)
                self.plotObjectMatch(genReference,
                                     objects,
                                     h_genseleff.h_den,
                                     h_genseleff.h_num,
                                     h_obj_match,
                                     h_resoset,
                                     self.data_set.name,
                                     debug)


class TrackGenMatchPlotter(GenericGenMatchPlotter):
    def __init__(self, data_set, gen_set,
                 data_selections=[selections.Selection('all')], gen_selections=[selections.Selection('all')]):
        super(TrackGenMatchPlotter, self).__init__(histos.TrackHistos, histos.TrackResoHistos,
                                                   data_set, gen_set,
                                                   data_selections, gen_selections)


class EGGenMatchPlotter(GenericGenMatchPlotter):
    def __init__(self, data_set, gen_set,
                 data_selections=[selections.Selection('all')], gen_selections=[selections.Selection('all')]):
        super(EGGenMatchPlotter, self).__init__(histos.EGHistos, histos.EGResoHistos,
                                                data_set, gen_set,
                                                data_selections, gen_selections)


class TkEGGenMatchPlotter(GenericGenMatchPlotter):
    def __init__(self, data_set, gen_set,
                 data_selections=[selections.Selection('all')], gen_selections=[selections.Selection('all')]):
        super(TkEGGenMatchPlotter, self).__init__(histos.TkEGHistos, histos.EGResoHistos,
                                                  data_set, gen_set,
                                                  data_selections, gen_selections)


# class ResoNtupleMatchPlotter(GenericGenMatchPlotter):
#     def __init__(self, data_set, gen_set,
#                  data_selections=[selections.Selection('all')], gen_selections=[selections.Selection('all')]):
#         super(ResoNtupleMatchPlotter, self).__init__(histos.EGHistos, histos.ResoTuples,
#                                                      data_set, gen_set,
#                                                      data_selections, gen_selections)



class ResoNtupleMatchPlotter(BasePlotter):
    def __init__(self, data_set, gen_set,
                 data_selections=[selections.Selection('all')], gen_selections=[selections.Selection('all')]):

        self.h_calibration = {}
        super(ResoNtupleMatchPlotter, self).__init__(data_set, data_selections, gen_set, gen_selections)

        # print self
        # print gen_selections

    def plotObjectMatch(self,
                        genParticles,
                        objects,
                        h_calibration,
                        algoname,
                        debug):
        best_match_indexes = {}
        if not objects.empty:
            best_match_indexes, allmatches = utils.match_etaphi(genParticles[['eta', 'phi']],
                                                                objects[['eta', 'phi']],
                                                                objects['pt'],
                                                                deltaR=0.1)

        for idx, genParticle in genParticles.iterrows():
            if idx in best_match_indexes.keys():
                # print ('-----------------------')
                #  print(genParticle)
                obj_matched = objects.loc[[best_match_indexes[idx]]]
                # print obj_matched
                # print obj_matched.clusters
                # print obj_matched.clusters[0]
                # print algoname
                # print obj_matched[['energy', 'layer_energy']]
                h_calibration.fill(reference=genParticle, target=obj_matched)

                if debug >= 4:
                    print ('--- Dump match for algo {} ---------------'.format(algoname))
                    print ('GEN particle: idx: {}'.format(idx))
                    print (genParticle)
                    print ('Matched to track object:')
                    print (obj_matched)
            else:
                if debug >= 5:
                    print ('==== Warning no match found for algo {}, idx {} ======================'.format(algoname, idx))
                    print (genParticle)
                    print (objects)

    def book_histos(self):
        self.gen_set.activate()
        self.data_set.activate()
        for tp_sel in self.data_selections:
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}_{}'.format(self.data_set.name, tp_sel.name, gen_sel.name)
                self.h_calibration[histo_name] = histos.ResoTuples(histo_name)

    def fill_histos(self, debug=False):
        for tp_sel in self.data_selections:
            objects = self.data_set.df
            if not tp_sel.all and not self.data_set.df.empty:
                objects = self.data_set.df.query(tp_sel.selection)
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}_{}'.format(self.data_set.name, tp_sel.name, gen_sel.name)
                genReference = self.gen_set.df[(self.gen_set.df.gen > 0)]
                if not gen_sel.all:
                    genReference = self.gen_set.df[(self.gen_set.df.gen > 0)].query(gen_sel.selection)
                    # FIXME: this doesn't work for pizeros since they are never listed in the genParticles...we need a working solution
                    # elif  particle.pdgid == PID.pizero:
                    #     genReference = genParts[(genParts.pid == particle.pdgid)]

                h_calib = self.h_calibration[histo_name]
                # print 'TPsel: {}, GENsel: {}'.format(tp_sel.name, gen_sel.name)
                self.plotObjectMatch(genReference,
                                     objects,
                                     h_calib,
                                     self.data_set.name,
                                     debug)




class CalibrationPlotter(BasePlotter):
    def __init__(self, data_set, gen_set,
                 data_selections=[selections.Selection('all')], gen_selections=[selections.Selection('all')]):

        self.h_calibration = {}
        super(CalibrationPlotter, self).__init__(data_set, data_selections, gen_set, gen_selections)

        # print self
        # print gen_selections

    def plotObjectMatch(self,
                        genParticles,
                        objects,
                        tcs,
                        h_calibration,
                        algoname,
                        debug):
        best_match_indexes = {}
        if not objects.empty:
            best_match_indexes, allmatches = utils.match_etaphi(genParticles[['eta', 'phi']],
                                                                objects[['eta', 'phi']],
                                                                objects['pt'],
                                                                deltaR=0.1)

        for idx, genParticle in genParticles.iterrows():
            if idx in best_match_indexes.keys():
                # print ('-----------------------')
                #  print(genParticle)
                obj_matched = objects.loc[[best_match_indexes[idx]]]
                # print obj_matched
                # print obj_matched.clusters
                # print obj_matched.clusters[0]
                components = tcs[tcs.id.isin(obj_matched.iloc[0].clusters)].copy()
                if 'layer_energy' not in obj_matched.columns:
                    layer_energy = []
                    for layer in range(1, 29, 2):
                        # components[components.layer == layer].energy.sum()
                        layer_energy.append(components[components.layer == layer].energy.sum())
                    obj_matched['layer_energy'] = [layer_energy]

                # print algoname
                # print obj_matched[['energy', 'layer_energy']]
                h_calibration.fill(reference=genParticle, target=obj_matched)

                if debug >= 4:
                    print ('--- Dump match for algo {} ---------------'.format(algoname))
                    print ('GEN particle: idx: {}'.format(idx))
                    print (genParticle)
                    print ('Matched to track object:')
                    print (obj_matched)
            else:
                if debug >= 5:
                    print ('==== Warning no match found for algo {}, idx {} ======================'.format(algoname, idx))
                    print (genParticle)
                    print (objects)

    def book_histos(self):
        self.gen_set.activate()
        self.data_set.activate()
        for tp_sel in self.data_selections:
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}_{}'.format(self.data_set.name, tp_sel.name, gen_sel.name)
                self.h_calibration[histo_name] = histos.CalibrationHistos(histo_name)

    def fill_histos(self, debug=False):
        for tp_sel in self.data_selections:
            objects = self.data_set.df
            if not tp_sel.all and not self.data_set.df.empty:
                objects = self.data_set.df.query(tp_sel.selection)
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}_{}'.format(self.data_set.name, tp_sel.name, gen_sel.name)
                genReference = self.gen_set.df[(self.gen_set.df.gen > 0)]
                if not gen_sel.all:
                    genReference = self.gen_set.df[(self.gen_set.df.gen > 0)].query(gen_sel.selection)
                    # FIXME: this doesn't work for pizeros since they are never listed in the genParticles...we need a working solution
                    # elif  particle.pdgid == PID.pizero:
                    #     genReference = genParts[(genParts.pid == particle.pdgid)]

                h_calib = self.h_calibration[histo_name]
                # print 'TPsel: {}, GENsel: {}'.format(tp_sel.name, gen_sel.name)
                self.plotObjectMatch(genReference,
                                     objects,
                                     self.data_set.tcs.df,
                                     h_calib,
                                     self.data_set.name,
                                     debug)


class TTGenMatchPlotter:
    def __init__(self, tt_set, gen_set,
                 tt_selections=[selections.Selection('all')], gen_selections=[selections.Selection('all')]):
        self.tt_set = tt_set
        self.tt_selections = tt_selections
        self.gen_set = gen_set
        self.gen_selections = gen_selections
        self.h_tt = {}
        self.h_reso_tt = {}
        self.h_reso_ttcl = {}

    def book_histos(self):
        self.tt_set.activate()
        self.gen_set.activate()
        for tp_sel in self.tt_selections:
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}'.format(tp_sel.name, gen_sel.name)
                self.h_tt[histo_name] = histos.TriggerTowerHistos('{}_{}'.format(self.tt_set.name, histo_name))
                self.h_reso_tt[histo_name] = histos.TriggerTowerResoHistos('{}_{}'.format(self.tt_set.name, histo_name))
                self.h_reso_ttcl[histo_name] = histos.TriggerTowerResoHistos('{}Cl_{}'.format(self.tt_set.name, histo_name))

    def fill_histos(self, debug=False):
        triggerTowers_all = self.tt_set.df
        genParts_all = self.gen_set.df[(self.gen_set.df.gen > 0)]
        for tp_sel in self.tt_selections:
            triggerTowers = triggerTowers_all
            if not tp_sel.all:
                triggerTowers = triggerTowers_all.query(tp_sel.selection)
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}'.format(tp_sel.name, gen_sel.name)
                genReference = genParts_all
                if not gen_sel.all:
                    genReference = genParts_all.query(gen_sel.selection)
                self.plotTriggerTowerMatch(genReference,
                                           None,
                                           triggerTowers,
                                           self.h_tt[histo_name],
                                           self.h_reso_tt[histo_name],
                                           self.h_reso_ttcl[histo_name],
                                           "TThighestPt",
                                           debug)

    def plotTriggerTowerMatch(self,
                              genParticles,
                              histoGen,
                              triggerTowers,
                              histoTowersMatch,
                              histoTowersReso,
                              histoTowersResoCl,
                              algoname,
                              debug):

        best_match_indexes = {}
        if triggerTowers.shape[0] != 0:
            best_match_indexes, allmatches = utils.match_etaphi(genParticles[['eta', 'phi']],
                                                                triggerTowers[['eta', 'phi']],
                                                                triggerTowers['pt'],
                                                                deltaR=0.2)
            # print ('-----------------------')
            # print (best_match_indexes)
        # print ('------ best match: ')
        # print (best_match_indexes)
        # print ('------ all matches:')
        # print (allmatches)

        if histoGen is not None:
            histoGen.fill(genParticles)

        for idx, genParticle in genParticles.iterrows():
            if idx in best_match_indexes.keys():
                # print ('-----------------------')
                #  print(genParticle)
                matchedTower = triggerTowers.loc[[best_match_indexes[idx]]]
                # print (matched3DCluster)
                # allMatches = trigger3DClusters.iloc[allmatches[idx]]
                # print ('--')
                # print (allMatches)
                # print (matched3DCluster.clusters.item())
                # print (type(matched3DCluster.clusters.item()))
                # matchedClusters = triggerClusters[ [x in matched3DCluster.clusters.item() for x in triggerClusters.id]]

                # fill the plots
                histoTowersMatch.fill(matchedTower)
                histoTowersReso.fill(reference=genParticle, target=matchedTower)

                ttCluster = clAlgo.buildTriggerTowerCluster(triggerTowers, matchedTower, debug)
                histoTowersResoCl.fill(reference=genParticle, target=ttCluster)

                # clustersInCone = sumClustersInCone(trigger3DClusters, allmatches[idx])
                # print ('----- in cone sum:')
                # print (clustersInCone)
                # histoResoCone.fill(reference=genParticle, target=clustersInCone.iloc[0])

                if debug >= 4:
                    print ('--- Dump match for algo {} ---------------'.format(algoname))
                    print ('GEN particle: idx: {}'.format(idx))
                    print (genParticle)
                    print ('Matched Trigger Tower:')
                    print (matchedTower)
            else:
                if debug >= 0:
                    print ('==== Warning no match found for algo {}, idx {} ======================'.format(algoname, idx))
                    if debug >= 2:
                        print (genParticle)


class CorrOccupancyPlotter(BasePlotter):
    def __init__(self, tp_set, tp_selections=[selections.Selection('all')]):
        self.h_occ = {}
        super(CorrOccupancyPlotter, self).__init__(tp_set, tp_selections)

    def book_histos(self):
        self.tp_set.activate()
        tp_name = self.tp_set.name
        for selection in self.tp_selections:
            self.h_occ[selection.name] = histos.CorrOccupancyHistos(name='{}_{}'.format(tp_name,
                                                                                         selection.name))

    def fill_histos(self, debug=False):
        # print '------------------'
        # print self.tp_set.name
        for selection in self.tp_selections:
            # print selection.selection
            if not selection.all and not self.tp_set.df.empty:
                sel_clusters = self.tp_set.df.query(selection.selection)
            else:
                sel_clusters = self.tp_set.df
            # print sel_clusters

            if not sel_clusters.empty:
                # print trigger_clusters.iloc[0]
                self.h_occ[selection.name].fill(sel_clusters)


class ClusterTCGenMatchPlotter(BasePlotter):
    def __init__(self,  # ResoHistoClass,
                 data_set, gen_set,
                 data_selections=[selections.Selection('all')],
                 gen_selections=[selections.Selection('all')]):
        # self.ResoHistoClass = ResoHistoClass
        self.h_tcmatching = {}
        super(ClusterTCGenMatchPlotter, self).__init__(data_set, data_selections, gen_set, gen_selections)

    def plotObjectMatch(self,
                        genParticles,
                        objects,
                        tcs,
                        h_tc_matched,
                        algoname,
                        debug):
        # fill histo with all selected GEN particles before any match

        best_match_indexes = {}
        if not objects.empty:
            best_match_indexes, allmatches = utils.match_etaphi(genParticles[['eta', 'phi']],
                                                                objects[['eta', 'phi']],
                                                                objects['pt'],
                                                                deltaR=0.1)
        if tcs.empty:
            return

        for idx, genParticle in genParticles.iterrows():
            if idx in best_match_indexes.keys():
                obj_matched = objects.loc[[best_match_indexes[idx]]].iloc[0]
                sel_tcs = tcs[(tcs.z * obj_matched.eta > 0)]
                if sel_tcs.empty:
                    continue

                sel_tcs.loc[sel_tcs.index, 'delta_eta'] = sel_tcs.eta - obj_matched.eta
                sel_tcs.loc[sel_tcs.index, 'delta_phi'] = sel_tcs.apply(lambda tc: ROOT.TVector2.Phi_mpi_pi(tc.phi - obj_matched.phi),
                                                                        axis=1)
                clAlgo.compute_tcs_to_cluster_deltaro(cluster=obj_matched,
                                                      tcs=sel_tcs)

                h_tc_matched.fill(sel_tcs, obj_matched)

                if debug >= 4:
                    print ('--- Dump match for algo {} ---------------'.format(algoname))
                    print ('GEN particle: idx: {}'.format(idx))
                    print (genParticle)

    def book_histos(self):
        self.gen_set.activate()
        self.data_set.activate()
        pass
        for tp_sel in self.data_selections:
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}_{}'.format(self.data_set.name, tp_sel.name, gen_sel.name)
                self.h_tcmatching[histo_name] = histos.TCClusterMatchHistos(histo_name)

    def fill_histos(self, debug=False):
        for tp_sel in self.data_selections:
            objects = self.data_set.df
            if not tp_sel.all and not self.data_set.df.empty:
                objects = self.data_set.df.query(tp_sel.selection)
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}_{}'.format(self.data_set.name, tp_sel.name, gen_sel.name)
                genReference = self.gen_set.df[(self.gen_set.df.gen > 0)]
                if not gen_sel.all:
                    genReference = self.gen_set.df[(self.gen_set.df.gen > 0)].query(gen_sel.selection)
                    # FIXME: this doesn't work for pizeros since they are never listed in the genParticles...we need a working solution
                    # elif  particle.pdgid == PID.pizero:
                    #     genReference = genParts[(genParts.pid == particle.pdgid)]

                h_tc_match = self.h_tcmatching[histo_name]
                # h_resoset = self.h_resoset[histo_name]
                # h_genseleff = self.h_effset[histo_name]
                # print 'TPsel: {}, GENsel: {}'.format(tp_sel.name, gen_sel.name)
                self.plotObjectMatch(genReference,
                                     objects,
                                     self.data_set.tcs.df,
                                     h_tc_match,
                                     self.data_set.name,
                                     debug)



class Cluster3DGenMatchPlotter(BasePlotter):
    def __init__(self, tp_set, gen_set,
                 tp_selections=[selections.Selection('all')], gen_selections=[selections.Selection('all')]):
        # self.tp_set = tp_set
        # self.tp_selections = tp_selections
        # self.gen_set = gen_set
        # self.gen_selections = gen_selections
        self.h_tpset = {}
        self.h_resoset = {}
        self.h_effset = {}
        self.h_dRs = {}
        # self.h_conecluster = {}
        super(Cluster3DGenMatchPlotter, self).__init__(tp_set, tp_selections, gen_set, gen_selections)

    def plot3DMatch(self,
                           genParticles, 
                           trigger3DClusters,
                           triggerClusters,
                           triggerCells,
                           histoGen,
                           histoGenMatched,
                           histo3DClMatch,
                           histo3DClNOMatch,
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

        doPrint="GENPt0toINF" in histoGen.name_

        All3DClusters = trigger3DClusters
        best_match_indexes = {}
        allmatches = {}
        if not trigger3DClusters.empty:
            best_match_indexes, allmatches = utils.match_etaphi(genParticles[['eta', 'phi']],
                                                                trigger3DClusters[['eta', 'phi']],
                                                                trigger3DClusters['pt'],
                                                                deltaR=0.2)
        # if doPrint: 
        # histo_name = '{}_{}_{}'.format(self.tp_set.name, tp_sel.name, gen_sel.name)
        # print self.h_dRs
        dummysplit = histoGen.name_.split("_")
        targethist = dummysplit[2]+"_"+dummysplit[3]+"_"+dummysplit[4]
        # print genParticles
        # print best_match_indexes, allmatches # {0: 1, 1: 3} {0: array([0, 1]), 1: array([2, 3])}
        # print All3DClusters
        # Compute dR between the two simtracks
        if len(genParticles.index)==2:
            GP1=genParticles.iloc[0]
            GP2=genParticles.iloc[1]
            dR = float(np.sqrt((GP1.phi-GP2.phi)**2+(GP1.eta-GP2.eta)**2))
            # print "comparing the two SimTracks"
            # print "\tdR = %s"%(dR)
            self.h_dRs[targethist].h_dR_SimTracks.Fill(dR)
        elif len(genParticles.index)>2:
            print "FOUND AN EVENT WITH NTRACKS>2"

        # Compute dR between the simtrack and any 3D cluster 
        # Use this loop also to compute dR between a simtrack and the best matching 3D cluster
        for iGP,GP in genParticles.iterrows():
            for iCL,CL in All3DClusters.iterrows():
                # print "comparing SimTrack %s with Cluster %s"%(iGP,iCL)
                dR=float(np.sqrt((GP.phi-CL.phi)**2+(GP.eta-CL.eta)**2))
                # print "\tdR = %s\tpT(cluster) = %s"%(dR,CL.pt)
                self.h_dRs[targethist].h_dR_AnyInCone.Fill(dR)
                if iCL==best_match_indexes[iGP]:
                    # print "found best match!"
                    self.h_dRs[targethist].h_dR_BestInCone.Fill(dR)



        if histoGen is not None: 
            histoGen.fill(genParticles) 

        for match in allmatches.values():
            for k in match:
                All3DClusters = All3DClusters.drop(k)
        
        unmatchedClusters = All3DClusters
        for index, row in unmatchedClusters.iterrows():
            histo3DClNOMatch.fill(row)
        

        for idx, genParticle in genParticles.iterrows():

            # if doPrint: print("%s\t%s\t%s\t%s"%(idx,genParticle['pt'],genParticle['eta'],genParticle['phi']))
            # for match in allmatches:
            #     mc = trigger3DClusters.loc[match]
                # if doPrint: print("\t%s\t%s\t%s\t%s"%(mc['pt'],mc['eta'],mc['phi'],idx in best_match_indexes.keys()))

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

                # fill the plots
                histo3DClMatch.fill(matched3DCluster)


                if histoGenMatched is not None: 
                    histoGenMatched.fill(genParticles.loc[[idx]]) 

                if debug >= 6:
                    print ('--- Dump match for algo {} ---------------'.format(algoname))
                    print ('GEN particle: idx: {}'.format(idx))
                    print (genParticle)
                    print ('Matched to 3D cluster:')
                    print (matched3DCluster)

                    #print ('3D cluster energy: {}'.format(matched3DCluster.energy.sum()))
                    #print ('3D cluster pt: {}'.format(matched3DCluster.pt.sum()))
                    #calib_factor = 1.084
                    #print ('sum 2D cluster energy: {}'.format(matchedClusters.energy.sum()*calib_factor))
                    # print ('sum 2D cluster pt: {}'.format(matchedClusters.pt.sum()*calib_factor))
                    #print ('sum TC energy: {}'.format(matchedTriggerCells.energy.sum()))
                    #print ('Sum of matched clusters in cone:')
                    #print (clustersInCone)
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
                self.h_dRs[histo_name] = histos.dRHistos(histo_name)
                # self.h_conecluster[histo_name] = histos.ClusterConeHistos(histo_name)

    def fill_histos(self, debug=False):
        # print "================== new event =================="

        for tp_sel in self.tp_selections:
            tcs = self.tp_set.tc_df
            cl2Ds = self.tp_set.cl2d_df
            cl3Ds = self.tp_set.cl3d_df
            if not tp_sel.all:
                cl3Ds = self.tp_set.cl3d_df.query(tp_sel.selection)
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}_{}'.format(self.tp_set.name, tp_sel.name, gen_sel.name)
                histo_name_NOMATCH = '{}_{}_{}_{}'.format(self.tp_set.name, tp_sel.name, gen_sel.name, "noMatch")
                genReference = self.gen_set.df[(self.gen_set.df.gen > 0)] 
                if not gen_sel.all:
                    genReference = self.gen_set.df[(self.gen_set.df.gen > 0)].query(gen_sel.selection) 
                    # FIXME: this doesn't work for pizeros since they are never listed in the genParticles...we need a working solution
                    # elif  particle.pdgid == PID.pizero:
                    #     genReference = genParts[(genParts.pid == particle.pdgid)]
                h_tpset_match = self.h_tpset[histo_name]
                h_tpset_NOmatch = self.h_tpset[histo_name_NOMATCH]
                h_genseleff = self.h_effset[histo_name]
                self.plot3DMatch(genReference,
                                        cl3Ds,
                                        cl2Ds,
                                        tcs,
                                        h_genseleff.h_den,
                                        h_genseleff.h_num,
                                        h_tpset_match.hcl3d,
                                        h_tpset_NOmatch.hcl3d,
                                        self.tp_set.name,
                                        debug)

    def __repr__(self):
        return '<{} tps: {}, tps_s: {}, gen:{}, gen_s:{}> '.format(self.__class__.__name__,
                                                                   self.tp_set.name,
                                                                   [sel.name for sel in self.tp_selections],
                                                                   self.gen_set.name,
                                                                   [sel.name for sel in self.gen_selections])


class Cluster3DPlotter(BasePlotter):
    def __init__(self, tp_set, tp_selections=[selections.Selection('all')]):
        # self.tp_set = tp_set
        # self.tp_selections = tp_selections
        self.h_tpset = {}
        super(Cluster3DPlotter, self).__init__(tp_set, tp_selections)

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
            if not tp_sel.all:
                cl3Ds = self.tp_set.cl3d_df.query(tp_sel.selection)
            # debug = 4
            # utils.debugPrintOut(debug, '{}_{}'.format(self.tp_set.name, 'TCs'), tcs, tcs[:3])
            # utils.debugPrintOut(debug, '{}_{}'.format(self.tp_set.name, 'CL2D'), cl2Ds, cl2Ds[:3])
            # utils.debugPrintOut(debug, '{}_{}'.format(self.tp_set.name, 'CL3D'), cl3Ds, cl3Ds[:3])
            histo_name='{}_{}_noMatch'.format(self.tp_set.name, tp_sel.name)
            if not cl3Ds.empty:
                for index, row in cl3Ds.iterrows():
                    self.h_tpset[histo_name].fill(row)


class Cluster3DMCMatchPlotter(BasePlotter):
    def __init__(self, tp_set, gen_set,
                 tp_selections=[selections.Selection('all')], gen_selections=[selections.Selection('all')]):
        # self.tp_set = tp_set
        # self.tp_selections = tp_selections
        # self.gen_set = gen_set
        # self.gen_selections = gen_selections
        self.h_tpset = {}
        self.h_resoset = {}
        self.h_effset = {}
        self.h_conecluster = {}
        super(Cluster3DMCMatchPlotter, self).__init__(tp_set, tp_selections, gen_set, gen_selections)

    def plot3DMatch(self,
                           genParticles, 
                           trigger3DClusters,
                           triggerClusters,
                           triggerCells,
                           histoGen,
                           histoGenMatched,
                           histo3DClMatch,
                           histo3DClNOMatch,
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

        All3DClusters = trigger3DClusters
        best_match_indexes = {}
        allmatches = {}
        if not trigger3DClusters.empty:
            best_match_indexes, allmatches = utils.match_etaphi(genParticles[['eta', 'phi']],
                                                                trigger3DClusters[['eta', 'phi']],
                                                                trigger3DClusters['pt'],
                                                                deltaR=0.2)
        if histoGen is not None: 
            histoGen.fill(genParticles) 

        for match in allmatches.values():
            for k in match:
                All3DClusters = All3DClusters.drop(k)
        
        unmatchedClusters = All3DClusters
        for index, row in unmatchedClusters.iterrows():
           histo3DClNOMatch.fill(row)
        
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

                # fill the plots
                histo3DClMatch.fill(matched3DCluster)


                if histoGenMatched is not None: 
                    histoGenMatched.fill(genParticles.loc[[idx]]) 

                if debug >= 6:
                    print ('--- Dump match for algo {} ---------------'.format(algoname))
                    print ('GEN particle: idx: {}'.format(idx))
                    print (genParticle)
                    print ('Matched to 3D cluster:')
                    print (matched3DCluster)
                    #print ('Matched 2D clusters:')
                    #print (matchedClusters)
                    #print ('matched cells:')
                    #print (matchedTriggerCells)

                    #print ('3D cluster energy: {}'.format(matched3DCluster.energy.sum()))
                    #print ('3D cluster pt: {}'.format(matched3DCluster.pt.sum()))
                    #calib_factor = 1.084
                    #print ('sum 2D cluster energy: {}'.format(matchedClusters.energy.sum()*calib_factor))
                    # print ('sum 2D cluster pt: {}'.format(matchedClusters.pt.sum()*calib_factor))
                    #print ('sum TC energy: {}'.format(matchedTriggerCells.energy.sum()))
                    #print ('Sum of matched clusters in cone:')
                    #print (clustersInCone)
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
            #print tp_sel.name, self.tp_set.name
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}_{}'.format(self.tp_set.name,
                                               tp_sel.name,
                                               gen_sel.name)
                histo_name_NOMATCH = '{}_{}_{}_{}'.format(self.tp_set.name, tp_sel.name, gen_sel.name, "noMatch")
                self.h_tpset[histo_name] = histos.HistoSet3DClusters(histo_name)
                self.h_tpset[histo_name_NOMATCH] = histos.HistoSet3DClusters(histo_name_NOMATCH)
                #self.h_resoset[histo_name] = histos.HistoSetReso(histo_name)
                self.h_effset[histo_name] = histos.HistoSetEff(histo_name)
                #self.h_conecluster[histo_name] = histos.ClusterConeHistos(histo_name)

    def fill_histos(self, debug=False):
        for tp_sel in self.tp_selections:
            tcs = self.tp_set.tc_df
            cl2Ds = self.tp_set.cl2d_df
            cl3Ds = self.tp_set.cl3d_df
            if not tp_sel.all:
                cl3Ds = self.tp_set.cl3d_df.query(tp_sel.selection)
            for gen_sel in self.gen_selections:
                histo_name = '{}_{}_{}'.format(self.tp_set.name, tp_sel.name, gen_sel.name)
                histo_name_NOMATCH = '{}_{}_{}_{}'.format(self.tp_set.name, tp_sel.name, gen_sel.name, "noMatch")
                genReference = self.gen_set.df[(self.gen_set.df.pt > -1)] 
                if not gen_sel.all:
                    genReference = self.gen_set.df[(self.gen_set.df.pt > -1)].query(gen_sel.selection)
                    # FIXME: this doesn't work for pizeros since they are never listed in the genParticles...we need a working solution
                    # elif  particle.pdgid == PID.pizero:
                    #     genReference = genParts[(genParts.pid == particle.pdgid)]

                #print self.h_tpset
                h_tpset_match = self.h_tpset[histo_name]
                h_tpset_NOmatch = self.h_tpset[histo_name_NOMATCH]
                h_genseleff = self.h_effset[histo_name]
                self.plot3DMatch(genReference,
                                        cl3Ds,
                                        cl2Ds,
                                        tcs,
                                        h_genseleff.h_den,
                                        h_genseleff.h_num,
                                        h_tpset_match.hcl3d,
                                        h_tpset_NOmatch.hcl3d,
                                        self.tp_set.name,
                                        debug)

    def __repr__(self):
        return '<{} tps: {}, tps_s: {}, gen:{}, gen_s:{}> '.format(self.__class__.__name__,
                                                                   self.tp_set.name,
                                                                   [sel.name for sel in self.tp_selections],
                                                                   self.gen_set.name,
                                                                   [sel.name for sel in self.gen_selections])

if __name__ == "__main__":
    for sel in selections.add_selections(selections.tp_id_selections,
                                         selections.tp_eta_selections):
        print sel

    print selections.add_selections(selections.tp_id_selections,
                                    selections.tp_pt_selections)

    print selections.gen_selection
