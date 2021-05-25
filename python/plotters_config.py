from __future__ import absolute_import
from . import plotters
from . import extraplotters
from . import collections
from . import selections
tp_plotters = [
               # TPPlotter(collections.tp_def, selections.tp_id_selections),
               # TPPlotter(collections.tp_truth, selections.tp_id_selections),
               # TPPlotter(selections.tp_def_uncalib, selections.tp_id_selections),
               # TPPlotter(selections.tp_def_calib, selections.tp_id_selections)
               # TPPlotter(selections.tp_hm, selections.tp_id_selections),
               plotters.TPPlotter(collections.tp_hm_vdr, selections.tp_id_selections),
               # TPPlotter(collections.tp_hm_fixed, selections.tp_id_selections),
               plotters.TPPlotter(collections.tp_hm_emint, selections.tp_id_selections),
               plotters.TPPlotter(collections.tp_hm_emint_merged, selections.tp_id_selections),
               # TPPlotter(collections.tp_hm_cylind10, selections.tp_id_selections),
               # TPPlotter(collections.tp_hm_cylind5, selections.tp_id_selections),
               # TPPlotter(collections.tp_hm_cylind2p5, selections.tp_id_selections),
               # TPPlotter(collections.tp_hm_vdr_rebin, selections.tp_id_selections),
               # TPPlotter(collections.tp_hm_vdr_stc, selections.tp_id_selections),
               # TPPlotter(selections.tp_def_nc, selections.tp_id_selections),
               # TPPlotter(selections.tp_hm_vdr_nc0, selections.tp_id_selections),
               # TPPlotter(selections.tp_hm_vdr_nc1, selections.tp_id_selections),
               # TPPlotter(selections.tp_hm_vdr_uncalib, selections.tp_id_selections),

               # TPPlotter(selections.tp_hm_vdr_merged, selections.tp_id_selections),
               ]

eg_plotters = [plotters.EGPlotter(collections.egs, selections.eg_qual_selections)]
track_plotters = [plotters.TrackPlotter(collections.tracks, selections.tracks_selections)]
tkeg_plotters = [plotters.TkEGPlotter(collections.tkegs, selections.tkeg_qual_selections)]
rate_plotters = [
                 # RatePlotter(collections.cl3d_def, selections.tp_rate_selections),
                 # RatePlotter(selections.tp_def_uncalib, selections.tp_rate_selections),
                 # RatePlotter(selections.tp_hm, selections.tp_rate_selections),
                 plotters.RatePlotter(collections.cl3d_hm, selections.tp_rate_selections),
                 # RatePlotter(collections.cl3d_hm_calib, selections.tp_rate_selections),
                 # RatePlotter(collections.cl3d_hm_cylind5_calib, selections.tp_rate_selections),
                 # RatePlotter(collections.cl3d_hm_cylind2p5_calib, selections.tp_rate_selections),
                 # RatePlotter(collections.cl3d_hm_shape_calib, selections.tp_rate_selections),
                 plotters.RatePlotter(collections.cl3d_hm_shapeDr, selections.tp_rate_selections),
                 plotters.RatePlotter(collections.cl3d_hm_shapeDr_calib, selections.tp_rate_selections),
                 plotters.RatePlotter(collections.cl3d_hm_emint, selections.tp_rate_selections),
                 # RatePlotter(collections.cl3d_hm_emint_merged, selections.tp_rate_selections),
                 # RatePlotter(collections.cl3d_hm_calib_merged, selections.tp_rate_selections),
                 # RatePlotter(collections.cl3d_hm_shape_calib_merged, selections.tp_rate_selections),
                 # RatePlotter(collections.cl3d_hm_rebin, selections.tp_rate_selections),
                 # RatePlotter(collections.cl3d_hm_stc, selections.tp_rate_selections),
                 # RatePlotter(selections.tp_def_nc, selections.tp_rate_selections),
                 # RatePlotter(selections.tp_hm_vdr_nc0, selections.tp_rate_selections),
                 # RatePlotter(selections.tp_hm_vdr_nc1, selections.tp_rate_selections),
                 # RatePlotter(selections.tp_hm_vdr_uncalib, selections.tp_rate_selections),
                 # RatePlotter(selections.tp_hm_vdr_merged, selections.tp_rate_selections),
                 # RatePlotter(selections.tp_def_calib, selections.tp_rate_selections),
                 # RatePlotter(selections.tp_def_merged, selections.tp_rate_selections)
                 ]

