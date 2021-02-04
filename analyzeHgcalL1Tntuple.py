#!/usr/bin/env python

"""
Main script for L1 TP analysis.

The script reads the configuration, opens the input and output files for the given sample,
runs the event loop and saves histograms to disk.
All the analysis logic is anyhow elsewhere:

Data:
    which data are potentially read is handled in the `collections` module.
    How to select the data is handled in the `selections` module.
Plotters:
    what to do with the data is handled in the `plotters` module
Histograms:
    which histograms are produced is handled in the `l1THistos` module (and the plotters).
"""

# import ROOT
# from __future__ import print_function
import sys
# The purpose of this file is to demonstrate mainly the objects
# that are in the HGCalNtuple
import ROOT
import os
import socket
import datetime
import optparse
import yaml
import traceback
import subprocess32
from shutil import copyfile

import root_numpy as rnp
import pandas as pd
import numpy as np

from NtupleDataFormat import HGCalNtuple
import python.l1THistos as histos
# import python.clusterTools as clAlgo
import python.file_manager as fm
import python.collections as collections
from python.utils import debugPrintOut

# from pandas.core.common import SettingWithCopyError, SettingWithCopyWarning
# import warnings
# warnings.filterwarnings('error', category=SettingWithCopyWarning)

class Parameters(dict):

    def __getattr__(self, name):
        return self[name]

    def __str__(self):
        return 'Name: {},\n \
                clusterize: {}\n \
                compute density: {}\n \
                maxEvents: {}\n \
                output file: {}\n \
                events per job: {}\n \
                debug: {}'.format(self.name,
                                  self.clusterize,
                                  self.computeDensity,
                                  self.maxEvents,
                                  self.output_filename,
                                  self.events_per_job,
                                  self.debug)

    def __repr__(self):
        return self.name


def get_collection_parameters(opt, cfgfile):
    outdir = cfgfile['common']['output_dir']['default']
    hostname = socket.gethostname()
    for machine, odir in cfgfile['common']['output_dir'].items():
        if machine in hostname:
            outdir = odir
    plot_version = cfgfile['common']['plot_version']

    collection_params = {}
    for collection, collection_data in cfgfile['collections'].items():
        samples = collection_data['samples']
        print ('--- Collection: {} with samples: {}'.format(collection, samples))
        print collection_data['priorities']
        sample_params = []

        plotters = []
        for plotter in collection_data['plotters']:
            plotters.extend(cfgfile['plotters'][plotter])

        for sample in samples:
            events_per_job = -1
            output_filename_base = 'histos_{}_{}_{}'.format(sample, collection_data['file_label'], plot_version)
            out_file_name = '{}i.root'.format(output_filename_base)
            if opt.BATCH:
                events_per_job = cfgfile['samples'][sample]['events_per_job']
                if opt.RUN:
                    out_file_name = '{}_{}.root'.format(output_filename_base, opt.RUN)

            if opt.OUTDIR:
                outdir = opt.OUTDIR

            out_file = os.path.join(outdir, out_file_name)

            weight_file = None
            if 'weights' in collection_data.keys():
                if sample in collection_data['weights'].keys():
                    weight_file = collection_data['weights'][sample]

            params = Parameters({'input_base_dir': cfgfile['common']['input_dir'],
                                 'input_sample_dir': cfgfile['samples'][sample]['input_sample_dir'],
                                 'output_filename_base': output_filename_base,
                                 'output_filename': out_file,
                                 'output_dir': outdir,
                                 'clusterize': cfgfile['common']['run_clustering'],
                                 'eventsToDump': [],
                                 'version': plot_version,
                                 'maxEvents': int(opt.NEVENTS),
                                 'events_per_job': events_per_job,
                                 'computeDensity': cfgfile['common']['run_density_computation'],
                                 'plotters': plotters,
                                 'htc_jobflavor': collection_data['htc_jobflavor'],
                                 'htc_priority': collection_data['priorities'][sample],
                                 'weight_file': weight_file,
                                 'debug': opt.DEBUG,
                                 'name': sample})
            sample_params.append(params)
        collection_params[collection] = sample_params
    return collection_params


