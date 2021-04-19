"""
Define and instantiate the selections.

The Selection class define via string a selection to be pplied to a certain
DataFrame. The selections are named (the name enters the final histogram name).
Selections can be composed (added). The actual selection syntax follows the
`pandas` `DataFrame` `query` syntax.
"""


class PID:
    electron = 11
    photon = 22
    pizero = 111
    pion = 211
    kzero = 130


class SelectionManager(object):
    """
    SelectionManager.

    Manages the registration of selections to have a global dictionary of the labels for drawing.

    It is a singleton.
    """

    class __TheManager:
        def __init__(self):
            self.selections = []

        def registerSelection(self, selection):
            # print '[EventManager] registering collection: {}'.format(collection.name)
            self.selections.append(selection)

        def get_labels(self):
            label_dict = {}
            for sel in self.selections:
                label_dict[sel.name] = sel.label
            return label_dict

    instance = None

    def __new__(cls):
        if not SelectionManager.instance:
            SelectionManager.instance = SelectionManager.__TheManager()
        return SelectionManager.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name):
        return setattr(self.instance, name)




class Selection:
    """
    [Selection] class.

    Args:
        name (string): the name to be used in the histo name
                       (should not use `-` characters or spaces)

        label (string): used in plot legends, no constraints
        selection (string): see pandas.DataFrame.query syntax
    """

    def __init__(self, name, label='', selection=''):
        self.name = name
        self.label = label
        self.selection = selection
        self.hash = hash(selection)
        self.register()

    def register(self):
        selection_manager = SelectionManager()
        selection_manager.registerSelection(self)

    def __add__(self, sel_obj):
        """ & operation """
        if sel_obj.all:
            return self
        if self.all:
            return sel_obj
        new_label = '{}, {}'.format(self.label, sel_obj.label)
        if self.label == '':
            new_label = sel_obj.label
        if sel_obj.label == '':
            new_label = self.label
        return Selection(name='{}{}'.format(self.name, sel_obj.name),
                         label=new_label,
                         selection='({}) & ({})'.format(self.selection, sel_obj.selection))

    def __str__(self):
        return 'n: {}, s: {}, l:{}'.format(self.name, self.selection, self.label)

    def __repr__(self):
        return '<{} n: {}, s: {}, l:{}> '.format(self.__class__.__name__,
                                                 self.name,
                                                 self.selection,
                                                 self.label)

    @property
    def all(self):
        if self.name == 'all':
            return True
        return False


def add_selections(list1, list2):
    ret = []
    for sel1 in list1:
        for sel2 in list2:
            ret.append(sel1+sel2)
    return ret


def prune(selection_list):
    sel_names = set()
    ret = []
    for sel in selection_list:
        if sel.name not in sel_names:
            sel_names.add(sel.name)
            ret.append(sel)
    return ret

# TP selections
no_selections = [Selection('all', '', '')]    

tp_id_selections = [
                    Selection('all', '', ''),
                    ##COMMENT FOR TEST Selection('Em', 'EGId', 'quality >0'),
                    # Selection('Emv1', 'EGId V1', '(showerlength > 1) & (bdt_pu > 0.026) & (bdt_pi > -0.03)')
                    ]

tp_rate_id_selections = [Selection('all', '', ''),
                         Selection('Em', 'EGId', 'quality >0'),]


tp_pt_selections = [Selection('all', '', ''),
                    Selection('Pt5to20', '5 < p_{T}^{L1} <= 20GeV', '(pt <= 20) & (pt > 5)'),
                    Selection('Pt20', 'p_{T}^{L1}>20GeV', 'pt > 20')
                    # Selection('Pt25', 'p_{T}^{L1}>=25GeV', 'pt >= 25'),
                    ##COMMENTFORTESTSelection('Pt30', 'p_{T}^{L1}>=30GeV', 'pt >= 30')
                    ]

tp_pt_selections_forBDT_bkg = [Selection('all', '', ''),
                    Selection('Pt5to20', '5 < p_{T}^{L1} <= 20GeV', '(pt <= 20) & (pt > 5)'),
                    Selection('Pt20', 'p_{T}^{L1}>20GeV', 'pt > 20')
                    ]                    

tp_pt_selections_forBDT_sig = [Selection('all', '', ''),
                               Selection('Pt10', 'p_{T}^{L1}>=10GeV', 'pt >= 10'),
                               Selection('Pt5to30', '5 <= p_{T}^{L1} <= 30GeV', '(pt <= 30) & (pt >= 5)'),
                    ]

