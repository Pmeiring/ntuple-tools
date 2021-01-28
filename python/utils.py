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
            best_match1 = np.argmax(trigger_pt.iloc[matched])
            best_match2 = np.idxmax(trigger_pt.iloc[matched])
            print "bestmatch: ",best_match1, best_match2
            best_match_indices[index] = best_match1
            all_matches_indices[index] = trigger_pt.iloc[matched].index.values
    # print best_match_indices
    # print all_matches_indices
    return best_match_indices, all_matches_indices

def custom_match(ref_etaphi, ref_pt, trigger_etaphi, trigger_pt, deltaR=0.2):
    kdtree = cKDTree(trigger_etaphi)
    best_match_indices = {}
    all_matches_indices = {}

    # Loop over the reference particles and search for the (best) matching trigger objects
    for index, row in ref_etaphi.iterrows():

        matched = kdtree.query_ball_point([row.exeta, row.exphi], deltaR)
        # note this in an integer of the index of the array not the index in the pandas meaning: hence to beused with iloc
        # Handle the -pi pi transition
        matched_sym = kdtree.query_ball_point([row.exeta, row.exphi-np.sign(row.exphi)*2.*m.pi], deltaR)
        # Find the unique entries
        matched = np.unique(np.concatenate((matched, matched_sym))).astype(int)

        if (len(matched) != 0):
            best_match = np.argmax(trigger_pt.iloc[matched])
            best_match_indices[index] = best_match
            all_matches_indices[index] = trigger_pt.iloc[matched].index.values

    return best_match_indices, all_matches_indices

def match_3Dcluster_L1Tk(cluster_etaphi, cluster_pt, L1tk_etaphi, L1tk_pt, deltaR=0.2):
    kdtree = cKDTree(L1tk_etaphi)
    best_match_indices = {}
    matches_indices = {}

    # Loop over the reference particles and search for the (best) matching trigger objects
    # for index, row in cluster_etaphi.iterrows():

    matched = kdtree.query_ball_point([cluster_etaphi.eta, cluster_etaphi.phi], deltaR)
    # note this in an integer of the index of the array not the index in the pandas meaning: hence to beused with iloc
    # Handle the -pi pi transition
    matched_sym = kdtree.query_ball_point([cluster_etaphi.eta, cluster_etaphi.phi-np.sign(cluster_etaphi.phi)*2.*m.pi], deltaR)
    # Find the unique entries
    matched = np.unique(np.concatenate((matched, matched_sym))).astype(int)

    # print matched
    # loop over matched tracks, remove if not satisfying pt requirements
    # print "cluster pT= ",cluster_pt
    matched_=[]
    for idx_L1tk in matched:
        abs_dpT = abs(L1tk_pt[idx_L1tk] - cluster_pt)
        if (abs_dpT/cluster_pt)<0.5: matched_.append(idx_L1tk)
        # print "track pT= ",L1tk_pt[idx_L1tk], (abs_dpT/cluster_pt)<0.5
    matched=matched_

    best_match = None            

    # find the best matching track for this cluster
    if (len(matched) != 0):

        # Take track with highest pT
        best_match = np.argmax(L1tk_pt.iloc[matched])

        #   Determine dR for each simtrack/cluster combi. 
        mindR = 100
        for idx_L1tk, L1tk in L1tk_etaphi.iterrows():
            
            if not idx_L1tk in matched: continue

            dR1 = np.sqrt( pow((cluster_etaphi.eta-L1tk.eta),2) + pow((cluster_etaphi.phi-L1tk.phi),2) )
            dR2 = np.sqrt( pow((cluster_etaphi.eta-L1tk.eta),2) + pow((cluster_etaphi.phi-np.sign(cluster_etaphi.phi)*2.*m.pi-L1tk.phi),2) )
            dR = min([dR1,dR2])
            # print "track ",idx_L1tk, L1tk.eta, L1tk.phi, dR
            if dR<mindR:
                mindR = dR
                best_match = idx_L1tk

    return best_match, matched


def debugPrintOut(level, name, toCount, toPrint):
    if level == 0:
        return
    if level >= 3:
        print('# {}: {}'.format(name, len(toCount)))
    if level >= 4 and not toPrint.empty:
        print(toPrint)


def do_all_matches(GP, L1Objects, dR_cone, useExtrapolatedGenCoords=False):

    L1Objects_etaphi = L1Objects[['eta','phi']]
    L1Objects_pt = L1Objects['pt']
    kdtree = cKDTree(L1Objects_etaphi)

    GP_eta=GP.eta
    GP_phi=GP.phi
    if useExtrapolatedGenCoords:
        GP_eta=GP.exeta
        GP_phi=GP.exphi

    idx_closestDRL1object=-1
    idx_closestPTL1object=-1 
    idx_highestPTL1object=-1


    # Match with dR cone and take care of +pi -pi transition
    matched = kdtree.query_ball_point([GP_eta, GP_phi], dR_cone)
    matched_sym = kdtree.query_ball_point([GP_eta, GP_phi-np.sign(GP_phi)*2.*m.pi], dR_cone)
    matched = np.unique(np.concatenate((matched, matched_sym))).astype(int)

    # Best match = highest pT L1 Object matched to GEN
    if (len(matched) != 0):
        idx_highestPTL1object = np.argmax(L1Objects_pt.iloc[matched])

    # Best match = closest dR L1 Object matched to GEN OR
    # Best match = closest pT L1 Object matched to GEN 
    mindR = 10000
    mindPt= 10000
    for idx_L1Object, L1Object in L1Objects_etaphi.iterrows():
        if not idx_L1Object in matched: continue
        dR1 = np.sqrt( pow((L1Object.eta-GP_eta),2) + pow((L1Object.phi-GP_phi),2) )
        dR2 = np.sqrt( pow((L1Object.eta-GP_eta),2) + pow((L1Object.phi-np.sign(L1Object.phi)*2.*m.pi-GP_phi),2) )
        dR = min(dR1,dR2)
        dPt = abs(L1Objects_pt[idx_L1Object]/GP.pt - 1)
        # print "matched cluster pT, dpT, dR, eta, phi = ", L1Objects_pt[idx_L1Object], dPt, dR, L1Object.eta, L1Object.phi
        if dR<mindR:
            mindR = dR
            idx_closestDRL1object = idx_L1Object
        if dPt<mindPt:
            mindPt= dPt
            idx_closestPTL1object = idx_L1Object

    return matched, idx_closestDRL1object, idx_highestPTL1object, idx_closestPTL1object