def convertGeomTreeToDF(tree):
    branches = [br.GetName() for br in tree.GetListOfBranches()
                if not br.GetName().startswith('c_')]
    cell_array = rnp.tree2array(tree, branches=branches)
    cell_df = pd.DataFrame()
    for idx in range(0, len(branches)):
        cell_df[branches[idx]] = cell_array[branches[idx]]
    return cell_df


def dumpFrame2JSON(filename, frame):
    with open(filename, 'w') as f:
        f.write(frame.to_json())


# @profile
def analyze(params, batch_idx=0):
    print (params)
    debug = int(params.debug)

    tc_geom_df = pd.DataFrame()
    tc_rod_bins = pd.DataFrame()
    if False:
        # read the geometry dump
        geom_file = os.path.join(params.input_base_dir, 'geom/test_triggergeom.root')
        tc_geom_tree = HGCalNtuple([geom_file], tree='hgcaltriggergeomtester/TreeTriggerCells')
        tc_geom_tree.setCache(learn_events=100)
        print ('read TC GEOM tree with # events: {}'.format(tc_geom_tree.nevents()))
        tc_geom_df = convertGeomTreeToDF(tc_geom_tree._tree)
        tc_geom_df['radius'] = np.sqrt(tc_geom_df['x']**2+tc_geom_df['y']**2)
        tc_geom_df['eta'] = np.arcsinh(tc_geom_df.z/tc_geom_df.radius)

        if False:
            tc_rod_bins = pd.read_csv(filepath_or_buffer='data/TCmapping_v2.txt',
                                      sep=' ',
                                      names=['id', 'rod_x', 'rod_y'],
                                      index_col=False)
            tc_rod_bins['rod_bin'] = tc_rod_bins.apply(
                func=lambda cell: (int(cell.rod_x), int(cell.rod_y)), axis=1)

            tc_geom_df = pd.merge(tc_geom_df, tc_rod_bins, on='id')

        if debug == -4:
            tc_geom_tree.PrintCacheStats()
        print ('...done')

    tree_name = 'l1CaloTriggerNtuplizer_egOnly/HGCalTriggerNtuple'
    # tree_name = 'l1CaloTriggerNtuplizer/HGCalTriggerNtuple'
    input_files = []
    range_ev = (0, params.maxEvents)

    if params.events_per_job == -1:
        print 'This is interactive processing...'
        input_files = fm.get_files_for_processing(input_dir=os.path.join(params.input_base_dir,
                                                                         params.input_sample_dir),
                                                  tree=tree_name,
                                                  nev_toprocess=params.maxEvents,
                                                  debug=debug)
    else:
        print 'This is batch processing...'
        input_files, range_ev = fm.get_files_and_events_for_batchprocessing(input_dir=os.path.join(params.input_base_dir,
                                                                                                   params.input_sample_dir),
                                                                            tree=tree_name,
                                                                            nev_toprocess=params.maxEvents,
                                                                            nev_perjob=params.events_per_job,
                                                                            batch_id=batch_idx,
                                                                            debug=debug)

    # print ('- dir {} contains {} files.'.format(params.input_sample_dir, len(input_files)))
    print '- will read {} files from dir {}:'.format(len(input_files), params.input_sample_dir)
    for file_name in input_files:
        print '        - {}'.format(file_name)

    ntuple = HGCalNtuple(input_files, tree=tree_name)
    if params.events_per_job == -1:
        if params.maxEvents == -1:
            range_ev = (0, ntuple.nevents())

    print ('- created TChain containing {} events'.format(ntuple.nevents()))
    print ('- reading from event: {} to event {}'.format(range_ev[0], range_ev[1]))

    ntuple.setCache(learn_events=1, entry_range=range_ev)
    output = ROOT.TFile(params.output_filename, "RECREATE")
    output.cd()

    if False:
        hTCGeom = histos.GeomHistos('hTCGeom')
        hTCGeom.fill(tc_geom_df[(np.abs(tc_geom_df.eta) > 1.65) & (np.abs(tc_geom_df.eta) < 2.85)])

    # instantiate all the plotters
    plotter_collection = []
    plotter_collection.extend(params.plotters)
    print plotter_collection

    # -------------------------------------------------------
    # book histos
    for plotter in plotter_collection:
        plotter.book_histos()

    # -------------------------------------------------------
    # event loop
    ev_manager = collections.EventManager()

    if params.weight_file is not None:
        ev_manager.read_weight_file(params.weight_file)

    nev = 0
    for evt_idx in range(range_ev[0], range_ev[1]+1):
        # print(evt_idx)
        event = ntuple.getEvent(evt_idx)
        if (params.maxEvents != -1 and nev >= params.maxEvents):
            break
        if debug >= 2 or event.entry() % 100 == 0:
            print ("--- Event {}, @ {}".format(event.entry(),
                                               datetime.datetime.now()))
            print ('    run: {}, lumi: {}, event: {}'.format(
                event.run(), event.lumi(), event.event()))

        nev += 1

        try:
            ev_manager.read(event, debug)

            puInfo = event.getPUInfo()
            debugPrintOut(debug, 'PU', toCount=puInfo, toPrint=puInfo)

            for plotter in plotter_collection:
                #print plotter
                plotter.fill_histos(debug=debug)

        except Exception as inst:
            print ("[EXCEPTION OCCURRED:] --- Event {}, @ {}".format(event.entry(),
                                                                     datetime.datetime.now()))
            print ('                       run: {}, lumi: {}, event: {}'.format(event.run(),
                                                                                event.lumi(),
                                                                                event.event()))
            print (str(inst))
            print ("Unexpected error:", sys.exc_info()[0])
            traceback.print_exc()
            sys.exit(200)


    print ("Processed {} events/{} TOT events".format(nev, ntuple.nevents()))
    print ("Writing histos to file {}".format(params.output_filename))

    lastfile = ntuple.tree().GetFile()
    print 'Read bytes: {}, # of transaction: {}'.format(
        lastfile.GetBytesRead(),  lastfile.GetReadCalls())
    if debug == -4:
        ntuple.PrintCacheStats()

    output.cd()
    hm = histos.HistoManager()
    hm.writeHistos()

    output.Close()

    return