tp_pt_selections_ext = [Selection('all', '', ''),
                        Selection('Pt10', 'p_{T}^{L1}>=10GeV', 'pt >= 10'),
                        Selection('Pt15', 'p_{T}^{L1}>=15GeV', 'pt >= 15'),
                        Selection('Pt20', 'p_{T}^{L1}>=20GeV', 'pt >= 20'),
                        Selection('Pt25', 'p_{T}^{L1}>=25GeV', 'pt >= 25'),
                        Selection('Pt30', 'p_{T}^{L1}>=30GeV', 'pt >= 30'),
                        Selection('Pt40', 'p_{T}^{L1}>=40GeV', 'pt >= 40')
                        ]

tp_pt_selections_occ = [Selection('all', '', ''),
                        Selection('Pt5', 'p_{T}^{L1}>=5GeV', 'pt >= 5'),
                        Selection('Pt10', 'p_{T}^{L1}>=10GeV', 'pt >= 10'),
                        Selection('Pt15', 'p_{T}^{L1}>=15GeV', 'pt >= 15'),
                        Selection('Pt20', 'p_{T}^{L1}>=20GeV', 'pt >= 20'),
                        ]


tp_tccluster_match_selections = [Selection('all', '', ''),
                                 Selection('Pt5to10', '5 <= p_{T}^{L1} < 10GeV', '(pt < 10) & (pt >= 5)'),
                                 Selection('Pt10to20', '10 <= p_{T}^{L1} < 20GeV', '(pt < 20) & (pt >= 10)')]




tp_calib_pt_selections = [Selection('all', '', ''),
                          Selection('Pt10', 'p_{T}^{L1}>=10GeV', 'pt >= 10'),
                          Selection('Pt20', 'p_{T}^{L1}>=20GeV', 'pt >= 20'),
                    # # Selection('Pt25', 'p_{T}^{L1}>=25GeV', 'pt >= 25'),
                    # Selection('Pt30', 'p_{T}^{L1}>=30GeV', 'pt >= 30')
                    ]

tp_eta_selections = [#Selection('all', '', ''),
                     # Selection('EtaA', '|#eta^{L1}| <= 1.52', 'abs(eta) <= 1.52'),
                     # Selection('EtaB', '1.52 < |#eta^{L1}| <= 1.7', '1.52 < abs(eta) <= 1.7'),
                     # Selection('EtaC', '1.7 < |#eta^{L1}| <= 2.4', '1.7 < abs(eta) <= 2.4'),
                     #Selection('EtaD', '2.4 < |#eta^{L1}| <= 2.7', '2.4 < abs(eta) <= 2.7'),
                     # Selection('EtaDE', '2.7 < |#eta^{L1}| <= 3.0', '2.7 < abs(eta) <= 3.0'),
                     # Selection('EtaE', '|#eta^{L1}| > 2.8', 'abs(eta) > 2.8'),
                     # Selection('EtaAB', '|#eta^{L1}| <= 1.7', 'abs(eta) <= 1.7'),
                     # Selection('EtaABC', '|#eta^{L1}| <= 2.4', 'abs(eta) <= 2.4'),
                     Selection('EtaBC', '1.52 < |#eta^{L1}| <= 2.7', '1.52 < abs(eta) <= 2.7'),
                     # Selection('EtaBCD', '1.52 < |#eta^{L1}| <= 2.8', '1.52 < abs(eta) <= 2.8'),
                     #Selection('EtaBCDE', '1.52 < |#eta^{L1}| < 3', '1.52 < abs(eta) < 3')
                     ]

tp_eta_selections_forBDT = [Selection('EtaBC', '1.52 < |#eta^{L1}| <= 2.7', '1.52 < abs(eta) <= 2.7'),
                     Selection('EtaDE', '2.7 < |#eta^{L1}| <= 3', '2.7 < abs(eta) <= 3'),
                     # Selection('EtaBCDE', '1.52 < |#eta^{L1}| < 3', '1.52 < abs(eta) < 3')
                     ]

# tp_BDT_selections = [Selection('BDT_tpg997', 'bdt_eg > 0.03496629')]


tp_rate_selections = add_selections(tp_rate_id_selections, tp_eta_selections)

#MY SELECTIONS
# tp_match_selections = tp_pt_selections
#tp_match_selections += add_selections(tp_id_selections, tp_pt_selections) 
tp_match_selections = add_selections(tp_pt_selections, tp_eta_selections)




tp_loweta  = [Selection('EtaBC', '1.52 < |#eta^{L1}| <= 2.7', '1.52 < abs(eta) <= 2.7')]
tp_higheta = [Selection('EtaDE', '2.7 < |#eta^{L1}| <= 3', '2.7 < abs(eta) <= 3')]
tp_noID = tp_loweta + tp_higheta

