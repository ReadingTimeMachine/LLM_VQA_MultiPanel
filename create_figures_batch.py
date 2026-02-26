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

##### HERE ######
import sys; sys.exit()










######### IMPORTS #############

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2 as cv
import pickle
import pandas as pd
from glob import glob
import json
import os
from copy import deepcopy
#import copy

from utils.metric_utils.utilities import isRectangleOverlap

##import dill

import time

import matplotlib as mpl
# need to use non-interactive!
mpl.use('Agg')

import os
os.environ["PATH"] += os.pathsep + '/Library/TeX/texbin'
mpl.rcParams['text.usetex'] = True
mpl.rcParams['text.latex.preamble'] = r'\usepackage{amsmath} \usepackage{amssymb}' #for \text command

from utils.synthetic_fig_utils import get_nrows_and_ncols, get_ticks, \
 get_font_info

from utils.text_utils import get_popular_nouns, get_inline_math

# create a bunch of fake figures
from utils.synthetic_fig_utils import normalize_params_prob
from utils.plot_parameters import plot_types_params, panel_params, \
  title_params, xlabel_params, colorbar_params, \
  ylabel_params, aspect_fig_params, dpi_params, tight_layout_params, \
  fontsizes, base, aspect_fig_params

from utils.data_utils import get_data, NumpyEncoder

import utils.distribution_utils

from utils.plot_utils import markers
marker_sizes = np.arange(0,10)+1
line_list_thick = np.arange(1,10)

use_uniques = True # use unique inlines
verbose = True

from sys import path
path.append('/Library/TeX/texbin/')

# debug
from importlib import reload

# for seed
from sys import maxsize as maxint

import warnings
warnings.filterwarnings("error")

timeout_seconds = timeout*60


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

if is_root():
    print('-- Start setup -- ')

### other libraries ###

# for debugging
import utils, utils.data_utils, utils.distribution_utils, utils.synthetic_fig_utils, utils.plot_utils, utils.figure_gen_utils.misc, utils.plot_check_utils, utils.tmp_port_from_script, utils.plot_parameters
# reload
reload(utils)
reload(utils.synthetic_fig_utils)
reload(utils.distribution_utils)
reload(utils.plot_utils)
reload(utils.data_utils)
reload(utils.figure_gen_utils.misc)
reload(utils.plot_check_utils)
reload(utils.tmp_port_from_script)
reload(utils.plot_parameters)


# import things
from utils.figure_gen_utils.pixel_location_utils import get_data_pixel_locations
from utils.figure_gen_utils.misc import log_scale_ax, add_annotations
from utils.data_utils import get_data, get_contour_data, get_image_of_the_sky_data
from utils.distribution_utils import get_gmm, get_gmm_data
from utils.plot_utils import make_plot, get_image_of_the_sky_plot
from utils.synthetic_fig_utils import get_titles_or_labels, get_titles_or_labels_ra_dec, normalize_params_prob, get_font_params, add_titles_and_labels, collect_plot_data_axes
from utils.plot_check_utils import check_aspect, check_labels_titles_off_page, set_all_seeds

from utils.tmp_port_from_script import reset_everybody, make_base_plot, set_figure_params, check_exceptions1, \
    create_data_save_dict, print_figure_params, close_plot_fail, close_plot_success, get_plot_data, \
    fill_datas, generate_data, collect_saved_labels, parse_colorbar_data, detect_cb_axes, collect_boxes, \
    update_fonts_boxes_overlap, check_plot_area, flip_colors

#from utils.plot_utils import memory_safe_plot

from utils.plot_parameters import plot_flip_params

############# SMALL FUNCTIONS ##########
import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Function timed out")

# memory leaks
import gc

import psutil
import os
import sys