eg_rate_plotters = [plotters.RatePlotter(collections.egs, selections.eg_rate_selections),
                    plotters.RatePlotter(collections.egs_brl, selections.eg_barrel_rate_selections),
                    plotters.RatePlotter(collections.egs_all, selections.eg_all_rate_selections),
                    # RatePlotter(collections.tkegs, selections.tkeg_rate_selections),
                    # RatePlotter(collections.tkeles, selections.tkisoeg_rate_selections),
                    plotters.RatePlotter(collections.tkelesEL, selections.tkisoeg_rate_selections),
                    # RatePlotter(collections.tkeles_brl, selections.barrel_rate_selections),
                    plotters.RatePlotter(collections.tkelesEL_brl, selections.barrel_rate_selections),
                    # RatePlotter(collections.tkeles_all, selections.all_rate_selections),
                    plotters.RatePlotter(collections.tkelesEL_all, selections.all_rate_selections),
                    # RatePlotter(collections.tkisoeles, selections.tkisoeg_rate_selections),
                    ]

# tp_genmatched_debug = [plotters.TPGenMatchPlotterDebugger(collections.tp_def, collections.gen_parts, collections.gen,
#                                                  [selections.Selection('Em', 'EGId', 'quality >0')],
#                                                  selections.gen_part_selections_debug)]

tp_calib_plotters = [plotters.CalibrationPlotter(collections.tp_hm_vdr, collections.gen_parts,
                                                 selections.tp_calib_selections,
                                                 selections.gen_part_selections_calib),
                     # CalibrationPlotter(collections.tp_hm_calib, collections.gen_parts,
                     #                    selections.tp_calib_selections,
                     #                    selections.gen_part_selections_calib),
                     # CalibrationPlotter(collections.tp_hm_emint, collections.gen_parts,
                     #                    selections.tp_calib_selections,
                     #                    selections.gen_part_selections_calib),
                     # CalibrationPlotter(collections.tp_hm_emint_merged, collections.gen_parts,
                     #                    selections.tp_calib_selections,
                     #                    selections.gen_part_selections_calib),
                     # CalibrationPlotter(collections.tp_hm_shape, collections.gen_parts,
                     #                    selections.tp_calib_selections,
                     #                    selections.gen_part_selections_calib),
                     plotters.CalibrationPlotter(collections.tp_hm_shapeDr, collections.gen_parts,
                                        selections.tp_calib_selections,
                                        selections.gen_part_selections_calib),
                     plotters.CalibrationPlotter(collections.tp_hm_shapeDtDu, collections.gen_parts,
                                        selections.tp_calib_selections,
                                        selections.gen_part_selections_calib),
                     # CalibrationPlotter(collections.tp_hm_cylind10, collections.gen_parts,
                     #                    selections.tp_calib_selections,
                     #                    selections.gen_part_selections_calib),
                     # CalibrationPlotter(collections.tp_hm_cylind5, collections.gen_parts,
                     #                    selections.tp_calib_selections,
                     #                    selections.gen_part_selections_calib),
                     # CalibrationPlotter(collections.tp_hm_cylind2p5, collections.gen_parts,
                     #                    selections.tp_calib_selections,
                     #                    selections.gen_part_selections_calib),
                     # CalibrationPlotter(collections.tp_hm_shape_calib, collections.gen_parts,
                     #                    selections.tp_calib_selections,
                     #                    selections.gen_part_selections_calib),
                     # CalibrationPlotter(collections.tp_hm_shapeDr_calib, collections.gen_parts,
                     #                    selections.tp_calib_selections,
                     #                    selections.gen_part_selections_calib),
                     # CalibrationPlotter(collections.tp_hm_cylind10_calib, collections.gen_parts,
                     #                    selections.tp_calib_selections,
                     #                    selections.gen_part_selections_calib),
                     # CalibrationPlotter(collections.tp_hm_cylind5_calib, collections.gen_parts,
                     #                    selections.tp_calib_selections,
                     #                    selections.gen_part_selections_calib),
                     # CalibrationPlotter(collections.tp_hm_cylind2p5_calib, collections.gen_parts,
                     #                    selections.tp_calib_selections,
                     #                    selections.gen_part_selections_calib),
                     # CalibrationPlotter(collections.tp_hm_shape_calib1, collections.gen_parts,
                     #                    selections.tp_calib_selections,
                     #                    selections.gen_part_selections_calib),
                     # CalibrationPlotter(collections.tp_hm_cylind10_calib1, collections.gen_parts,
                     #                    selections.tp_calib_selections,
                     #                    selections.gen_part_selections_calib),
                     # CalibrationPlotter(collections.tp_hm_cylind5_calib1, collections.gen_parts,
                     #                    selections.tp_calib_selections,
                     #                    selections.gen_part_selections_calib),
                     # CalibrationPlotter(collections.tp_hm_cylind2p5_calib1, collections.gen_parts,
                     #                    selections.tp_calib_selections,
                     #                    selections.gen_part_selections_calib),
]