tp_IDtpg__loweta__lowpt = add_selections(tp_loweta, [Selection('tpgID900_lowetalowpt',  'passed ID WP900: low eta, low pt',  'bdteg>-0.9969856')])
tp_IDtpg_higheta__lowpt = add_selections(tp_loweta, [Selection('tpgID900_highetalowpt', 'passed ID WP900: high eta, low pt', 'bdteg>-0.9989121')])
tp_IDtpg__loweta_highpt = add_selections(tp_loweta, [Selection('tpgID900_lowetahighpt', 'passed ID WP900: low eta, high pt', 'bdteg>0.9967954')])
tp_IDtpg_higheta_highpt = add_selections(tp_loweta, [Selection('tpgID900_highetahighpt','passed ID WP900: high eta, high pt','bdteg>0.9972339')])
tp_IDtpg = tp_IDtpg__loweta__lowpt + tp_IDtpg_higheta__lowpt + tp_IDtpg__loweta_highpt + tp_IDtpg_higheta_highpt

tp_IDnew__loweta__lowpt = add_selections(tp_loweta, [Selection('newID900_lowetalowpt',  'passed ID WP900: low eta, low pt',  'bdteg>-0.7489949')])
tp_IDnew_higheta__lowpt = add_selections(tp_loweta, [Selection('newID900_highetalowpt', 'passed ID WP900: high eta, low pt', 'bdteg>-0.8880973')])
tp_IDnew__loweta_highpt = add_selections(tp_loweta, [Selection('newID900_lowetahighpt', 'passed ID WP900: low eta, high pt', 'bdteg>0.9905590')])
tp_IDnew_higheta_highpt = add_selections(tp_loweta, [Selection('newID900_highetahighpt','passed ID WP900: high eta, high pt','bdteg>0.9893420')])
tp_IDnew = tp_IDnew__loweta__lowpt + tp_IDnew_higheta__lowpt + tp_IDnew__loweta_highpt + tp_IDnew_higheta_highpt

tp_selections_rateeff = tp_noID + tp_IDtpg + tp_IDnew










tp_calib_selections = tp_id_selections


genpart_ele_selections = [Selection('Ele', 'e^{#pm}', 'abs(pdgid) == {}'.format(PID.electron))]
genpart_photon_selections = [Selection('Phot', '#gamma', 'abs(pdgid) == {}'.format(PID.photon))]                      #
genpart_pion_selections = [Selection('Pion', '#pi', 'abs(pdgid) == {}'.format(PID.pion))]


#gen_ee_selections = [Selection('', '', 'reachedEE >= 1')]
gen_ee_selections = [Selection('all')]


gen_eta_selections = [
                      # Selection('EtaA', '|#eta^{GEN}| <= 1.52', 'abs(eta) <= 1.52'),
                      # Selection('EtaB', '1.52 < |#eta^{GEN}| <= 1.7', '1.52 < abs(eta) <= 1.7'),
                      # Selection('EtaC', '1.7 < |#eta^{GEN}| <= 2.4', '1.7 < abs(eta) <= 2.4'),
                      #Selection('EtaD', '2.4 < |#eta^{GEN}| <= 2.8', '2.4 < abs(eta) <= 2.8'),
                      Selection('EtaDE', '2.7 < |#eta^{GEN}| <= 3.0', '2.7 < abs(eta) <= 3.0'),
                      # Selection('EtaE', '|#eta^{GEN}| > 2.8', 'abs(eta) > 2.8'),
                      # Selection('EtaAB', '|#eta^{GEN}| <= 1.7', 'abs(eta) <= 1.7'),
                      # Selection('EtaABC', '|#eta^{GEN}| <= 2.4', 'abs(eta) <= 2.4'),
                      Selection('EtaBC', '1.52 < |#eta^{GEN}| <= 2.7', '1.52 < abs(eta) <= 2.7'),
                      #Selection('EtaBCD', '1.52 < |#eta^{GEN}| <= 2.8', '1.52 < abs(eta) <= 2.8'),
                      # Selection('EtaBCDE', '1.52 < |#eta^{GEN}|', '1.52 < abs(eta)')
                      ]

gen_exeta_selections = [
                      Selection('EtaDE', '2.7 < |#eta^{GEN}| <= 3.0', '2.7 < abs(exeta) <= 3.0'),
                      Selection('EtaBC', '1.52 < |#eta^{GEN}| <= 2.7', '1.52 < abs(exeta) <= 2.7'),
]

