"""Provides MVA classifiers."""

import ROOT
import array


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


MVA_classifier_lowetalowpt = None
MVA_classifier_lowetahighpt = None
MVA_classifier_highetalowpt = None
MVA_classifier_highetahighpt = None

def MVA_classifier_builder_lowlow():
    global MVA_classifier_lowetalowpt
    if MVA_classifier_lowetalowpt is None:
        MVA_classifier_lowetalowpt = book_MVA_classifier(model="BDT",
                                                # weight_file='data/egid_best9_loweta_lowpt_Histomaxvardr_loweta_low.xml',
                                                weight_file='data/egid_allvars_Histomaxvardr_loweta_low.xml',
                                                # variables=['layer90',
                                                #            'hoe',
                                                #            'srrtot',
                                                #            'ntc67',
                                                #            'ntc90',
                                                #            'coreshowerlength',
                                                #            'seetot',
                                                #            'layer50',
                                                #            'spptot'])
                                                variables=['coreshowerlength','showerlength','firstlayer','maxlayer','szz','srrmean','srrtot','seetot','spptot', 'seemax', 'sppmax', 'srrmax', 'meanz', 'emaxe', 'layer10', 'layer50', 'layer90', 'ntc67', 'ntc90', 'hoe'])
                                 
    return MVA_classifier_lowetalowpt



def MVA_classifier_builder_highlow():
    global MVA_classifier_highetalowpt
    if MVA_classifier_highetalowpt is None:
        MVA_classifier_highetalowpt = book_MVA_classifier(model="BDT",
                                                weight_file='data/egid_allvars_Histomaxvardr_higheta_low.xml',
                                                # variables=['seetot',
                                                #            'layer90',
                                                #            'meanz',
                                                #            'hoe',
                                                #            'ntc90',
                                                #            'ntc67',
                                                #            'spptot',
                                                #            'layer10',
                                                #            'emaxe'])
                                                variables=['coreshowerlength','showerlength','firstlayer','maxlayer','szz','srrmean','srrtot','seetot','spptot', 'seemax', 'sppmax', 'srrmax', 'meanz', 'emaxe', 'layer10', 'layer50', 'layer90', 'ntc67', 'ntc90', 'hoe'])
    return MVA_classifier_highetalowpt


def MVA_classifier_builder_lowhigh():
    global MVA_classifier_lowetahighpt
    if MVA_classifier_lowetahighpt is None:
        MVA_classifier_lowetahighpt = book_MVA_classifier(model="BDT",
                                                weight_file='data/egid_allvars_Histomaxvardr_loweta_high.xml',
                                                # variables=['hoe',
                                                #            'srrtot',
                                                #            'firstlayer',
                                                #            'ntc67',
                                                #            'ntc90',
                                                #            'layer50',
                                                #            'seetot',
                                                #            'layer10',
                                                #            'emaxe'])
                                                variables=['coreshowerlength','showerlength','firstlayer','maxlayer','szz','srrmean','srrtot','seetot','spptot', 'seemax', 'sppmax', 'srrmax', 'meanz', 'emaxe', 'layer10', 'layer50', 'layer90', 'ntc67', 'ntc90', 'hoe'])
    return MVA_classifier_lowetahighpt    


def MVA_classifier_builder_highhigh():
    global MVA_classifier_highetahighpt
    if MVA_classifier_highetahighpt is None:
        MVA_classifier_highetahighpt = book_MVA_classifier(model="BDT",
                                                weight_file='data/egid_allvars_Histomaxvardr_higheta_high.xml',
                                                # variables=['hoe',
                                                #            'ntc67',
                                                #            'srrtot',
                                                #            'spptot',
                                                #            'ntc90',
                                                #            'emaxe',
                                                #            'layer90',
                                                #            'szz',
                                                #            'layer50'])
                                                variables=['coreshowerlength','showerlength','firstlayer','maxlayer','szz','srrmean','srrtot','seetot','spptot', 'seemax', 'sppmax', 'srrmax', 'meanz', 'emaxe', 'layer10', 'layer50', 'layer90', 'ntc67', 'ntc90', 'hoe'])
    return MVA_classifier_highetahighpt  