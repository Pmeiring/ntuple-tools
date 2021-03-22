"""Provides MVA classifiers."""
import numpy as np
import ROOT
import array

def setup_tmva(model, weight_file, variables):
    from ROOT import TMVA
    reader = TMVA.Reader("!V")

    vardict = {}
    #all variables must be float32
    for ivar in range(0, len(variables)):
        vardict[ivar] = np.array([0], dtype=np.float32)
        reader.AddVariable("f{0}".format(ivar), vardict[ivar])
    tmva = reader.BookMVA("bdt", weight_file)
    return tmva

def book_MVA_classifier(model, weight_file, variables):
    mva_classifier = ROOT.TMVA.Reader()

    for variable in variables:
        mva_classifier.AddVariable(variable, array.array('f', [0.]))
    mva_classifier.BookMVA(model, weight_file)
    return mva_classifier


# setup the EGID classifies
mva_pu_classifier = None


def mva_pu_classifier_builder():
    global mva_pu_classifier
    if mva_pu_classifier is None:
        mva_pu_classifier = book_MVA_classifier(model='BDT',
                                                weight_file='data/MVAnalysis_Bkg_BDTvsPU.weights.xml',
                                                variables=['pt_cl',
                                                           'eta_cl',
                                                           'maxLayer_cl',
                                                           'hOverE_cl',
                                                           'eMaxOverE_cl',
                                                           'sigmaZZ_cl'])
    return mva_pu_classifier


mva_pi_classifier = None


def mva_pi_classifier_builder():
    global mva_pi_classifier
    if mva_pi_classifier is None:
        mva_pi_classifier = book_MVA_classifier(model='BDT',
                                                weight_file='data/MVAnalysis_Bkg_BDTvsPions.weights.xml',
                                                variables=['pt_cl',
                                                           'eta_cl',
                                                           'maxLayer_cl',
                                                           'hOverE_cl',
                                                           'eMaxOverE_cl',
                                                           'sigmaZZ_cl'])
    return mva_pi_classifier



MVA_classifier_lowptloweta = None
MVA_classifier_lowpthigheta = None
MVA_classifier_highptloweta = None
MVA_classifier_highpthigheta = None

def MVA_classifier_builder_lowlow():
    global MVA_classifier_lowptloweta
    if MVA_classifier_lowptloweta is None:
        MVA_classifier_lowptloweta = book_MVA_classifier(model="BDT",
                                                weight_file='data/egid_best9_loweta_lowpt_Histomaxvardr_loweta_low.xml',
                                                variables=['layer90',
                                                           'hoe',
                                                           'srrtot',
                                                           'ntc67',
                                                           'ntc90',
                                                           'coreshowerlength',
                                                           'seetot',
                                                           'layer50',
                                                           'spptot'])
    return MVA_classifier_lowptloweta

def MVA_classifier_builder_lowhigh():
    global MVA_classifier_lowpthigheta
    if MVA_classifier_lowpthigheta is None:
        MVA_classifier_lowpthigheta = book_MVA_classifier(model="BDT",
                                                weight_file='data/egid_best9_higheta_lowpt_Histomaxvardr_higheta_low.xml',
                                                variables=['seetot',
                                                           'layer90',
                                                           'meanz',
                                                           'hoe',
                                                           'ntc90',
                                                           'ntc67',
                                                           'spptot',
                                                           'layer10',
                                                           'emaxe'])
    return MVA_classifier_lowpthigheta


def MVA_classifier_builder_highlow():
    global MVA_classifier_highptloweta
    if MVA_classifier_highptloweta is None:
        MVA_classifier_highptloweta = book_MVA_classifier(model="BDT",
                                                weight_file='data/egid_best9_loweta_Histomaxvardr_loweta_default.xml',
                                                variables=['hoe',
                                                           'srrtot',
                                                           'firstlayer',
                                                           'ntc67',
                                                           'ntc90',
                                                           'layer50',
                                                           'seetot',
                                                           'layer10',
                                                           'emaxe'])
    return MVA_classifier_highptloweta    


def MVA_classifier_builder_highhigh():
    global MVA_classifier_highpthigheta
    if MVA_classifier_highpthigheta is None:
        MVA_classifier_highpthigheta = book_MVA_classifier(model="BDT",
                                                weight_file='data/egid_best9_higheta_Histomaxvardr_higheta_default.xml',
                                                variables=['hoe',
                                                           'ntc67',
                                                           'srrtot',
                                                           'spptot',
                                                           'ntc90',
                                                           'emaxe',
                                                           'layer90',
                                                           'szz',
                                                           'layer50'])
    return MVA_classifier_highpthigheta        