gen_eta_sel = [Selection('EtaDE', '2.4 < |#eta^{GEN}| <= 3.0', '2.4 < abs(eta) <= 3.0'),
               Selection('EtaBC', '1.52 < |#eta^{GEN}| <= 2.4', '1.52 < abs(eta) <= 2.4'),
               Selection('EtaBCD', '1.52 < |#eta^{GEN}| <= 2.8', '1.52 < abs(eta) <= 2.8'),
                      ]


gen_eta_barrel_selections = [Selection('EtaF', '|#eta^{GEN}| <= 1.479', 'abs(eta) <= 1.479')]
gen_eta_be_selections = [Selection('EtaF', '|#eta^{GEN}| <= 1.479', 'abs(eta) <= 1.479'),
                         Selection('EtaD', '2.4 < |#eta^{GEN}| <= 2.8', '2.4 < abs(eta) <= 2.8'),
                         Selection('EtaBC', '1.52 < |#eta^{GEN}| <= 2.4', '1.52 < abs(eta) <= 2.4'),
                         Selection('EtaBCD', '1.52 < |#eta^{GEN}| <= 2.8', '1.52 < abs(eta) <= 2.8')
                         ]


eta_barrel_selections = [Selection('all'), Selection('EtaF', '|#eta^{L1}| <= 1.479', 'abs(eta) <= 1.479')]
eta_be_selections = [Selection('all'),
                     Selection('EtaF', '|#eta^{L1}| <= 1.479', 'abs(eta) <= 1.479'),
                     Selection('EtaA', '|#eta^{L1}| <= 1.52', 'abs(eta) <= 1.52'),
                     Selection('EtaBC', '1.52 < |#eta^{L1}| <= 2.4', '1.52 < abs(eta) <= 2.4')
                     ]
barrel_quality_selections = [Selection('all'),
                             Selection('LooseTkID', 'LooseTkID', 'looseTkID'),
                             Selection('Iso0p1', 'Iso0p1', '((tkIso <= 0.1) & (abs(eta) <= 1.479)) | ((tkIso <= 0.125) & (abs(eta) > 1.479))'),
                             ]

barrel_rate_selections = add_selections(eta_barrel_selections, barrel_quality_selections)
all_rate_selections = prune(eta_be_selections+barrel_rate_selections)

eg_barrel_rate_selections = [sel for sel in barrel_rate_selections if 'Iso' not in sel.name]
eg_all_rate_selections = [sel for sel in all_rate_selections if 'Iso' not in sel.name]


gen_pt_selection15 = [Selection('all'),
                      Selection('Pt15', 'p_{T}^{GEN}>=15GeV', 'pt >= 15')]

gen_pt_selections = [Selection("Pt0toINF", 'p_{T}^{GEN} #leq 0 GeV', 'pt >= 0'),
                     #Selection('Pt0to5', '0 #leq p_{T}^{GEN} < 5GeV', '(pt >= 0) & (pt < 5)'),
                     #Selection('Pt5to10', '5 #leq p_{T}^{GEN} < 10GeV', '(pt >= 5) & (pt < 10)'),
                     Selection('Pt0to10', '0 #leq p_{T}^{GEN} < 10GeV', '(pt >= 0) & (pt < 10)'),
                     #Selection('Pt10to15', '10 #leq p_{T}^{GEN} < 15GeV', '(pt >= 10) & (pt < 15)'),
                     Selection('Pt10to20', '10 #leq p_{T}^{GEN} < 20GeV', '(pt >= 10) & (pt < 20)'),
                     #Selection('Pt15to20', '15 #leq p_{T}^{GEN} < 20GeV', '(pt >= 15) & (pt < 20)'),
                     #Selection('Pt20to30', '20 #leq p_{T}^{GEN} < 30GeV', '(pt >= 20) & (pt < 30)'),
                     #Selection('Pt30to40', '30 #leq p_{T}^{GEN} < 40GeV', '(pt >= 30) & (pt < 40)'),
                     #Selection('Pt40', 'p_{T}^{GEN}>=40GeV', 'pt >= 40'),
                     Selection('Pt20toINF', 'p_{T}^{GEN} #leq 20GeV', 'pt >= 20')
                     ]


# gen_pt_sel = [Selection('Pt15', 'p_{T}^{GEN}>=15GeV', 'pt >= 15'),
#                      # Selection('Pt10to25', '10 #leq p_{T}^{GEN} < 25GeV', '(pt >= 10) & (pt < 25)'),
#                      # Selection('Pt20', 'p_{T}^{GEN}>=20GeV', 'pt >= 20'),
#                      Selection('Pt30', 'p_{T}^{GEN}>=30GeV', 'pt >= 30'),
#                      # Selection('Pt35', 'p_{T}^{GEN}>=35GeV', 'pt >= 35'),
#                      Selection('Pt40', 'p_{T}^{GEN}>=40GeV', 'pt >= 40')]