tp_genmatched_plotters = [
                          # TPGenMatchPlotter(collections.tp_def, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(collections.tp_truth, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(selections.tp_def_uncalib, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(selections.tp_def_calib, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(selections.tp_def_merged, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(selections.tp_hm, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          plotters.TPGenMatchPlotter(collections.tp_hm_vdr, collections.gen_parts,
                                            selections.tp_match_selections,
                                            selections.gen_part_selections),
                          # TPGenMatchPlotter(collections.tp_hm_fixed, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # # TPGenMatchPlotter(collections.tp_hm_cylind10, collections.gen_parts,
                          # #                   selections.tp_match_selections,
                          # #                   selections.gen_part_selections),
                          # # TPGenMatchPlotter(collections.tp_hm_cylind5, collections.gen_parts,
                          # #                   selections.tp_match_selections,
                          # #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(collections.tp_hm_cylind2p5, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          plotters.TPGenMatchPlotter(collections.tp_hm_calib, collections.gen_parts,
                                            selections.tp_match_selections,
                                            selections.gen_part_selections),
                          # TPGenMatchPlotter(collections.tp_hm_cylind10_calib, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(collections.tp_hm_cylind5_calib, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(collections.tp_hm_cylind2p5_calib, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(collections.tp_hm_shape_calib, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          plotters.TPGenMatchPlotter(collections.tp_hm_shapeDr_calib, collections.gen_parts,
                                            selections.tp_match_selections,
                                            selections.gen_part_selections),
                          plotters.TPGenMatchPlotter(collections.tp_hm_emint, collections.gen_parts,
                                            selections.tp_match_selections,
                                            selections.gen_part_selections),
                          # TPGenMatchPlotter(collections.tp_hm_calib_merged, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(collections.tp_hm_shape_calib_merged, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(collections.tp_hm_cylind2p5_calib_merged, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(collections.tp_hm_shape_calib_merged, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(collections.tp_hm_vdr_rebin, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(collections.tp_hm_vdr_stc, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(selections.tp_def_nc, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(selections.tp_hm_vdr_nc0, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(selections.tp_hm_vdr_nc1, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(selections.tp_hm_vdr_uncalib, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # TPGenMatchPlotter(selections.tp_hm_vdr_merged, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          ]