def get_memory_mb():
    """Get current process memory in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def get_size_mb(obj):
    """Get size of an object in MB (approximate)"""
    return sys.getsizeof(obj) / 1024 / 1024

############ MORE SETUP #############

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



# get fonts -- see "cnn_create_synthetic_ticks" in FullProcess
dfont = pd.read_csv(fullproc_r + 'fonts.csv')

# check that location is there
drop_names = []
for fl in dfont['font location']:
    if not os.path.exists(fl):
        drop_names.append(False)
    else:
        drop_names.append(True)

font_names1 = dfont.loc[drop_names]['font name'].values

# known ones to remove
known_remove_fonts = ['.SF Compact']
font_names = []
for f in font_names1:
    if f in known_remove_fonts:
        pass
    else:
        font_names.append(f)

# for plot styles
plot_styles = [
    'default',
    'Solarize_Light2',
    '_classic_test_patch',
    '_mpl-gallery',
    '_mpl-gallery-nogrid',
    'bmh',
    'classic',
    #'dark_background',
    'fast',
    'fivethirtyeight',
    'ggplot',
    'grayscale',
    #'seaborn-v0_8',
    'seaborn-v0_8-bright',
    #'seaborn-v0_8-colorblind',
    #'seaborn-v0_8-dark',
    'seaborn-v0_8-dark-palette',
    #'seaborn-v0_8-darkgrid',
    'seaborn-v0_8-deep',
    'seaborn-v0_8-muted',
    'seaborn-v0_8-notebook',
    'seaborn-v0_8-paper',
    'seaborn-v0_8-pastel',
    'seaborn-v0_8-poster',
    'seaborn-v0_8-talk',
    #'seaborn-v0_8-ticks',
    #'seaborn-v0_8-white',
    #'seaborn-v0_8-whitegrid',
    'tableau-colorblind10'
]

# colormaps
color_maps = plt.colormaps()

# get words
popular_nouns = get_popular_nouns(fullproc_r + 'data/', verbose=False)
# inline math
inlines = get_inline_math(fullproc_r,
                          recreate_inlines=False,
                         use_uniques=use_uniques, verbose = False)


############## PLOT PARAMS ###################

plot_params = deepcopy(plot_types_params)

### Scatter plots
linestyles = ['-', '--', ':'] # only use a subset of the linestyles

plot_params_line = {'scatter':plot_params['scatter'].copy()}

plot_params_line['scatter']['npoints'] = {'min':10, 'max':150}

plot_params_line['scatter']['colormap scatter'] = {'prob': 0.85}

# just linear, random
plot_params_line['scatter']['distribution']['random']['prob'] = 1 # 

# gaussian mixture model
plot_params_line['scatter']['distribution']['gmm']['prob'] = 1
plot_params_line['scatter']['distribution']['gmm']['nclusters'] = {'min': 1, 'max': 5}
plot_params_line['scatter']['distribution']['gmm']['nsamples'] = {'min': 10, 'max': 50}

# linear plots
plot_params_line['scatter']['distribution']['linear']['prob'] = 1

# probability of getting a scatter plot
plot_params_line['scatter']['prob'] = 1

### Line plots
plot_params_line['line'] = plot_params['line'].copy()

plot_params_line['line']['npoints'] = {'min':10, 'max':100}
plot_params_line['line']['nlines'] = {'min':1, 'max':10}

# just linear, random
plot_params_line['line']['distribution']['random']['prob'] = 1

# gaussian mixture model
plot_params_line['line']['distribution']['gmm']['prob'] = 1
plot_params_line['line']['distribution']['gmm']['histogram as line']['prob'] = 1
plot_params_line['line']['distribution']['gmm']['nclusters'] = {'min': 1, 'max': 5}
plot_params_line['line']['distribution']['gmm']['nsamples'] = {'min': 10, 'max': 50}

# linear plots
plot_params_line['line']['distribution']['linear']['prob'] = 1

# Prob for getting line
plot_params_line['line']['prob'] = 1

### Histograms
#linestyles_hist = ['-', ':'] # only use a subset of the linestyles
linestyles_hist = ['-'] # only use a subset of the linestyles

plot_params_line['histogram'] = plot_params['histogram'].copy()

# no horizontal plots
plot_params_line['histogram']['horizontal prob'] = 0.0

# random distributions
plot_params_line['histogram']['distribution']['random']['prob'] = 1

# gaussian mixture model
plot_params_line['histogram']['distribution']['gmm']['prob'] = 1
plot_params_line['histogram']['distribution']['gmm']['nclusters'] = {'min': 1, 'max': 5}
plot_params_line['histogram']['distribution']['gmm']['nsamples'] = {'min': 10, 'max': 500}

# linear distributions prob
plot_params_line['histogram']['distribution']['linear']['prob'] = 1

# prob for getting a histogram
plot_params_line['histogram']['prob'] = 1

### Contours
plot_params_line['contour'] = plot_params['contour'].copy()

plot_params_line['contour']['nlines']['min'] = 1
plot_params_line['contour']['nlines']['max'] = 5

# lower resolution?
plot_params_line['contour']['npoints']  = {'nx':{'min':10,'max':100}, 'ny':{'min':10,'max':100}}

# prob of getting a contour plot
plot_params_line['contour']['prob'] = 1


### Images of the sky
plot_params_line['image of the sky'] = plot_params['image of the sky'].copy()

# lines if overplotting like with contours
plot_params_line['image of the sky']['nlines']['min'] = 1
plot_params_line['image of the sky']['nlines']['max'] = 5

# if image of sky, use an "image of the sky" from astroquery or a GMM distribution?
plot_params_line['image of the sky']['distribution']['gmm']['prob'] = 1 
plot_params_line['image of the sky']['distribution']['sky']['prob'] = 1

# if querying with astroquery, where are tables (object+wavelengths) and storage of already downloaded files?
# 1. these contain combos of object + wavelength from our historical corpus
plot_params_line['image of the sky']['distribution']['sky']['object wavelength table'] = fullproc_r + '/object_wavelength_pairs.pickle'
# where to store images once they have been queried & downloaded
plot_params_line['image of the sky']['distribution']['sky']['query images dir'] = astroquery_img_dir

# image or lines
plot_params_line['image of the sky']['image or contour']['prob']['image'] = 1000

# lower resolution?
plot_params_line['image of the sky']['npoints']  = {'nx':{'min':10,'max':100}, 'ny':{'min':10,'max':100}}

# prob of getting an image of the sky
plot_params_line['image of the sky']['prob'] = 1


### Other params
panel_params['number prob']['median'] = 4 # smaller, usually use 4-ish, 1 for debugging
panel_params['number prob']['max'] = 25 # 2 for debugging, 25 for typical run

# prob of equations
title_params['equation']['prob'] = 0.25 # probability any word will be equation
xlabel_params['equation']['prob'] = 0.25 # probability any word will be equation
ylabel_params['equation']['prob'] = 0.25 # probability any word will be equation

colorbar_params['prob'] = 1.0 # prob of plot having colorbar

tight_layout_params = {'prob':1.0, # prob of tight layout
                       'pad':{'min':0.0, 'max':0.1}, 
                       'w_pad':{'min':0.0, 'max':0.1}, 
                       'h_pad':{'min':0.0, 'max':0.1}
                       }# for now

### normalize everybody
plot_params_line, panel_params, \
  title_params, xlabel_params, \
  ylabel_params = normalize_params_prob(plot_params_line.copy(), panel_params, 
                                        title_params, xlabel_params, 
                                        ylabel_params, colorbar_params, 
                                        verbose=False)


fontsize_min = fontsizes['fontsize min']
aspect_cut = {'min':0.3, 'max':4.0}

if is_root():
    print('-- Done with setup -- ')

# # ## DEBUG ##
# panel_params['number prob']['median'] = 1 # smaller, usually use 4-ish, 1 for debugging
# panel_params['number prob']['max'] = 1 # 2 for debugging, 25 for typical run
# plot_params_line['image of the sky']['prob'] = 1/3 #1/5 #1./5
# plot_params_line['scatter']['prob'] = 0 #1/5 #1./5
# plot_params_line['histogram']['prob'] = 0 #1./5
# plot_params_line['line']['prob'] = 1/3 # 1./5
# plot_params_line['contour']['prob'] = 1/3 # 1./5
# plot_params_line['image of the sky']['distribution']['gmm']['prob'] = 0 #/2 
# plot_params_line['image of the sky']['distribution']['sky']['prob'] = 1 #1/2 #1/2 
# plot_params_line['image of the sky']['colormap contour']['prob'] = 0 #/2 
# #plot_flip_params['prob'] = 0.25 # higher for testing

########################################################
########################################################
########################################################
########################################################
########################################################
########################################################



###################### DO THE THING ##########################
success_plot = False # overall plot
# keep titles
xlabels_pull = deepcopy(popular_nouns)
ylabels_pull = deepcopy(popular_nouns)
titles_pull = deepcopy(popular_nouns)

plot_params_here = plot_params_line.copy()

plt.close('all')

ifigures = np.arange(0,ifigures_max)
#print(ifigures)
my_storage = {}

for sto, ifigure in parallel_objects(ifigures, nProcs,storage=my_storage):
    sto.result_id = ifigure

    print('')
    if verbose:
        print('*************** Figure', ifigure+1, '****************')
    # check if there for all formats
    hasFig = []
    for iformat in img_format:
        if os.path.exists(fake_figs_dir + 'imgs/Picture_' + str(ifigure+1).zfill(6) + '.'+iformat):
            hasFig.append(iformat)
    # and json
    if os.path.exists(fake_figs_dir + 'jsons/Picture_' + str(ifigure+1).zfill(6) + '.json'):
        hasFig.append('json')
    if (len(hasFig) == len(img_format) + 1) and not restart: # extra 1 for json
        if verbose:
            print('  already have:', fake_figs_dir + 'imgs/Picture_' + str(ifigure+1).zfill(6) + '.<FMT>')
        continue

    # set all seeds and random generators for this figure
    rng_dict, seeds_dict = set_all_seeds(reset_outer = True, 
                            reset_inner = True, 
                            reset_titles=True, 
                            reset_fonts = True, 
                            reset_aspect = True, 
                            reset_ptype=True, 
                            seeds_dict=seeds_dict)
    # set other params
    figure_params = set_figure_params(rng_dict, color_maps, plot_styles, 
                                      aspect_fig_params, dpi_params, 
                                      panel_params, tight_layout_params, base, plot_flip_params,
                                      verbose=verbose)

    # ### DEBUG ###
    # figure_params['# columns'] = 3
    # figure_params['# rows'] = 1
    # debug_plot_types = ['line', 'contour', 'image of the sky']

    font_params = get_font_params(rng_dict, fontsizes, font_names)

    # keep titles
    xlabels_pull = np.stack((np.array(deepcopy(popular_nouns)),) * figure_params['# panels'], axis=0)
    ylabels_pull = np.stack((np.array(deepcopy(popular_nouns)),) * figure_params['# panels'], axis=0)
    titles_pull = np.stack((np.array(deepcopy(popular_nouns)),) * figure_params['# panels'], axis=0)

    # for each plot, make data
    data_save = create_data_save_dict()
    # try to make data
    success_plot = False # flag for if we keep running while loop for fig generation
    success_flags = {'get base plot':False, 'get data for plot':False, 
                     'get data from plot':False, 'get titles':False, 'get colorbar titles':False, 
                     'get colorbar fonts':True}
    success_get_base_plot = False # do we need to re-generate figure axes?

    # for inner loop of tries for a figure
    itries = 0
    # to start
    fig, datas, imgplot, axes_from_loop, axes_save, \
                       cbar_axes_save, cbars, plot_data_all, plot_data = [None]*9
    # ------- inner loop -------
    while itries < itriesMax and not success_plot:
        # try:
        #     data
        # except:
        #     datas = None
        # try:
        #     cbar_axes_save
        # except:
        #     cbar_axes_save = None
        # cbar_axes_save = None
        gc.collect()
        if verbose: print(' ------ ON itries:', itries, '----------')
        itries += 1
        if itries >= itriesMax:
            itries = 0
            if verbose: print('RESET EVERYBODY')
            success_plot = False
            plt.close('all')
            # have to reset everybody
            rng_dict, seeds_dict, figure_params, \
                font_params, xlabels_pull, ylabels_pull, \
                    titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                                                                aspect_fig_params, dpi_params, 
                                                                panel_params, tight_layout_params, 
                                                                fontsizes, font_names, popular_nouns, success_flags)  
            try:
                del fig
            except:
                pass
            try:
                del datas
            except:
                pass
            try:
                del data_save
            except:
                pass
            try: 
                del axes_from_loop
            except:
                pass
            try:
                del axes_save
            except:
                pass
            try:
                del cbar_axes_save
            except:
                pass
            try:
                del cbars
            except:
                pass
            try:
                del plot_data_all
            except:
                pass
            try:
                del plot_data
            except:
                pass
            gc.collect()
            data_save = create_data_save_dict()
        #if fig is not None:
        try:
            fig
        except:
            fig = None

        # close figure as needed
        close_plot_fail(fig, ifigure, fake_figs_dir, img_format, remove_diags=False)

        ################# GET BASIC FIGURE #################
        # ### DEBUG ###
        # figure_params['# columns'] = 3
        # figure_params['# rows'] = 1
        try:
            if not success_flags['get base plot']:
                gc.collect()
                plt.close('all')
                if verbose:
                    print('  -- generating base fig')
                    print_figure_params(figure_params)
                # make base fig
                fig, axes_save, plot_inds, figsize = make_base_plot(figure_params, verbose=False)
                success_flags['get base plot'] = True
                data_save['figsize'] = figsize
                figure_params['facecolor'] = fig.get_facecolor()
                if figdraw: fig.canvas.draw() # just give it a shot here
                #success_plot = True
        except Exception as e1:
            success_plot, rng_dict, seeds_dict, figure_params, \
                font_params, xlabels_pull, ylabels_pull, \
                    titles_pull, data_save, \
                        success_flags = check_exceptions1(e1, fontsizes, 
                                                        font_names, 
                            rng_dict, seeds_dict, figure_params, font_params, 
                            xlabels_pull, ylabels_pull, titles_pull, 
                            data_save, success_flags,color_maps, plot_styles, 
                    aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
                            verbose = True)  

        if not success_flags['get base plot']: # re do the loop
            continue  

        ################### CREATE DATA, ALL AXES ############  
        err_add = ''    
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)  # e.g., 300 for 5 minutes  
        try:
            # first, get all the data for the plot
            if not success_flags['get data for plot']:
                if verbose: print('  -- generating data for plot')
                plot_data_all = []
                for iplot, ax in enumerate(axes_save):
                    plot_data, err = get_plot_data(plot_params_here, 
                        rng_dict['inner'], 
                        figure_params=figure_params)
                    # ##### DEBUG #####
                    # plot_data, err = get_plot_data(plot_params_here, 
                    #     rng_dict['inner'], plot_type=debug_plot_types[iplot],
                    #     figure_params=figure_params)
                    if err:
                        del plot_data
                        break
                    plot_data_all.append(deepcopy(plot_data))
                success_flags['get data for plot'] = True
        except TimeoutError as et:
            err = True
            success_plot, rng_dict, seeds_dict, figure_params, \
            font_params, xlabels_pull, ylabels_pull, \
                titles_pull, data_save, \
                    success_flags = check_exceptions1(et, fontsizes, 
                                                    font_names, 
                        rng_dict, seeds_dict, figure_params, font_params, 
                        xlabels_pull, ylabels_pull, titles_pull, 
                        data_save, success_flags,color_maps, plot_styles, 
                aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
                        verbose = True) 
        except Exception as e2:
                err = True
                err_add = str(e2)
        finally:
            signal.alarm(0)

        if err: # either via exception or not
            success_flags['get data for plot'] = False
            success_plot = False
            plt.close('all')
            # have to reset everybody
            rng_dict, seeds_dict, figure_params, \
                font_params, xlabels_pull, ylabels_pull, \
                    titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                                                                aspect_fig_params, dpi_params, 
                                                                panel_params, tight_layout_params, 
                                                                fontsizes, font_names, popular_nouns, success_flags)
            # del fig, datas, data_save,  axes_from_loop, axes_save, \
            #             cbar_axes_save, cbars, plot_data_all, plot_data
            try:
                del fig
            except:
                pass
            try:
                del datas
            except:
                pass
            try:
                del data_save
            except:
                pass
            try: 
                del axes_from_loop
            except:
                pass
            try:
                del axes_save
            except:
                pass
            try:
                del cbar_axes_save
            except:
                pass
            try:
                del cbars
            except:
                pass
            try:
                del plot_data_all
            except:
                pass
            try:
                del plot_data
            except:
                pass
            gc.collect()
            data_save = create_data_save_dict()
            if verbose:
                print('[ERROR]: in getting data, will reset and try again.')  
                if len(err_add) > 0:
                        print('  -- added error:', err_add)    
        if not success_flags['get data for plot']:
            continue    


        ############# GET DATA FROM PLOT, ALL AXES ###########  
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)  # e.g., 300 for 5 minutes  
        err_full = False                                 
        try:
            if not success_flags['get data from plot']:
                if verbose: print('  -- getting data *from* plot')
                axes_from_loop = []
                for iplot, ax in enumerate(axes_save):
                    # get data for this plot
                    plot_data = plot_data_all[iplot]
                    # create axes and plot data
                    result = generate_data(fig, iplot, figure_params, plot_data, 
                                                    rng_dict['inner'], verbose=False)
                    if result is not None:
                        generated_data, ax, err = result
                    else:
                        generated_data, ax, err = None, None, True
                    if err:
                        err_full = True
                        if verbose: print('[ERROR]: "generate_data" led to memory overflow')
                        break # end this loop over axes
                    # save axes
                    axes_from_loop.append(ax)
                    # save
                    data_save['data_for_plots'].append(deepcopy(plot_data['data_for_plot']))
                    data_save['plot_types'].append(deepcopy(plot_data['plot_type']))
                    data_save['data_from_plots'].append(generated_data['data_from_plot'])                    
                    data_save['distribution_types'].append(deepcopy(plot_data['distribution_type']))
            if figdraw: fig.canvas.draw() # try again here
            if not err_full:
                success_flags['get data from plot'] = True
        except TimeoutError as et:
            success_plot, rng_dict, seeds_dict, figure_params, \
            font_params, xlabels_pull, ylabels_pull, \
                titles_pull, data_save, \
                    success_flags = check_exceptions1(et, fontsizes, 
                                                    font_names, 
                        rng_dict, seeds_dict, figure_params, font_params, 
                        xlabels_pull, ylabels_pull, titles_pull, 
                        data_save, success_flags,color_maps, plot_styles, 
                aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
                        verbose = True)          
        except Exception as e3:   
            success_plot, rng_dict, seeds_dict, figure_params, \
            font_params, xlabels_pull, ylabels_pull, \
                titles_pull, data_save, \
                    success_flags = check_exceptions1(e3, fontsizes, 
                                                    font_names, 
                        rng_dict, seeds_dict, figure_params, font_params, 
                        xlabels_pull, ylabels_pull, titles_pull, 
                        data_save, success_flags,color_maps, plot_styles, 
                aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
                        verbose = True)
        finally:
            signal.alarm(0)

        if not success_flags['get data from plot']:
            continue   

        ################# SET TITLES AND AXIS LABELS ##############
        try:
            if not success_flags['get titles']:
                if verbose: print('  -- generating titles and axis labels')
                xp,yp,tp = [],[],[]
                xpt,ypt,tpt = [],[],[]
                for iplot, ax in enumerate(axes_from_loop):
                    # get data for this plot
                    plot_data = plot_data_all[iplot]
                    success_loop_labels = False
                    itries_labels = 0
                    while not success_loop_labels and itries_labels <= itriesMax:
                        gc.collect()
                        itries_labels +=1
                        title, xlabel, ylabel = add_titles_and_labels(plot_data['plot_type'], plot_data['plot_params_here_ax'], 
                                                                plot_data['data_for_plot'],
                                                                ax, xlabels_pull[iplot], ylabels_pull[iplot], 
                                                                titles_pull[iplot], inlines,
                                                            title_params, xlabel_params, ylabel_params, font_params, 
                                                            rng=rng_dict['titles'])
            
                        xlabels_pull2, ylabels_pull2, titles_pull2, err = collect_saved_labels(xlabel, ylabel, title)

                        if err: # issue getting labels, pull again
                            del title, xlabel, ylabel
                            continue
                        xp.append(xlabels_pull2); yp.append(ylabels_pull2); tp.append(titles_pull2)
                        xpt.append(xlabel); ypt.append(ylabel); tpt.append(title)
                        success_loop_labels = True
                if not success_loop_labels or itries_labels >= itriesMax:
                    success_flags['get titles'] = False
                    success_plot = False
                    plt.close('all')
                    # have to reset everybody
                    rng_dict, seeds_dict, figure_params, \
                        font_params, xlabels_pull, ylabels_pull, \
                            titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                                                                    aspect_fig_params, dpi_params, 
                                                                    panel_params, tight_layout_params, 
                                                                    fontsizes, font_names, popular_nouns, success_flags)
                    del fig, datas, data_save,  axes_from_loop, axes_save, \
                        cbar_axes_save, cbars, plot_data_all, plot_data
                    gc.collect()
                    data_save = create_data_save_dict()
                else: # all is well so far!
                    try:
                        if figdraw: fig.canvas.draw() # try again
                        data_save['titles'] = tpt
                        data_save['xlabels'] = xpt
                        data_save['ylabels'] = ypt
                        fontcolor = xpt[0].get_color()
                        xlabels_pull = deepcopy(xp)
                        ylabels_pull = deepcopy(yp)
                        titles_pull = deepcopy(tp) 
                        success_flags['get titles'] = True  
                    except Exception as e44:   
                            success_plot, rng_dict, seeds_dict, figure_params, \
                            font_params, xlabels_pull, ylabels_pull, \
                                titles_pull, data_save, \
                                    success_flags = check_exceptions1(e44, fontsizes, 
                                                                    font_names, 
                                        rng_dict, seeds_dict, figure_params, font_params, 
                                        xlabels_pull, ylabels_pull, titles_pull, 
                                        data_save, success_flags,color_maps, plot_styles, 
                    aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
                                        verbose = True)
                    #print('  *** titles, xlabels, ylabels:', tpt, xpt, ypt)
        except Exception as e4:   
                success_plot, rng_dict, seeds_dict, figure_params, \
                font_params, xlabels_pull, ylabels_pull, \
                    titles_pull, data_save, \
                        success_flags = check_exceptions1(e4, fontsizes, 
                                                        font_names, 
                            rng_dict, seeds_dict, figure_params, font_params, 
                            xlabels_pull, ylabels_pull, titles_pull, 
                            data_save, success_flags,color_maps, plot_styles, 
                    aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
                            verbose = True)
        if not success_flags['get titles']:
            continue

        ################# SET TITLES AND AXIS LABELS ##############
        try:
            if not success_flags['get titles']:
                if verbose: print('  -- generating titles and axis labels')
                xp,yp,tp = [],[],[]
                xpt,ypt,tpt = [],[],[]
                for iplot, ax in enumerate(axes_from_loop):
                    # get data for this plot
                    plot_data = plot_data_all[iplot]
                    success_loop_labels = False
                    itries_labels = 0
                    while not success_loop_labels and itries_labels <= itriesMax:
                        gc.collect()
                        itries_labels +=1
                        title, xlabel, ylabel = add_titles_and_labels(plot_data['plot_type'], plot_data['plot_params_here_ax'], 
                                                                plot_data['data_for_plot'],
                                                                ax, xlabels_pull[iplot], ylabels_pull[iplot], 
                                                                titles_pull[iplot], inlines,
                                                            title_params, xlabel_params, ylabel_params, font_params, 
                                                            rng=rng_dict['titles'])
            
                        xlabels_pull2, ylabels_pull2, titles_pull2, err = collect_saved_labels(xlabel, ylabel, title)

                        if err: # issue getting labels, pull again
                            del title, xlabel, ylabel
                            continue
                        xp.append(xlabels_pull2); yp.append(ylabels_pull2); tp.append(titles_pull2)
                        xpt.append(xlabel); ypt.append(ylabel); tpt.append(title)
                        success_loop_labels = True
                if not success_loop_labels or itries_labels >= itriesMax:
                    success_flags['get titles'] = False
                    success_plot = False
                    plt.close('all')
                    # have to reset everybody
                    rng_dict, seeds_dict, figure_params, \
                        font_params, xlabels_pull, ylabels_pull, \
                            titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                                                                    aspect_fig_params, dpi_params, 
                                                                    panel_params, tight_layout_params, 
                                                                    fontsizes, font_names, popular_nouns, success_flags)
                    del fig, datas, data_save,  axes_from_loop, axes_save, \
                        cbar_axes_save, cbars, plot_data_all, plot_data
                    gc.collect()
                    data_save = create_data_save_dict()
                else: # all is well so far!
                    try:
                        if figdraw: fig.canvas.draw() # try again
                        data_save['titles'] = tpt
                        data_save['xlabels'] = xpt
                        data_save['ylabels'] = ypt
                        fontcolor = xpt[0].get_color()
                        xlabels_pull = deepcopy(xp)
                        ylabels_pull = deepcopy(yp)
                        titles_pull = deepcopy(tp) 
                        success_flags['get titles'] = True  
                    except Exception as e44:   
                            success_plot, rng_dict, seeds_dict, figure_params, \
                            font_params, xlabels_pull, ylabels_pull, \
                                titles_pull, data_save, \
                                    success_flags = check_exceptions1(e44, fontsizes, 
                                                                    font_names, 
                                        rng_dict, seeds_dict, figure_params, font_params, 
                                        xlabels_pull, ylabels_pull, titles_pull, 
                                        data_save, success_flags,color_maps, plot_styles, 
                    aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
                                        verbose = True)
        except Exception as e4:   
                success_plot, rng_dict, seeds_dict, figure_params, \
                font_params, xlabels_pull, ylabels_pull, \
                    titles_pull, data_save, \
                        success_flags = check_exceptions1(e4, fontsizes, 
                                                        font_names, 
                            rng_dict, seeds_dict, figure_params, font_params, 
                            xlabels_pull, ylabels_pull, titles_pull, 
                            data_save, success_flags,color_maps, plot_styles, 
                    aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
                            verbose = True)
        if not success_flags['get titles']:
            continue


        #import sys; sys.exit()
        # get fontcolor
        figure_params['fontcolor'] = fontcolor
        ############# GET COLOR BARS ##############
        try:
            # get colorbar stuff for each plot
            if not success_flags['get colorbar titles']:
                cbar_words_list = popular_nouns
                cbar_inlines = inlines
                cbar_nums = []; cbar_words = []; cbars = []
                for iplot, ax in enumerate(axes_from_loop):
                    cbar, colorbar_words = parse_colorbar_data(data_save['plot_types'][iplot],  
                                                        data_save['data_from_plots'][iplot], 
                                                        fig, rng_dict['inner'], 
                                                        font_params, title_params,colorbar_params,
                                                        data_save['data_for_plots'][iplot],
                                                        popular_nouns=cbar_words_list,
                                                        inlines=cbar_inlines)
                    # fill datasave
                    cbars.append(cbar)
                    cbar_words.append(colorbar_words)
                    if cbar is not None:
                        cbar_nums.append(len(cbar_nums)) # save axis of this colorbar
                        cbar_nums.append(len(cbar_nums)) # add extra for axes for colorbar
                    else:
                        cbar_nums.append(-1)
                if figdraw: fig.canvas.draw() # with norm, now need to draw after
                success_flags['get colorbar titles'] = True
                data_save['cbars'] = cbars
                data_save['cbar_words'] = deepcopy(cbar_words)
                data_save['cbar_nums'] = deepcopy(cbar_nums)
        except Exception as ec:
            success_plot = False
            success_flags['get colorbar titles'] = False
            success_plot, rng_dict, seeds_dict, figure_params, \
                font_params, xlabels_pull, ylabels_pull, \
                    titles_pull, data_save, \
                        success_flags = check_exceptions1(ec, fontsizes, 
                                                        font_names, 
                            rng_dict, seeds_dict, figure_params, font_params, 
                            xlabels_pull, ylabels_pull, titles_pull, 
                            data_save, success_flags,color_maps, plot_styles, 
                    aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
                            verbose = True, error_front=' in parse_colorbar_data -- ')                    
        if not success_flags['get colorbar titles']:
            continue


        ############# SET FINAL COLORS ###########
        plt.set_cmap(figure_params['color map'])
        plt.style.use(figure_params['plot style'])
        plt.rcParams['font.family'] = str(font_params['csfont']['fontname'])
        f2 = fig.get_facecolor()
        success_flip = False
        # flip?
        if figure_params['flipped font/face colors']:
            fig, facecolor, fontcolor, cbarsout = flip_colors(fig, data_save, figure_params, axes_from_loop)
            figure_params['fontcolor'] = fontcolor
            figure_params['facecolor'] = facecolor
        else:
            cbarsout = data_save['cbars']
        try:
            fig.canvas.draw()
            data_save['cbars'] = cbarsout
            success_flip = True
        except Exception as ec11:
            success_flip = False
            success_plot, rng_dict, seeds_dict, figure_params, \
                font_params, xlabels_pull, ylabels_pull, \
                    titles_pull, data_save, \
                        success_flags = check_exceptions1(ec11, fontsizes, 
                                                        font_names, 
                            rng_dict, seeds_dict, figure_params, font_params, 
                            xlabels_pull, ylabels_pull, titles_pull, 
                            data_save, success_flags,color_maps, plot_styles, 
                    aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
                            verbose = True, error_front=' in fliping colors -- ')
                    
        if not success_flip:
            continue


        ##############################################     
        ########## END OF TRYING TO MAKE PLOT ########
        ##############################################

        # import sys; sys.exit()

        ####### SAVE DATA #########
        # if we've made it thus far, lets collect all the data
        success_fill_data = False
        try:
            datas, width, height = fill_datas(fig, figure_params, font_params, plot_inds)
            success_fill_data = True
        except Exception as e_fill_data1:
            success_fill_data = False
            if 'Tight layout not applied' in str(e_fill_data1): # issue with tight layout, redo
                if verbose: print('[ERROR]: tight layout not applied, take 2 - ', str(e_fill_data1))
                success_plot = False
                plt.close('all')
                # have to reset everybody
                rng_dict, seeds_dict, figure_params, \
                    font_params, xlabels_pull, ylabels_pull, \
                        titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                                                                 aspect_fig_params, dpi_params, 
                                                                 panel_params, tight_layout_params, 
                                                                 fontsizes, font_names, popular_nouns, success_flags)  
            else:   
                if verbose: print('[ERROR]: in getting data from plot - ', str(e_fill_data1))
                plt.close('all')
                success_plot = False
                # have to reset everybody
                rng_dict, seeds_dict, figure_params, \
                    font_params, xlabels_pull, ylabels_pull, \
                        titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                                                                 aspect_fig_params, dpi_params, 
                                                                 panel_params, tight_layout_params, 
                                                                 fontsizes, font_names, popular_nouns, success_flags)  
                del fig, datas, data_save,  axes_from_loop, axes_save, \
                        cbar_axes_save, cbars, plot_data_all, plot_data
                gc.collect()
                data_save = create_data_save_dict()
        if not success_fill_data:    
            continue   


        # which are axis and which are not?
        axes_save, cbar_axes_save, err = detect_cb_axes(fig, data_save['cbar_nums'])
        if err:
            plt.close('all')
            success_plot = False
            # have to reset everybody
            rng_dict, seeds_dict, figure_params, \
                font_params, xlabels_pull, ylabels_pull, \
                    titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                                                                aspect_fig_params, dpi_params, 
                                                                panel_params, tight_layout_params, 
                                                                fontsizes, font_names, popular_nouns, success_flags) 
            del fig, datas, data_save,  axes_from_loop, axes_save, \
                        cbar_axes_save, cbars, plot_data_all, plot_data
            gc.collect()
            data_save = create_data_save_dict()
            continue


        # save the fig
        success_save = False
        try:
            for iformat in img_format:
                fig.tight_layout(h_pad=figure_params['layout h_pad'], w_pad=figure_params['layout w_pad'], pad=figure_params['layout pad'])
                fig.savefig(fake_figs_dir + 'imgs/Picture_' + str(ifigure+1).zfill(6) + '.'+iformat, 
                            dpi=figure_params['dpi'], facecolor=figure_params['facecolor'])
                if verbose: print('saved:', fake_figs_dir + 'imgs/Picture_' + str(ifigure+1).zfill(6) + '.' +iformat)
            success_save = True
        except Exception as esave:
            success_save = False
            success_plot, rng_dict, seeds_dict, figure_params, \
                font_params, xlabels_pull, ylabels_pull, \
                    titles_pull, data_save, \
                        success_flags = check_exceptions1(esave, fontsizes, 
                                                        font_names, 
                            rng_dict, seeds_dict, figure_params, font_params, 
                            xlabels_pull, ylabels_pull, titles_pull, 
                            data_save, success_flags,color_maps, plot_styles, 
                    aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
                            verbose = True, error_front=' saving figure failed -- ')

        if not success_save:
            continue


        # Save the data from the fig and for the fig
        success_fill_data = False
        try:
            for iplot, (ax,cbar_ax) in enumerate(zip(axes_save,cbar_axes_save)): ### XYZ, only 1 axis here
                datas['plot' + str(iplot)], err = collect_plot_data_axes(ax, fig,
                                height, width,
                                data_save['data_from_plots'][iplot], 
                                data_save['data_for_plots'][iplot], 
                                data_save['plot_types'][iplot], data_save['titles'][iplot], 
                                data_save['xlabels'][iplot], data_save['ylabels'][iplot],
                                data_save['distribution_types'][iplot], cbar_ax=cbar_ax,
                                colorbar_verbose=False,
                                verbose=True)#, error_out=False)
            # one extra
            datas['figure']['figsize'] = data_save['figsize']
            datas['figure']['facecolor'] = figure_params['facecolor']
            if not err: 
                success_fill_data = True
                if verbose: print('  -- filled "datas" with to/from plot')
            else: # no idea, reset everybody
                #laksjflasj
                success_fill_data = False
                plt.close('all')
                # have to reset everybody
                rng_dict, seeds_dict, figure_params, \
                    font_params, xlabels_pull, ylabels_pull, \
                        titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                                                                 aspect_fig_params, dpi_params, 
                                                                 panel_params, tight_layout_params, 
                                                                 fontsizes, font_names, popular_nouns, success_flags)
                del fig, datas, data_save,  axes_from_loop, axes_save, \
                        cbar_axes_save, cbars, plot_data_all, plot_data
                gc.collect()
                data_save = create_data_save_dict()
        except Exception as e_fill_data:
            laskjfal
            success_fill_data = False
            if verbose:
                print('[ERROR] 2: ' + str(e_fill_data))
            if 'Glyph' in str(e_fill_data) and 'missing' in str(e_fill_data): # missing a glyph, try different font
                _, _, _, _, _, _, csfont = get_font_info(fontsizes, font_names, rng=rng_dict['font'])
                font_params['csfont'] = csfont
                success_flags['get titles'] = False
            else: # no idea! reset everybody
                # have to reset everybody
                plt.close('all')
                rng_dict, seeds_dict, figure_params, \
                    font_params, xlabels_pull, ylabels_pull, \
                        titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                                                                 aspect_fig_params, dpi_params, 
                                                                 panel_params, tight_layout_params, 
                                                                 fontsizes, font_names, popular_nouns, success_flags)
                del fig, datas, data_save,  axes_from_loop, axes_save, \
                        cbar_axes_save, cbars, plot_data_all, plot_data
                gc.collect()
                data_save = create_data_save_dict()
        if not success_fill_data:
            continue

        #import sys; sys.exit()

        ################################################################
        ########### CHECKS -- titles off, bounding boxes, etc ##########
        ################################################################
        if verbose: print('  -- running checks...')

        # 1. Check for square with weird aspect ratio
        try:
            success_aspect, aspect_errors_iplot = check_aspect(datas, aspect_cut, verbose=verbose)
        except Exception as ea:
            if verbose: print('[ERROR]: in check_aspect -- ', str(ea))
            success_aspect = False
            if 'cannot unpack non-iterable' in str(ea):
                lkfjalsj
        if not success_aspect:
            print('[UPDATE]: JPN -- should in theory just re-grab data for this index plot!!')
            plt.close('all')
            # have to reset everybody
            rng_dict, seeds_dict, figure_params, \
                font_params, xlabels_pull, ylabels_pull, \
                    titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                                                                aspect_fig_params, dpi_params, 
                                                                panel_params, tight_layout_params, 
                                                                fontsizes, font_names, popular_nouns, success_flags)
            del fig, datas, data_save,  axes_from_loop, axes_save, \
                        cbar_axes_save, cbars, plot_data_all, plot_data
            gc.collect()
            data_save = create_data_save_dict()
            continue

        # 2. Check if titles or x/y axis labels are running off the page     
        font_params, xlabels_pull, ylabels_pull, \
            titles_pull, rng_dict, reset_all, remake_plot = check_labels_titles_off_page(datas, 
                                                                                        font_params, 
                                                                                        rng_dict, 
                                                                                        popular_nouns,
                                                                                        xlabels_pull, 
                                                                                        ylabels_pull, 
                                                                                        titles_pull,
                                                                                        fontsizes, font_names,
                                                                                        fontsize_min = fontsize_min, 
                                                                                        verbose=verbose)
        if reset_all:
            plt.close('all')
            if verbose: print('[ERROR]: in checking for titles off page')
            # have to reset everybody
            rng_dict, seeds_dict, figure_params, \
                font_params, xlabels_pull, ylabels_pull, \
                    titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                                                                aspect_fig_params, dpi_params, 
                                                                panel_params, tight_layout_params, 
                                                                fontsizes, font_names, popular_nouns, success_flags)
            del fig, datas, data_save,  axes_from_loop, axes_save, \
                        cbar_axes_save, cbars, plot_data_all, plot_data
            gc.collect()
            data_save = create_data_save_dict()
        if remake_plot:
            if verbose: print('[ERROR]: need to remake plot')
            continue

        # 3. Save the figure, check if issues opening it    
        # check if issue opening plot
        e = ''
        success_reopen = False
        try:
            for iformat in img_format:
                img = np.array(Image.open(fake_figs_dir + 'imgs/Picture_' + str(ifigure+1).zfill(6) + '.' + iformat))
            success_reopen = True
        except Exception as e:
            success_reopen = False
            plt.close('all')
            if verbose: 
                print('[ERROR]: Issue with opening image!')
                if str(e) != '': print('Full error:', str(e))
            # have to reset everybody
            rng_dict, seeds_dict, figure_params, \
                font_params, xlabels_pull, ylabels_pull, \
                    titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                                                                aspect_fig_params, dpi_params, 
                                                                panel_params, tight_layout_params, 
                                                                fontsizes, font_names, popular_nouns, success_flags)
            del fig, datas, data_save,  axes_from_loop, axes_save, \
                        cbar_axes_save, cbars, plot_data_all, plot_data
            gc.collect()
            data_save = create_data_save_dict()
        if not success_reopen:
            continue


        # 4. check if any figure boxes, title boxes, axis label boxes, etc overlap with eachother
        success_boxes, boxes_check, names_overlap = collect_boxes(datas, grace_ticks=grace_ticks)
        # save diagnostics plot
        if save_diagnostic_plot:
            img_diag = np.array(Image.open(fake_figs_dir + 'imgs/Picture_' + str(ifigure+1).zfill(6) + '.' + img_format[0]).convert('RGB'))
            imgplot = add_annotations(img_diag, deepcopy(datas), verbose=False)
            imgplot = Image.fromarray(imgplot).save(fake_figs_dir + 'diags/Picture_' + str(ifigure+1).zfill(6) + '.' + img_format[0])
            if verbose:
                print('saved diagnostic plot:', fake_figs_dir + 'diags/Picture_' + str(ifigure+1).zfill(6) + '.' + img_format[0])
            del imgplot

        if not success_boxes:
            success_plot = False
            if verbose:
                print('[ERROR]: bounding boxes overlap')
            # try making everything smaller
            success_flags, rng_dict, seeds_dict, font_params, \
                popular_nouns, xlabels_pull, ylabels_pull, \
                    titles_pull = update_fonts_boxes_overlap(names_overlap, 
                                                             success_flags, rng_dict, 
                                                             seeds_dict, font_params, figure_params,
                               popular_nouns, xlabels_pull, ylabels_pull, titles_pull,
                               fontsizes, font_names,
                                fontsize_min=fontsize_min)
            gc.collect()
        if not success_boxes:
            continue

        # 5. Check for size of plot(s) within the figure
        success_area, area = check_plot_area(datas)
        if not success_area:
            plt.close('all')
            if verbose: 
                print('[ERROR]: Plot area too small (w/rt figure area), ratio =', area)
                if str(e) != '': print('Full error:', str(e))
            # have to reset everybody
            rng_dict, seeds_dict, figure_params, \
                font_params, xlabels_pull, ylabels_pull, \
                    titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                                                                aspect_fig_params, dpi_params, 
                                                                panel_params, tight_layout_params, 
                                                                fontsizes, font_names, popular_nouns, success_flags)
            del fig, datas, data_save,  axes_from_loop, axes_save, \
                        cbar_axes_save, cbars, plot_data_all, plot_data
            gc.collect()
            data_save = create_data_save_dict()
            continue


        ############################################################
        ############### DONE -- SAVE EVERYTHING ####################
        ############################################################

        # made it to the end -- success!
        success_plot = True
        #import sys; sys.exit()

        if success_plot:
            close_plot_success(fig, datas, ifigure, fake_figs_dir, figure_params, font_params)
            del fig, datas, data_save,  axes_from_loop, axes_save, \
                        cbar_axes_save, cbars, plot_data_all, plot_data, ax
            gc.collect()
            data_save = create_data_save_dict()
            plt.close('all')
            #import sys; sys.exit()
            rng_dict, seeds_dict, figure_params, \
                font_params, xlabels_pull, ylabels_pull, \
                    titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                                                                aspect_fig_params, dpi_params, 
                                                                panel_params, tight_layout_params, 
                                                                fontsizes, font_names, popular_nouns, success_flags)
            