gen_pt_sel = [Selection('all', '', ''),
                     # Selection('Pt5to20', '5 #leq p_{T}^{GEN} <= 20GeV', '(pt >= 5) & (pt <= 20)'),
                     # Selection('Pt20', 'p_{T}^{GEN}>=20GeV', 'pt > 20'),
                     # Selection('Pt15', 'p_{T}^{GEN}>=15GeV', 'pt > 15'),
                     # Selection('Pt30', 'p_{T}^{GEN}<=30GeV', 'pt < 30'),
]

gen_pt_sel_test = [Selection('Pt0to5',    '0 #leq p_{T}^{GEN} < 5GeV',  '(pt >= 0) & (pt < 5)'),
                   Selection('Pt5to10',   '5 #leq p_{T}^{GEN} < 10GeV', '(pt >= 5) & (pt < 10)'),
                   Selection('Pt10to15', '10 #leq p_{T}^{GEN} < 15GeV', '(pt >= 10) & (pt < 15)'),
                   Selection('Pt15to20', '15 #leq p_{T}^{GEN} < 20GeV', '(pt >= 15) & (pt < 20)'),
                   Selection('Pt20to25', '20 #leq p_{T}^{GEN} < 25GeV', '(pt >= 20) & (pt < 25)'),
                   Selection('Pt25toINF', 'p_{T}^{GEN} #leq 20GeV', 'pt >= 25')
]

# gen_part_selections = [Selection('GEN', '', '(abs(pdgid) == {}) | (abs(pdgid) == {}) | (abs(pdgid) == {})'.format(PID.electron, PID.photon, PID.pion))]
# gen_part_selections = [Selection('GEN', '', '(abs(pdgid) == {}) & (firstmother_pdgid == {})'.format(PID.electron, PID.electron))]
# FIXME: add fabs to firstmother_if
#add pions here


gen_selections = [Selection('GEN', '', '((abs(pdgid) == {}) & (abs(firstmother_pdgid) == {})) | ((abs(pdgid) == {}) & (abs(firstmother_pdgid) == {})) | ((abs(pdgid) == {}) & (abs(firstmother_pdgid) == {}))'.format(PID.electron, PID.electron,
                                                                                                                                                    PID.photon, PID.photon, PID.pion, PID.pion
                                        ))]


# gen_selections = [Selection('GEN', '', '(abs(pdgid) == {}) & (abs(firstmother_pdgid) == {})'.format(PID.electron, PID.electron))]

#gen_selections = [Selection('GEN', '', '')]


gen_debug = [Selection('all', '', '')] 

MC_selections = [Selection('all', '', '')]

gen_photon_sel = [Selection('GEN', '', '((abs(pdgid) == {}) & (abs(firstmother_pdgid) == {}) & (reachedEE == 2))'.format(PID.photon, PID.photon))]
# gen_photon_sel = [Selection('GEN', '', '((abs(pdgid) == {}) & (abs(firstmother_pdgid) == {}))'.format(PID.photon, PID.photon))]

gen_ele_sel = [Selection('GEN', '', '((abs(pdgid) == {}) & (abs(firstmother_pdgid) == {}) & (reachedEE == 2))'.format(PID.electron, PID.electron))]
# gen_ele_sel = [Selection('GEN', '', '((abs(pdgid) == {}) & (abs(firstmother_pdgid) == {}) )'.format(PID.electron, PID.electron))]

gen_pion_sel = [Selection('GEN', '', '((abs(pdgid) == {}) & (abs(firstmother_pdgid) == {}) & (reachedEE == 2))'.format(PID.pion, PID.pion,))]
# gen_pion_sel = [Selection('GEN', '', '((abs(pdgid) == {}) & (abs(firstmother_pdgid) == {}) )'.format(PID.pion, PID.pion))]




gen_ee_sel = [#Selection('all'),
              Selection('END', 'ECAll', 'reachedEE>=1 '),
              ###COMMENTFORTESTSelection('EC', 'EC', 'reachedEE == 2')
              ]


gen_part_fbrem_selection = [Selection('all', '', ''),
                            Selection('HBrem', 'f_{BREM} >= 0.5', 'fbrem >= 0.5'),
                            Selection('LBrem', 'f_{BREM} < 0.5', 'fbrem < 0.5'),
                            ]

