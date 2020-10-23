import math as m
import numpy as np
from scipy.spatial import cKDTree


def match_etaphi(ref_etaphi, trigger_etaphi, trigger_pt, deltaR=0.2):
    '''Match objects within a given DeltaR. Returns the panda index of the best match (highest-pt)
       and of all the matches'''
    # print "INPUT ref_etaphi"
    # print ref_etaphi
    # print "INPUT trigger_etaphi"
    # print trigger_etaphi
    # print "INPUT trigger_pt"
    # print trigger_pt
    #print "deltaR: ", deltaR
    kdtree = cKDTree(trigger_etaphi)
    best_match_indices = {}
    all_matches_indices = {}
    # for iref,(eta,phi) in enumerate(ref_etaphi):
    for index, row in ref_etaphi.iterrows():
        matched = kdtree.query_ball_point([row.eta, row.phi], deltaR)
        # not this in an integer of the index of the array not the index in the pandas meaning: hence to beused with iloc
        # Handle the -pi pi transition
        matched_sym = kdtree.query_ball_point([row.eta, row.phi-np.sign(row.phi)*2.*m.pi], deltaR)
        matched = np.unique(np.concatenate((matched, matched_sym))).astype(int)
        # print matched
        # print type(matched)
        # print trigger_pt[matched]
        # print trigger_etaphi.iloc[matched]
        # Choose the match with highest pT
        if (len(matched) != 0):
            best_match = np.argmax(trigger_pt.iloc[matched])
            best_match_indices[index] = best_match
            all_matches_indices[index] = trigger_pt.iloc[matched].index.values
    # print best_match_indices
    # print all_matches_indices
    return best_match_indices, all_matches_indices

def custom_match(ref_etaphi, ref_pt, trigger_etaphi, trigger_pt, deltaR=0.2):
    kdtree = cKDTree(trigger_etaphi)
    best_match_indices = {}
    all_matches_indices = {}
    for index, row in ref_etaphi.iterrows():
        # print "GP ",index

        matched = kdtree.query_ball_point([row.eta, row.phi], deltaR)
        # print "first matched", matched
        # closest_dr = kdtree.query([row.eta, row.phi])
        # matched_mindr=[closest_dr[1]] if closest_dr[0]<deltaR else []
        # print "matched ",matched_mindr

        # not this in an integer of the index of the array not the index in the pandas meaning: hence to beused with iloc
        # Handle the -pi pi transition
        matched_sym = kdtree.query_ball_point([row.eta, row.phi-np.sign(row.phi)*2.*m.pi], deltaR)
        # print "sym matched", matched_sym
        # closest_drsym = kdtree.query([row.eta, row.phi-np.sign(row.phi)*2.*m.pi])
        # matched_mindrsym=[closest_drsym[1]] if closest_drsym[0]<deltaR else []
        # print "matched sym ",matched_mindrsym
        # Find the unique entries
        matched = np.unique(np.concatenate((matched, matched_sym))).astype(int)
        # matched_mindr= np.unique(np.concatenate((matched_mindr, matched_mindrsym))).astype(int)


        # print "matched_mindr ",matched_mindr

        if (len(matched) != 0):
            #   Determine dR for each simtrack/cluster combi. 
            mindR = deltaR
            best_match3 = None            
            for itr, rowtr in trigger_etaphi.iterrows():
                dR1 = np.sqrt( pow((row.eta-rowtr.eta),2) + pow((row.phi-rowtr.phi),2) )
                dR2 = np.sqrt( pow((row.eta-rowtr.eta),2) + pow((row.phi-np.sign(row.phi)*2.*m.pi-rowtr.phi),2) )
                dR = min([dR1,dR2])
                if dR<mindR:
                    mindR = dR
                    best_match3 = itr


            # print matched
            dpT = abs(trigger_pt-ref_pt[index])
            # print row.eta, row.phi, ref_pt[index]
            # print trigger_etaphi
            # print trigger_pt

            best_match = np.argmax(trigger_pt.iloc[matched])
            best_match2 = np.argmin(dpT.iloc[matched])
            # best_match3 = matched_mindr[0]

            # print "pt ratio: "
            # print trigger_pt/ref_pt[index]
            # print "bestmatch = ",best_match, best_match2, best_match3

            best_match_indices[index] = best_match2
            all_matches_indices[index] = trigger_pt.iloc[matched].index.values
    # print best_match_indices
    # print all_matches_indices
    return best_match_indices, all_matches_indices

def debugPrintOut(level, name, toCount, toPrint):
    if level == 0:
        return
    if level >= 3:
        print('# {}: {}'.format(name, len(toCount)))
    if level >= 4 and not toPrint.empty:
        print(toPrint)