eg_genmatched_plotters = [plotters.EGGenMatchPlotter(collections.egs, collections.gen_parts,
                                            selections.eg_pt_selections,
                                            selections.gen_part_selections),
                          plotters.EGGenMatchPlotter(collections.egs_brl, collections.gen_parts,
                                            selections.egqual_pt_selections_barrel,
                                            selections.gen_part_barrel_selections),
                          plotters.EGGenMatchPlotter(collections.egs_all, collections.gen_parts,
                                            selections.egqual_pt_selections_barrel,
                                            selections.gen_part_be_selections),
                          # TkEGGenMatchPlotter(collections.tkegs, collections.gen_parts,
                          #                     selections.tkeg_pt_selections,
                          #                     selections.gen_part_selections),
                          # TkEGGenMatchPlotter(collections.tkegs_emu, collections.gen_parts,
                          #                     selections.tkeg_pt_selections,
                          #                     selections.gen_part_selections),
                          plotters.EGGenMatchPlotter(collections.tkeles, collections.gen_parts,
                                            selections.tkisoeg_pt_selections,
                                            selections.gen_part_selections_tketa),
                          plotters.EGGenMatchPlotter(collections.tkelesEL, collections.gen_parts,
                                            selections.tkisoeg_pt_selections,
                                            selections.gen_part_selections_tketa),
                          # EGGenMatchPlotter(collections.tkeles_brl, collections.gen_parts,
                          #                   selections.eg_pt_selections_barrel,
                          #                   selections.gen_part_barrel_selections),
                          plotters.EGGenMatchPlotter(collections.tkelesEL_brl, collections.gen_parts,
                                            selections.eg_pt_selections_barrel,
                                            selections.gen_part_barrel_selections),
                          # EGGenMatchPlotter(collections.tkeles_all, collections.gen_parts,
                          #                   selections.tkisoeg_pt_selections_barrel,
                          #                   selections.gen_part_be_selections),
                          plotters.EGGenMatchPlotter(collections.tkelesEL_all, collections.gen_parts,
                                            selections.tkisoeg_pt_selections_barrel,
                                            selections.gen_part_be_selections),
                          # TPGenMatchPlotter(collections.tp_hm_emint_merged, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # EGGenMatchPlotter(collections.tkisoeles, collections.gen_parts,
                          #                   selections.tkisoeg_pt_selections,
                          #                   selections.gen_part_selections),
                                            ]


ele_genmatched_plotters = [plotters.EGGenMatchPlotter(collections.egs, collections.gen_parts,
                                                      selections.eg_pt_selections,
                                                      selections.gen_part_ele_selections),
                          plotters.EGGenMatchPlotter(collections.egs_brl, collections.gen_parts,
                                            selections.egqual_pt_selections_barrel,
                                            selections.gen_part_barrel_selections),
                          plotters.EGGenMatchPlotter(collections.egs_all, collections.gen_parts,
                                            selections.egqual_pt_selections_barrel,
                                            selections.gen_part_be_selections),
                          # TkEGGenMatchPlotter(collections.tkegs, collections.gen_parts,
                          #                     selections.tkeg_pt_selections,
                          #                     selections.gen_part_selections),
                          # TkEGGenMatchPlotter(collections.tkegs_emu, collections.gen_parts,
                          #                     selections.tkeg_pt_selections,
                          #                     selections.gen_part_selections),
                          plotters.EGGenMatchPlotter(collections.tkelesEL, collections.gen_parts,
                                            selections.tkisoeg_pt_selections,
                                            selections.gen_part_ele_selections_tketa),
                          # EGGenMatchPlotter(collections.tkeles_brl, collections.gen_parts,
                          #                   selections.eg_pt_selections_barrel,
                          #                   selections.gen_part_barrel_selections),
                          plotters.EGGenMatchPlotter(collections.tkelesEL_brl, collections.gen_parts,
                                            selections.eg_pt_selections_barrel,
                                            selections.gen_part_barrel_selections),
                          # EGGenMatchPlotter(collections.tkeles_all, collections.gen_parts,
                          #                   selections.tkisoeg_pt_selections_barrel,
                          #                   selections.gen_part_be_selections),
                          plotters.EGGenMatchPlotter(collections.tkelesEL_all, collections.gen_parts,
                                            selections.tkisoeg_pt_selections_barrel,
                                            selections.gen_part_be_selections),
                          # TPGenMatchPlotter(collections.tp_hm_emint_merged, collections.gen_parts,
                          #                   selections.tp_match_selections,
                          #                   selections.gen_part_selections),
                          # EGGenMatchPlotter(collections.tkisoeles, collections.gen_parts,
                          #                   selections.tkisoeg_pt_selections,
                          #                   selections.gen_part_selections),
                                            ]