genpart_ele_sel = add_selections(gen_ele_sel, gen_ee_sel)
genpart_ele_pt_sel = add_selections(genpart_ele_sel, gen_pt_sel)
genpart_ele_eta_sel = add_selections(genpart_ele_sel, gen_eta_sel)
genpart_ele_eta_brem_sel = add_selections(genpart_ele_eta_sel, gen_part_fbrem_selection)


# gen_part_selections = [Selection('GEN', '', '(abs(pdgid) == {})'.format(PID.e lectron))]


gen_part_ee_sel = add_selections(gen_selections, gen_ee_selections)
gen_part_ee_pt_sel = add_selections(gen_part_ee_sel, gen_pt_selections)
gen_part_ee_eta_sel = add_selections(gen_part_ee_sel, gen_eta_selections)
gen_part_ee_eta_brem_sel = add_selections(gen_part_ee_eta_sel, gen_part_fbrem_selection)

gen_part_selections_debug = []
gen_part_selections_debug = add_selections(gen_part_ee_sel, [Selection('EtaBCD', '1.52 < |#eta^{GEN}| <= 2.8', '1.52 < abs(eta) <= 2.8')])

#MYSTUFF

# += adds as a seperate selection 
# add_selection combines the selections in arguments into one or more

#gen_part_selections = gen_debug
gen_part_selections = gen_part_ee_sel#gen_selections
gen_part_selections += gen_part_ee_pt_sel
#gen_part_selections += gen_part_ee_eta_sel
#gen_part_selections += add_selections(gen_part_ee_eta_sel, gen_part_ee_pt_sel)

# gen_e_sel = gen_ele_sel
# gen_e_sel+= gen_pt_selections
# gen_e_sel+= gen_eta_selections
# gen_e_sel = add_selections(gen_ele_sel, gen_pt_selections)
# gen_e_sel = add_selections(gen_e_sel, gen_eta_selections)
# gen_e_sel = add_selections(gen_pt_selections, gen_eta_selections)
# gen_e_sel = add_selections(gen_e_sel, [Selection('all', '', '')])
# gen_e_sel = add_selections(gen_ele_sel, [Selection('EtaBCD', '1.52 < |#eta^{GEN}| <= 2.8', '1.52 < abs(eta) <= 2.8')])
# gen_e_sel_forBDT_sig = add_selections(gen_ele_sel, gen_pt_sel_forBDT_sig)


gen_e_sel = add_selections(gen_ele_sel, gen_pt_sel)
gen_e_sel = add_selections(gen_e_sel, gen_exeta_selections)


gen_e_sel_test = add_selections(gen_ele_sel, gen_pt_sel_test)
gen_e_sel_test = add_selections(gen_e_sel_test, gen_exeta_selections)



# gen_e_sel += gen_ele_sel


gen_g_sel = add_selections(gen_photon_sel, gen_pt_selections)
gen_g_sel = add_selections(gen_g_sel, gen_eta_selections)
gen_g_sel = add_selections(gen_pt_selections, gen_eta_selections)
# gen_e_sel = add_selections(gen_e_sel, [Selection('all', '', '')])
gen_g_sel += add_selections(gen_photon_sel, [Selection('EtaBCD', '1.52 < |#eta^{GEN}| <= 2.8', '1.52 < abs(eta) <= 2.8')])

gen_p_sel = add_selections(gen_pion_sel, gen_pt_selections)
gen_p_sel = add_selections(gen_p_sel, gen_eta_selections)
gen_p_sel = add_selections(gen_pt_selections, gen_eta_selections)
# gen_p_sel = add_selections(gen_p_sel, [Selection('all', '', '')])
gen_p_sel += add_selections(gen_pion_sel, [Selection('EtaBCD', '1.52 < |#eta^{GEN}| <= 2.8', '1.52 < abs(eta) <= 2.8')])


# END OF MYSTUFF


# gen_e_pt_sel= add_selections(gen_e_sel, gen_pt_selections)
# gen_e_pteta_sel = add_selections(gen_e_pt_sel, gen_eta_selections)

gen_MC_selections = MC_selections
gen_MC_selections += gen_pt_selections

gen_part_ele_selections = []
gen_part_ele_selections += genpart_ele_sel
gen_part_ele_selections += genpart_ele_pt_sel
# gen_part_selections += gen_part_ee_eta_sel
gen_part_ele_selections += add_selections(genpart_ele_eta_sel, gen_pt_selection15)


gen_part_barrel_selections = []
gen_part_barrel_selections += gen_selections
gen_part_barrel_selections += add_selections(gen_selections, gen_pt_selections)
gen_part_barrel_selections += add_selections(gen_selections, gen_eta_barrel_selections)

gen_part_be_selections = []
gen_part_be_selections += gen_selections