def editTemplate(infile, outfile, params):
    template_file = open(infile)
    template = template_file.read()
    template_file.close()

    for param in params.keys():
        template = template.replace(param, params[param])

    out_file = open(outfile, 'w')
    out_file.write(template)
    out_file.close()


def main(analyze):
    # ============================================
    # configuration bit

    usage = ('usage: %prog [options]\n'
             + '%prog -h for help')
    parser = optparse.OptionParser(usage)
    parser.add_option('-f', '--file', dest='CONFIGFILE', help='specify the ini configuration file')
    parser.add_option('-c', '--collection', dest='COLLECTION',
                      help='specify the collection to be processed')
    parser.add_option('-s', '--sample', dest='SAMPLE',
                      help='specify the sample (within the collection) to be processed ("all" to run the full collection)')
    parser.add_option('-d', '--debug', dest='DEBUG', help='debug level (default is 0)', default=0)
    parser.add_option('-n', '--nevents', dest='NEVENTS',
                      help='# of events to process per sample (default is 10)', default=10)
    parser.add_option("-b", "--batch", action="store_true", dest="BATCH",
                      default=False, help="submit the jobs via CONDOR")
    parser.add_option("-r", "--run", dest="RUN", default=None,
                      help="the batch_id to run (need to be used with the option -b)")
    parser.add_option("-o", "--outdir", dest="OUTDIR", default=None,
                      help="override the output directory for the files")
    # parser.add_option("-i", "--inputJson", dest="INPUT", default='input.json', help="list of input files and properties in JSON format")

    global opt, args
    (opt, args) = parser.parse_args()

    # read the config file
    cfgfile = None
    with open(opt.CONFIGFILE, 'r') as stream:
        cfgfile = yaml.load(stream)

    collection_params = get_collection_parameters(opt, cfgfile)

    samples_to_process = list()
    if opt.COLLECTION:
        if opt.COLLECTION in collection_params.keys():
            if opt.SAMPLE:
                if opt.SAMPLE == 'all':
                    samples_to_process.extend(collection_params[opt.COLLECTION])
                else:
                    sel_sample = [sample for sample in collection_params[opt.COLLECTION]
                                  if sample.name == opt.SAMPLE]
                    samples_to_process.append(sel_sample[0])
            else:
                print ('Collection: {}, available samples: {}'.format(
                    opt.COLLECTION, collection_params[opt.COLLECTION]))
                sys.exit(0)
        else:
            print ('ERROR: collection {} not in the cfg file'.format(opt.COLLECTION))
            sys.exit(10)
    else:
        print ('\nAvailable collections: {}'.format(collection_params.keys()))
        sys.exit(0)

    print ('About to process samples: {}'.format(samples_to_process))

    if opt.BATCH and not opt.RUN:
        batch_dir = 'batch_{}_{}'.format(opt.COLLECTION, cfgfile['common']['plot_version'])
        if not os.path.exists(batch_dir):
            os.mkdir(batch_dir)
            os.mkdir(batch_dir+'/conf/')
            os.mkdir(batch_dir+'/logs/')

        dagman_sub = ''
        dagman_dep = ''
        dagman_ret = ''
        for sample in samples_to_process:
            dagman_spl = ''
            dagman_spl_retry = ''
            sample_batch_dir = os.path.join(batch_dir, sample.name)
            sample_batch_dir_logs = os.path.join(sample_batch_dir, 'logs')
            os.mkdir(sample_batch_dir)
            os.mkdir(sample_batch_dir_logs)
            print(sample)
            nevents = int(opt.NEVENTS)
            n_jobs = fm.get_number_of_jobs_for_batchprocessing(input_dir=os.path.join(sample.input_base_dir, sample.input_sample_dir),
                                                               tree='hgcalTriggerNtuplizer/HGCalTriggerNtuple',
                                                               nev_toprocess=nevents,
                                                               nev_perjob=sample.events_per_job,
                                                               debug=int(opt.DEBUG))
            print ('Total # of events to be processed: {}'.format(nevents))
            print ('# of events per job: {}'.format(sample.events_per_job))
            if n_jobs == 0:
                n_jobs = 1
            print ('# of jobs to be submitted: {}'.format(n_jobs))

            params = {}
            params['TEMPL_TASKDIR'] = sample_batch_dir
            params['TEMPL_NJOBS'] = str(n_jobs)
            params['TEMPL_WORKDIR'] = os.environ["PWD"]
            params['TEMPL_CFG'] = opt.CONFIGFILE
            params['TEMPL_COLL'] = opt.COLLECTION
            params['TEMPL_SAMPLE'] = sample.name
            params['TEMPL_OUTFILE'] = '{}.root'.format(sample.output_filename_base)
            params['TEMPL_EOSPROTOCOL'] = fm.get_eos_protocol(dirname=sample.output_dir)
            params['TEMPL_INFILE'] = '{}_*.root'.format(sample.output_filename_base)
            params['TEMPL_FILEBASE'] = sample.output_filename_base
            params['TEMPL_OUTDIR'] = sample.output_dir
            params['TEMPL_VIRTUALENV'] = os.path.basename(os.environ['VIRTUAL_ENV'])
            params['TEMPL_VERSION'] = sample.version
            params['TEMPL_JOBFLAVOR'] = sample.htc_jobflavor

            editTemplate(infile='templates/batch.sub',
                         outfile=os.path.join(sample_batch_dir, 'batch.sub'),
                         params=params)

            editTemplate(infile='templates/run_batch.sh',
                         outfile=os.path.join(sample_batch_dir, 'run_batch.sh'),
                         params=params)

            editTemplate(infile='templates/copy_files.sh',
                         outfile=os.path.join(sample_batch_dir, 'copy_files.sh'),
                         params=params)
            os.chmod(os.path.join(sample_batch_dir, 'copy_files.sh'),  0754)

            editTemplate(infile='templates/batch_hadd.sub',
                         outfile=os.path.join(sample_batch_dir, 'batch_hadd.sub'),
                         params=params)

            editTemplate(infile='templates/run_batch_hadd.sh',
                         outfile=os.path.join(sample_batch_dir, 'run_batch_hadd.sh'),
                         params=params)

            editTemplate(infile='templates/batch_cleanup.sub',
                         outfile=os.path.join(sample_batch_dir, 'batch_cleanup.sub'),
                         params=params)

            editTemplate(infile='templates/run_batch_cleanup.sh',
                         outfile=os.path.join(sample_batch_dir, 'run_batch_cleanup.sh'),
                         params=params)

            editTemplate(infile='templates/hadd_dagman.dag',
                         outfile=os.path.join(batch_dir, 'hadd_{}.dag'.format(sample.name)),
                         params=params)

            editTemplate(infile='templates/run_harvest.sh',
                         outfile=os.path.join(sample_batch_dir, 'run_harvest.sh'),
                         params=params)

            editTemplate(infile='templates/batch_harvest.sub',
                         outfile=os.path.join(sample_batch_dir, 'batch_harvest.sub'),
                         params=params)

            for jid in range(0, n_jobs):
                dagman_spl += 'JOB Job_{} batch.sub\n'.format(jid)
                dagman_spl += 'VARS Job_{} JOB_ID="{}"\n'.format(jid, jid)
                dagman_spl_retry += 'Retry Job_{} 3\n'.format(jid)
                dagman_spl_retry += 'PRIORITY Job_{} {}\n'.format(jid, sample.htc_priority)


            dagman_sub += 'SPLICE {} {}.spl DIR {}\n'.format(
                sample.name, sample.name, sample_batch_dir)
            dagman_sub += 'JOB {} {}/batch_hadd.sub\n'.format(sample.name+'_hadd', sample_batch_dir)
            dagman_sub += 'JOB {} {}/batch_cleanup.sub\n'.format(
                sample.name+'_cleanup', sample_batch_dir)

            dagman_dep += 'PARENT {} CHILD {}\n'.format(sample.name, sample.name+'_hadd')
            dagman_dep += 'PARENT {} CHILD {}\n'.format(sample.name+'_hadd', sample.name+'_cleanup')

            # dagman_ret += 'Retry {} 3\n'.format(sample.name)
            dagman_ret += 'Retry {} 3\n'.format(sample.name+'_hadd')
            dagman_ret += 'PRIORITY {} {}\n'.format(sample.name+'_hadd', sample.htc_priority)

            dagman_splice = open(os.path.join(sample_batch_dir, '{}.spl'.format(sample.name)), 'w')
            dagman_splice.write(dagman_spl)
            dagman_splice.write(dagman_spl_retry)
            dagman_splice.close()

            # copy the config file in the batch directory
            copyfile(opt.CONFIGFILE, os.path.join(sample_batch_dir, opt.CONFIGFILE))

        dagman_file_name = os.path.join(batch_dir, 'dagman.dag')
        dagman_file = open(dagman_file_name, 'w')
        dagman_file.write(dagman_sub)
        dagman_file.write(dagman_dep)
        dagman_file.write(dagman_ret)
        dagman_file.close()

        # create targz file of the code from git
        git_proc = subprocess32.Popen(['git', 'archive', '--format=tar.gz', 'HEAD', '-o',
                                       os.path.join(batch_dir, 'ntuple-tools.tar.gz')], stdout=subprocess32.PIPE)
        # cp TEMPL_TASKDIR/TEMPL_CFG
        print('Ready for submission please run the following commands:')
        # print('condor_submit {}'.format(condor_file_path))
        print('condor_submit_dag {}'.format(dagman_file_name))
        sys.exit(0)

    batch_idx = 0
    if opt.BATCH and opt.RUN:
        batch_idx = int(opt.RUN)

    # test = copy.deepcopy(singleEleE50_PU0)
    # #test.output_filename = 'test2222.root'
    # test.maxEvents = 5
    # test.debug = 6
    # test.eventsToDump = [1, 2, 3, 4]
    # test.clusterize = False
    # test.computeDensity = True
    #
    # test_sample = [test]

    # pool = Pool(1)
    # pool.map(analyze, nugun_samples)
    # pool.map(analyze, test_sample)
    # pool.map(analyze, electron_samples)
    # pool.map(analyze, [singleEleE50_PU200])

    # samples = test_sample
    for sample in samples_to_process:
        analyze(sample, batch_idx=batch_idx)


if __name__ == "__main__":
    try:
        main(analyze=analyze)
    except Exception as inst:
        print (str(inst))
        print ("Unexpected error:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(100)