eg_resotuples_plotters = [plotters.ResoNtupleMatchPlotter(collections.egs, collections.gen_parts,
                                                          selections.eg_qual_selections,
                                                          selections.gen_part_selections),
                          plotters.ResoNtupleMatchPlotter(collections.egs_brl, collections.gen_parts,
                                                          selections.barrel_quality_selections,
                                                          selections.gen_part_barrel_selections),
                          plotters.ResoNtupleMatchPlotter(collections.tkelesEL, collections.gen_parts,
                                                          selections.tkisoeg_selections,
                                                          selections.gen_part_selections_tketa),
                          plotters.ResoNtupleMatchPlotter(collections.tkelesEL_brl, collections.gen_parts,
                                                          selections.barrel_quality_selections,
                                                          selections.gen_part_barrel_selections),
                                            ]


track_genmatched_plotters = [plotters.TrackGenMatchPlotter(collections.tracks, collections.gen_parts,
                                                  selections.tracks_selections,
                                                  selections.gen_part_selections),
                             plotters.TrackGenMatchPlotter(collections.tracks_emu, collections.gen_parts,
                                                  selections.tracks_selections,
                                                  selections.gen_part_selections)]

genpart_plotters = [plotters.GenPlotter(collections.gen_parts, selections.genpart_ele_genplotting)]

ttower_plotters = [plotters.TTPlotter(collections.towers_tcs),
                   plotters.TTPlotter(collections.towers_sim),
                   plotters.TTPlotter(collections.towers_hgcroc),
                   plotters.TTPlotter(collections.towers_wafer)
                   ]

ttower_genmatched_plotters = [plotters.TTGenMatchPlotter(collections.towers_tcs, collections.gen_parts,
                              [selections.Selection('all')], selections.gen_part_selections),
                              plotters.TTGenMatchPlotter(collections.towers_sim, collections.gen_parts,
                              [selections.Selection('all')], selections.gen_part_selections),
                              plotters.TTGenMatchPlotter(collections.towers_hgcroc, collections.gen_parts,
                              [selections.Selection('all')], selections.gen_part_selections),
                              plotters.TTGenMatchPlotter(collections.towers_wafer, collections.gen_parts,
                              [selections.Selection('all')], selections.gen_part_selections)
                              ]

correlator_occupancy_plotters = [plotters.CorrOccupancyPlotter(collections.tracks, selections.tracks_selections),
                                 plotters.CorrOccupancyPlotter(collections.tracks_emu, selections.tracks_selections),
                                 plotters.CorrOccupancyPlotter(collections.egs_all, selections.tp_pt_selections_occ),
                                 ]

tp_cluster_tc_match_plotters = [plotters.ClusterTCGenMatchPlotter(collections.tp_hm_vdr,
                                                                  collections.gen_parts,
                                                                  data_selections=selections.tp_tccluster_match_selections,
                                                                  gen_selections=selections.gen_part_ee_eta_brem_sel)]


# ========================================== STAND ALONE ================================

# rate plotter to use for minbias sample
mySArate_plotter = [plotters.RatePlotter(   collections.cl3d_hm, 
                                            selections.tp_selections_rateeff)
]