gen_part_be_selections += add_selections(gen_selections, gen_pt_selections)
gen_part_be_selections += add_selections(gen_selections, gen_eta_be_selections)


gen_part_be_reso_selections = []
gen_part_be_reso_selections += gen_selections
gen_part_be_reso_selections += add_selections(gen_selections, gen_eta_be_selections)

gen_part_selections_calib = []
gen_part_selections_calib += gen_part_ee_sel
gen_part_selections_calib += gen_part_ee_eta_sel
gen_part_selections_calib += add_selections([gen_part_ee_eta_sel[1]], gen_pt_selections)
# gen_part_selections_calib += gen_part_ee_eta_sel


gen_part_selections_tketa = [gen_sel for gen_sel in gen_part_selections if 'EtaD' not in gen_sel.name]
gen_part_ele_selections_tketa = [gen_sel for gen_sel in gen_part_ele_selections if 'EtaD' not in gen_sel.name]
# gen_part_selections_tketa += []
# print 'gen_part_selections: {}'.format(len(gen_part_selections))

genpart_ele_ee_selections = []
genpart_ele_ee_selections_tmp = add_selections(genpart_ele_selections, gen_ee_selections)
genpart_ele_ee_selections += genpart_ele_ee_selections_tmp
genpart_ele_ee_selections += add_selections(genpart_ele_ee_selections_tmp, gen_pt_selections)
genpart_ele_ee_selections += add_selections(genpart_ele_ee_selections_tmp, gen_eta_selections)

# print 'genpart_ele_ee_selections: {}'.format(len(genpart_ele_ee_selections))

genpart_photon_ee_selections = []
genpart_photon_ee_selections_tmp = add_selections(genpart_photon_selections, gen_ee_selections)
genpart_photon_ee_selections += genpart_photon_ee_selections_tmp
genpart_photon_ee_selections += add_selections(genpart_photon_ee_selections_tmp, gen_pt_selections)
genpart_photon_ee_selections += add_selections(genpart_photon_ee_selections_tmp, gen_eta_selections)

genpart_pion_ee_selections = []
genpart_pion_ee_selections_tmp = add_selections(genpart_pion_selections, gen_ee_selections)
genpart_pion_ee_selections += genpart_pion_ee_selections_tmp
genpart_pion_ee_selections += add_selections(genpart_pion_ee_selections_tmp, gen_pt_selections)
genpart_pion_ee_selections += add_selections(genpart_pion_ee_selections_tmp, gen_eta_selections)

# genpart_ele_

genpart_ele_genplotting = [Selection('all')]
genpart_ele_genplotting += add_selections(genpart_ele_selections, gen_ee_selections)

eg_qual_selections = [
                      # Selection('EGq1', 'q1', 'hwQual > 0'),
                      Selection('EGq2', 'hwQual 2', 'hwQual == 2'),
                      Selection('EGq3', 'hwQual 3', 'hwQual == 3'),
                      Selection('EGq4', 'hwQual 4', 'hwQual == 4'),
                      Selection('EGq5', 'hwQual 5', 'hwQual == 5')]

iso_selections = [Selection('all'),
                  Selection('Iso0p2', 'Iso0p2', 'tkIso <= 0.2'),
                  Selection('Iso0p1', 'Iso0p1', 'tkIso <= 0.1'),
                  Selection('Iso0p3', 'Iso0p3', 'tkIso <= 0.3'), ]


tkisoeg_selections = []
tkisoeg_selections += add_selections(eg_qual_selections, iso_selections)


eg_rate_selections = []
eg_rate_selections += add_selections(eg_qual_selections, tp_eta_selections)
eg_pt_selections = []
eg_pt_selections += add_selections(eg_qual_selections, tp_pt_selections_ext)

eg_pt_selections_barrel = []
eg_pt_selections_barrel += add_selections([Selection('all')], tp_pt_selections_ext)
# eg_pt_selections_barrel += barrel_quality_selections
# eg_pt_selections_barrel = prune(eg_pt_selections_barrel)

tkisoeg_rate_selections = []
tkisoeg_rate_selections += add_selections(tkisoeg_selections, tp_eta_selections)
tkisoeg_pt_selections = []
tkisoeg_pt_selections += add_selections(eg_qual_selections, tp_pt_selections_ext)
tkisoeg_pt_selections += tkisoeg_selections
tkisoeg_pt_selections = prune(tkisoeg_pt_selections)

# print 'tkisoeg_rate_selections:'
# print tkisoeg_rate_selections
tkisoeg_pt_selections_barrel = []
# tkisoeg_pt_selections_barrel += tp_pt_selections_ext
tkisoeg_pt_selections_barrel += add_selections(eg_pt_selections_barrel, barrel_quality_selections)

