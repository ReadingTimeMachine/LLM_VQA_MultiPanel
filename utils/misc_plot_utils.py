import os
from copy import deepcopy
import pandas as pd

from synthetic_training_figures.utils.plot_parameters import panel_params as panel_params_orig
from synthetic_training_figures.utils.plot_parameters import title_params as title_params_orig
from synthetic_training_figures.utils.plot_parameters import xlabel_params as xlabel_params_orig
from synthetic_training_figures.utils.plot_parameters import ylabel_params as ylabel_params_orig
from synthetic_training_figures.utils.plot_parameters import colorbar_params as colorbar_params_orig

from synthetic_training_figures.utils.plot_parameters import plot_types_params

from synthetic_training_figures.utils.synthetic_fig_utils import normalize_params_prob


def make_plotplotparams(fullproc_r = "~/ArXiv_figure_injection/resources/", 
                        astroquery_img_dir="~/Dropbox/wwt_image_extraction/FullProcess_resources/astroquery_images/"):
    """
    This basically is a holder for setting all of the basic plot 
    parameters for plot generation.  This sets panel parameters, 
    title parameters, x/ylabel params, colorbar params, linestyles.
    """
    fullproc_r = os.path.expanduser(fullproc_r)
    astroquery_img_dir = os.path.expanduser(astroquery_img_dir)
    ############## PLOT PARAMS ###################

    plot_params = deepcopy(plot_types_params)
    panel_params = deepcopy(panel_params_orig)
    title_params = deepcopy(title_params_orig)
    xlabel_params = deepcopy(xlabel_params_orig)
    ylabel_params = deepcopy(ylabel_params_orig)
    colorbar_params = deepcopy(colorbar_params_orig)

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

    ### normalize everybody
    plot_params_line, panel_params, \
    title_params, xlabel_params, \
    ylabel_params = normalize_params_prob(plot_params_line.copy(), panel_params, 
                                            title_params, xlabel_params, 
                                            ylabel_params, colorbar_params, 
                                            verbose=False)
    #### get fonts #####
    # check that location is there
    drop_names = []
    dfont = pd.read_csv(fullproc_r + 'fonts.csv')
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

    return plot_params_line, panel_params, title_params, xlabel_params, \
        ylabel_params, colorbar_params, linestyles_hist, linestyles, font_names