# efficiency plotter to use for singleelectron sample 
mySAeffi_plotter = [extraplotters.Cluster3DGenMatchHybrid(
                                            collections.cl3d_hm, 
                                            collections.gen_parts,
                                            selections.tp_selections_rateeff,                      #<- defines collection to be matched
                                            [selections.Selection('', '', '')], #<- defines ID to apply after matching
                                            selections.gen_e_sel,
                                            saveEffPlots=True, saveNtuples=False)
]

# ntuplizer to use for minbias sample
SA_BDT_bkg_ntuplizer = [extraplotters.Cluster3DHybrid(
                                            collections.cl3d_hm, 
                                            selections.tp_eta_sel_noID,
                                            saveEffPlots=False, saveNtuples=True)
]

# ntuplizer to use for singleelectron sample
SA_BDT_sig_ntuplizer = [extraplotters.Cluster3DGenMatchHybrid(
                                            collections.cl3d_hm, 
                                            collections.gen_parts,
                                            selections.tp_eta_sel_noID,
                                            [selections.Selection('', '', '')],
                                            selections.gen_e_sel,
                                            saveEffPlots=False, saveNtuples=True)
]

# ========================================== STAND ALONE + TRACKS ================================

# rate plotter to use for minbias sample
mySATKrate_plotter = [plotters.RatePlotter( collections.composite_tk3dcl, 
                                            selections.tp_IDcl3dtrk)
]

# efficiency plotter to use for singleelectron sample 
mySATKeffi_plotter = [extraplotters.Cluster3DGenMatchHybrid(
                                            collections.composite_tk3dcl, 
                                            collections.gen_parts,
                                            selections.tp_IDcl3dtrk,                      #<- defines collection to be matched
                                            [selections.Selection('', '', '')], #<- defines ID to apply after matching
                                            selections.gen_e_sel_trk,
                                            saveEffPlots=True, saveNtuples=False)
]

# rate plotter to use for minbias sample
L1TDR_SATKrate_plotter = [plotters.RatePlotter( collections.composite_tk3dclellips, 
                                            selections.tp_IDcl3dtrkEllips)
]

# efficiency plotter to use for singleelectron sample 
L1TDR_SATKeffi_plotter = [extraplotters.Cluster3DGenMatchHybrid(
                                            collections.composite_tk3dclellips, 
                                            collections.gen_parts,
                                            selections.tp_IDcl3dtrkEllips,                      #<- defines collection to be matched
                                            [selections.Selection('', '', '')], #<- defines ID to apply after matching
                                            selections.gen_e_sel_trk,
                                            saveEffPlots=True, saveNtuples=False)
]

# ntuplizer to use for minbias sample
SATK_BDT_bkg_ntuplizer = [extraplotters.Cluster3DHybrid(
                                            collections.composite_tk3dcl, 
                                            selections.tk_acceptance,
                                            saveEffPlots=False, saveNtuples=True)
]

# ntuplizer to use for singleelectron sample
SATK_BDT_sig_ntuplizer = [extraplotters.Cluster3DGenMatchHybrid(
                                            collections.composite_tk3dcl, 
                                            collections.gen_parts,
                                            selections.tk_acceptance,
                                            [selections.Selection('', '', '')],
                                            selections.gen_e_sel_trk,
                                            saveEffPlots=False, saveNtuples=True)
]

# ========================================== CUSTOM MATCHING STUDIES ================================


# object matching plotter
mymatch_plotter = [extraplotters.CustomHistPlotter(
                                            collections.cl3d_hm, 
                                            collections.l1Trks ,
                                            collections.gen_parts,
                                            selections.tp_eta_sel_noID,
                                            selections.gen_e_sel)
]


# ntuplizer to use for singleelectron sample
# myBDT_sig_test = [extraplotters.Cluster3DGenMatchHybrid(
#                                             collections.cl3d_hm, 
#                                             collections.l1Trks ,
#                                             collections.gen_parts,
#                                             selections.tp_eta_selections,
#                                             selections.gen_e_sel_test,
#                                             includeTracks=False, saveEffPlots=False, saveNtuples=True)
# ]