egqual_pt_selections_barrel = [sel for sel in tkisoeg_pt_selections_barrel if "Iso" not in sel.name]

tkeg_selection = [Selection('all'),
                  Selection('M1', '|#Delta#phi| <0.08 & #DeltaR < 0.07', '(abs(dphi) < 0.08) & (dr < 0.07)'),
                  Selection('M1P2', '|#Delta#phi| <0.08 & #DeltaR < 0.07 & p_{T}^{trk} > 2GeV', '(abs(dphi) < 0.08) & (dr < 0.07) & (tkpt > 2.)'),
                  Selection('M1P5', '|#Delta#phi| <0.08 & #DeltaR < 0.07 & p_{T}^{trk} > 5GeV', '(abs(dphi) < 0.08) & (dr < 0.07) & (tkpt > 5.)'),
                  Selection('M1P10', '|#Delta#phi| <0.08 & #DeltaR < 0.07 & p_{T}^{trk} > 10GeV', '(abs(dphi) < 0.08) & (dr < 0.07) & (tkpt > 10.)'),
                  # Selection('M1P2S', '|#Delta#phi| <0.08 & #DeltaR < 0.07 & p_{T}^{trk} > 2GeV', '(abs(dphi) < 0.08) & (dr < 0.07) & (tkpt > 2.) & (tknstubs > 3)'),
                  # Selection('M1P5S', '|#Delta#phi| <0.08 & #DeltaR < 0.07 & p_{T}^{trk} > 5GeV', '(abs(dphi) < 0.08) & (dr < 0.07) & (tkpt > 5.) & (tknstubs > 3)'),
                  # Selection('M1P10S', '|#Delta#phi| <0.08 & #DeltaR < 0.07 & p_{T}^{trk} > 10GeV', '(abs(dphi) < 0.08) & (dr < 0.07) & (tkpt > 10.) & (tknstubs > 3)'),
                  # Selection('M2', '|#Delta#phi| <0.08 & #DeltaR < 0.05', '(abs(dphi) < 0.08) & (dr < 0.05)'),
                  # Selection('M2P', '|#Delta#phi| <0.08 & #DeltaR < 0.05 & p_{T}^{trk} > 10GeV', '(abs(dphi) < 0.08) & (dr < 0.05) & (tkpt > 10.)'),
                  # Selection('M2S', '|#Delta#phi| <0.08 & #DeltaR < 0.05 & #stubs > 3', '(abs(dphi) < 0.08) & (dr < 0.05) & (tknstubs > 3)'),
                  ]

tkeg_rate_selections = []
tkeg_rate_selections += add_selections(eg_rate_selections, tkeg_selection)
tkeg_qual_selections = []
tkeg_qual_selections += add_selections(eg_qual_selections, tkeg_selection)
tkeg_pt_selections = []
tkeg_pt_selections += add_selections(tkeg_qual_selections, tp_pt_selections_ext)

# === L1 Track selections ===========================================

tracks_quality_sels = [Selection('all'),
                       Selection('St4', '# stubs > 3', 'nStubs > 3')]
tracks_pt_sels = [Selection('all'),
                  Selection('Pt2', 'p_{T}^{tk} > 2 GeV', 'pt > 2'),
                  Selection('Pt5', 'p_{T}^{tk} > 5 GeV', 'pt > 5'),
                  Selection('Pt10', 'p_{T}^{tk} > 10 GeV', 'pt > 10')]

tracks_selections = []
tracks_selections += add_selections(tracks_quality_sels, tracks_pt_sels)


if __name__ == "__main__":
    # for sel in gen_part_selections:
    #     print sel
    # for sel in eg_pt_selections:
    #     print sel.name
    # for sel in tkisoeg_pt_selections:
    #     print sel
    # for sel in gen_part_selections_tketa:
    #     print sel
    # for sel in gen_part_selections:
    #     print sel
    # for sel in eg_pt_selections_barrel:
    #     print sel
    # for sel in gen_part_barrel_selections:
    #     print sel
    # for sel in gen_part_be_selections:
    #     print sel
    # for sel in gen_part_selections_tketa:
    #     print sel
    # for sel in eg_pt_selections:
    #     print sel
    # for sel in tkisoeg_rate_selections:
    #     print sel
    # for sel in tkisoeg_pt_selections_barrel:
    #     print sel
    # for sel in egqual_pt_selections_barrel:
    #     print sel
    # for sel in eg_all_rate_selections:
    #     print sel
    # for sel in tp_rate_selections:
    #     print sel
    for sel in gen_part_ele_selections:
        print (sel)
