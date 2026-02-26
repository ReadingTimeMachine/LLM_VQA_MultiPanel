# run like: mpirun -np 4 python create_figures_batch.py -save_dir "~/Dropbox/wwt_image_extraction/FullProcess_resources/synthetic_figures"

import argparse

parser = argparse.ArgumentParser()

# larger tester
parser.add_argument("-arxiv_dir", nargs='?', default="~/Dropbox/wwt_image_extraction/arxiv_new/")
#parser.add_argument("-save_jsons_dir", nargs='?', default="/Users/jnaiman/Dropbox/wwt_image_extraction/FullProcess_resources/arxiv_new_json_test/") # JPN HERE
parser.add_argument("-save_dir", nargs='?', default="~/Dropbox/jcdl_followup/synthetic_figures/") 
parser.add_argument("-nProcs", nargs='?', default=2)
parser.add_argument("-number_of_figures", nargs='?', default=2)



parser.add_argument("-verbose", nargs='?', default=True) # use only astro papers?
parser.add_argument("-restart", nargs='?', default=False)

# timeout in minutes
parser.add_argument("-time_out", nargs='?', default=5)

parser.add_argument("-fullproc_r", nargs='?', default="~/ArXiv_figure_injection/resources/") 
parser.add_argument("-astroquery_img_dir", nargs='?', default="~/Dropbox/wwt_image_extraction/FullProcess_resources/astroquery_images/") 
parser.add_argument("-save_diagnostic_plot", nargs='?', default=True)



parser.add_argument("-grace_ticks", nargs='?', default=5)
parser.add_argument("-max_tries", nargs='?', default=50)

# ---- hard code a few things for now ----
# format(s) for generated figures?
img_format = ['jpeg']
seeds_dict = None # assume randomized seeds
figdraw = True

######### READ ARGS ###########

args = parser.parse_args()

fullproc_r = args.fullproc_r
fake_figs_dir = args.save_dir
astroquery_img_dir = args.astroquery_img_dir
save_diagnostic_plot = args.save_diagnostic_plot
timeout = args.time_out
restart = args.restart
grace_ticks = args.grace_ticks
itriesMax = args.max_tries
ifigures_max = args.number_of_figures
nProcs = args.nProcs

timeout_seconds = timeout*60

################################
# Imports and Libraries

from utils.main_plot_utils import make_random_plot
import matplotlib.pyplot as plt
import numpy as np

import matplotlib as mpl
# need to use non-interactive!
mpl.use('Agg')
import os
os.environ["PATH"] += os.pathsep + '/Library/TeX/texbin'
mpl.rcParams['text.usetex'] = True
mpl.rcParams['text.latex.preamble'] = r'\usepackage{amsmath} \usepackage{amssymb}' 

from yt.enable_parallelism import turn_on_parallelism
from yt.utilities.parallel_tools.parallel_analysis_interface import parallel_objects
from yt.funcs import is_root
from yt.utilities.parallel_tools.parallel_analysis_interface import communication_system
#print('comm system started')

turn_on_parallelism()

comm = communication_system.communicators[-1]

running_in_parallel = False
# Check if parallel
if comm.size > 1:
    running_in_parallel = True
    if is_root():
        print('Running in parallel')
else:
    print('Running in serial')

########## SETUP ##############

if is_root():
    print('-- Start setup -- ')

fullproc_r = os.path.expanduser(fullproc_r)
fake_figs_dir = os.path.expanduser(fake_figs_dir)
astroquery_img_dir = os.path.expanduser(astroquery_img_dir)


# check directories
img_dir = fake_figs_dir + '/imgs/'
if not os.path.exists(img_dir):
    os.mkdir(img_dir)
    print('made:', img_dir)
json_dir = fake_figs_dir + '/jsons/'
if not os.path.exists(json_dir):
    os.mkdir(json_dir)
    print('made:', json_dir)

for d in ['pickles']:
    pickle_dir = fake_figs_dir + '/'+d+'/'
    if not os.path.exists(pickle_dir):
        os.mkdir(pickle_dir)
        print('made:', pickle_dir)

if save_diagnostic_plot:
    img_dir = fake_figs_dir + '/diags/'
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)
        print('made:', img_dir)


############# RUN THE THING ################
plt.close('all')

ifigures = np.arange(0,ifigures_max)
#print(ifigures)
my_storage = {}

for sto, ifigure in parallel_objects(ifigures, nProcs,storage=my_storage):
    sto.result_id = ifigure

    diagsout = make_random_plot(fake_figs_dir = fake_figs_dir, ifigure=ifigure)



# at end, let us know!
if is_root():
    print('*****************************************')
    print('******* ALL DONE, WOOHOO!! **************')
    print('*****************************************')



