import os
import matplotlib.pyplot as plt
import pandas as pd
from copy import deepcopy
import numpy as np
from PIL import Image

import warnings
warnings.filterwarnings("error")

from synthetic_training_figures.utils.text_utils import get_popular_nouns, get_inline_math

from synthetic_training_figures.utils.plot_parameters import aspect_fig_params, dpi_params, \
    panel_params, tight_layout_params, base, plot_flip_params, fontsizes, \
        plot_types_params, colorbar_params, ylabel_params
            
from synthetic_training_figures.utils.figure_gen_utils.misc import add_annotations_v1 as add_annotations


# from synthetic_training_figures.utils.plot_parameters import panel_params as panel_params_orig
# from synthetic_training_figures.utils.plot_parameters import title_params as title_params_orig
# from synthetic_training_figures.utils.plot_parameters import xlabel_params as xlabel_params_orig
# from synthetic_training_figures.utils.plot_parameters import ylabel_params as ylabel_params_orig

from synthetic_training_figures.utils.synthetic_fig_utils import get_font_params, normalize_params_prob, add_titles_and_labels, collect_plot_data_axes
#from utils.synthetic_fig_utils import get_titles_or_labels, get_titles_or_labels_ra_dec, normalize_params_prob, get_font_params, add_titles_and_labels, collect_plot_data_axes


#from synthetic_training_figures.utils.tmp_port_from_script import set_figure_params
from synthetic_training_figures.utils.plot_check_utils import set_all_seeds, check_aspect, check_labels_titles_off_page

#from utils.tmp_port_from_script import 
# reset_everybody, make_base_plot, set_figure_params, check_exceptions1, \
#     create_data_save_dict, print_figure_params, close_plot_fail, close_plot_success, get_plot_data, \
#     fill_datas, generate_data, collect_saved_labels, parse_colorbar_data, detect_cb_axes, collect_boxes, \
#     update_fonts_boxes_overlap, check_plot_area, flip_colors

from synthetic_training_figures.utils.tmp_port_from_script import check_exceptions, make_base_plot, \
    close_plot_fail, close_plot_success, get_plot_data, \
    fill_datas, generate_data, collect_saved_labels, parse_colorbar_data, detect_cb_axes, collect_boxes, \
    update_fonts_boxes_overlap, check_plot_area, flip_colors, print_figure_params


###########################################################################
######################### MAIN PLOTTER ########################
###########################################################################

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

#############################################

# debug
# from importlib import reload
# import figure_class
# reload(figure_class)
from .figure_class import FigureRun, reset_figure
## HERE?##
def make_random_plot(figure = None, verbose=True, 
                    fake_figs_dir='./', ifigure=None, 
                    img_format='jpeg', figdraw=True, 
                    timeout=5, aspect_cut = {'min':0.3, 'max':4.0}, grace_ticks=5, 
                    **kwargs):
    """
    timeout: timeout in minutes
    """

    if figure is None: # if none, set by any kwargs
        #figure = FigureRun()
        figure = reset_figure(**kwargs)

    timeout_seconds = timeout*60

    if not isinstance(img_format, list):
        img_format = [img_format]

    
    # # keep titles
    # figure.xlabels_pull = np.stack((np.array(deepcopy(popular_nouns)),) * figure_params['# panels'], axis=0)
    # figure.ylabels_pull = np.stack((np.array(deepcopy(popular_nouns)),) * figure_params['# panels'], axis=0)
    # titles_pull = np.stack((np.array(deepcopy(popular_nouns)),) * figure_params['# panels'], axis=0)

    # if plot_styles is None:
    #     plot_styles = [figure_params['plot style']]
    # if color_maps is None:
    #     color_maps = [figure_params['color map']]

    # font_params = get_font_params(rng_dict, fontsizes, font_names)

    # # for each plot, make data
    # data_save = create_data_save_dict()
    # # try to make data
    # success_plot = False # flag for if we keep running while loop for fig generation
    # success_flags = {'get base plot':False, 'get data for plot':False, 
    #                  'get data from plot':False, 'get titles':False, 'get colorbar titles':False, 
    #                  'get colorbar fonts':True}
    # success_get_base_plot = False # do we need to re-generate figure axes?

    # # for inner loop of tries for a figure
    # itries = 0
    # to start
    fig, datas, imgplot, axes_from_loop, axes_save, \
                       cbar_axes_save, cbars, plot_data_all, plot_data = [None]*9
    # if have font params saved, use them
    # if font_params is not None:
    #     save_font = True
    #     font_params_save = deepcopy(font_params)
    # ------- inner loop -------
    while figure.itries < figure.itriesMax and not figure.success_plot:
        gc.collect()
        if verbose: print(' ------ ON itries:', figure.itries, '----------')
        figure.itries += 1
        if figure.itries >= figure.itriesMax:
            figure.itries = 0
            if verbose: print('RESET EVERYBODY')
            figure.success_plot = False
            plt.close('all')
            # have to reset everybody
            figure = reset_figure(**kwargs)
            # rng_dict, seeds_dict, figure_params, \
            #     font_params, xlabels_pull, ylabels_pull, \
            #         titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
            #                                                     aspect_fig_params, dpi_params, 
            #                                                     panel_params, tight_layout_params, 
            #                                                     fontsizes, font_names, popular_nouns, success_flags)  
            try:
                del fig
            except:
                pass
            try:
                del datas
            except:
                pass
            # try:
            #     del data_save
            # except:
            #     pass
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
            #data_save = create_data_save_dict()
        #if fig is not None:
        try:
            fig
        except:
            fig = None

        # close figure as needed
        close_plot_fail(fig, ifigure, fake_figs_dir, img_format, remove_diags=False, 
                figure_name=figure.figure_name)

        # if save_font:
        #     font_params = deepcopy(font_params_save)
        ################# GET BASIC FIGURE #################
        try:
            if not figure.success_flags['get base plot']:
                gc.collect()
                plt.close('all')
                if verbose:
                    print('  -- generating base fig')
                    print_figure_params(figure.figure_params)
                # make base fig
                fig, axes_save, plot_inds, figsize = make_base_plot(figure.figure_params, verbose=False)
                figure.success_flags['get base plot'] = True
                figure.data_save['figsize'] = figsize
                figure.figure_params['facecolor'] = fig.get_facecolor()
                if figdraw: fig.canvas.draw() # just give it a shot here
                #success_plot = True
        except Exception as e1:
            figure = check_exceptions(e1, figure, **kwargs)
            # success_plot, rng_dict, seeds_dict, figure_params, \
            #     font_params, xlabels_pull, ylabels_pull, \
            #         titles_pull, data_save, \
            #             success_flags = check_exceptions1(e1, fontsizes, 
            #                                             font_names, 
            #                 rng_dict, seeds_dict, figure_params, font_params, 
            #                 xlabels_pull, ylabels_pull, titles_pull, 
            #                 data_save, success_flags,color_maps, plot_styles, 
            #         aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
            #                 verbose = True)  

        if not figure.success_flags['get base plot']: # re do the loop
            continue  

        with warnings.catch_warnings():
            warnings.simplefilter("error", UserWarning)
            if figdraw:
                try:
                    fig.canvas.draw()
                except UserWarning as ew:
                    figure = check_exceptions(ew, figure, **kwargs)

        ################### CREATE DATA, ALL AXES ############  
        err_add = ''    
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)  # e.g., 300 for 5 minutes  
        try:
            # first, get all the data for the plot
            if not figure.success_flags['get data for plot']:
                if verbose: print('  -- generating data for plot')
                plot_data_all = []
                for iplot, ax in enumerate(axes_save):
                    plot_data, err = get_plot_data(figure.plot_params, 
                        figure.rng_dict['inner'], 
                        figure_params=figure.figure_params)
                    if err:
                        del plot_data
                        break
                    plot_data_all.append(deepcopy(plot_data))
                figure.success_flags['get data for plot'] = True
        except TimeoutError as et:
            err = True
            figure = check_exceptions(et,figure, **kwargs)
            # success_plot, rng_dict, seeds_dict, figure_params, \
            # font_params, xlabels_pull, ylabels_pull, \
            #     titles_pull, data_save, \
            #         success_flags = check_exceptions1(et, fontsizes, 
            #                                         font_names, 
            #             rng_dict, seeds_dict, figure_params, font_params, 
            #             xlabels_pull, ylabels_pull, titles_pull, 
            #             data_save, success_flags,color_maps, plot_styles, 
            #     aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
            #             verbose = True) 
        except Exception as e2:
                err = True
                err_add = str(e2)
        finally:
            signal.alarm(0)

        if err: # either via exception or not
            figure.success_flags['get data for plot'] = False
            figure.success_plot = False
            plt.close('all')
            # have to reset everybody
            figure = reset_figure(**kwargs)
            # rng_dict, seeds_dict, figure_params, \
            #     font_params, xlabels_pull, ylabels_pull, \
            #         titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
            #                                                     aspect_fig_params, dpi_params, 
            #                                                     panel_params, tight_layout_params, 
            #                                                     fontsizes, font_names, popular_nouns, success_flags)
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
            # try:
            #     del data_save
            # except:
            #     pass
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
            #figure.data_save = create_data_save_dict()
            if verbose:
                print('[ERROR]: in getting data, will reset and try again.')  
                if len(err_add) > 0:
                        print('  -- added error:', err_add)    
        if not figure.success_flags['get data for plot']:
            continue    


        ############# GET DATA FROM PLOT, ALL AXES ###########  
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)  # e.g., 300 for 5 minutes  
        err_full = False                                 
        try:
            if not figure.success_flags['get data from plot']:
                if verbose: print('  -- getting data *from* plot')
                axes_from_loop = []
                for iplot, ax in enumerate(axes_save):
                    # get data for this plot
                    plot_data = plot_data_all[iplot]
                    # create axes and plot data
                    result = generate_data(fig, iplot, figure.figure_params, plot_data, 
                                                    figure.rng_dict['inner'], verbose=False)
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
                    figure.data_save['data_for_plots'].append(deepcopy(plot_data['data_for_plot']))
                    figure.data_save['plot_types'].append(deepcopy(plot_data['plot_type']))
                    figure.data_save['data_from_plots'].append(generated_data['data_from_plot'])                    
                    figure.data_save['distribution_types'].append(deepcopy(plot_data['distribution_type']))
            if figdraw: fig.canvas.draw() # try again here
            if not err_full:
                figure.success_flags['get data from plot'] = True
        except TimeoutError as et:
            figure = check_exceptions(et,figure, **kwargs)
            # success_plot, rng_dict, seeds_dict, figure_params, \
            # font_params, xlabels_pull, ylabels_pull, \
            #     titles_pull, data_save, \
            #         success_flags = check_exceptions1(et, fontsizes, 
            #                                         font_names, 
            #             rng_dict, seeds_dict, figure_params, font_params, 
            #             xlabels_pull, ylabels_pull, titles_pull, 
            #             data_save, success_flags,color_maps, plot_styles, 
            #     aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
            #             verbose = True)          
        except Exception as e3:   
            figure = check_exceptions(e3,figure, **kwargs)
            # success_plot, rng_dict, seeds_dict, figure_params, \
            # font_params, xlabels_pull, ylabels_pull, \
            #     titles_pull, data_save, \
            #         success_flags = check_exceptions1(e3, fontsizes, 
            #                                         font_names, 
            #             rng_dict, seeds_dict, figure_params, font_params, 
            #             xlabels_pull, ylabels_pull, titles_pull, 
            #             data_save, success_flags,color_maps, plot_styles, 
            #     aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
            #             verbose = True)
        finally:
            signal.alarm(0)

        if not figure.success_flags['get data from plot']:
            continue   

        ################# SET TITLES AND AXIS LABELS ##############
        # try:
        #     if not figure.success_flags['get titles']:
        #         if verbose: print('  -- generating titles and axis labels')
        #         xp,yp,tp = [],[],[]
        #         xpt,ypt,tpt = [],[],[]
        #         for iplot, ax in enumerate(axes_from_loop):
        #             # get data for this plot
        #             plot_data = plot_data_all[iplot]
        #             success_loop_labels = False
        #             itries_labels = 0
        #             while not success_loop_labels and itries_labels <= figure.itriesMax:
        #                 gc.collect()
        #                 itries_labels +=1
        #                 title, xlabel, ylabel = add_titles_and_labels(plot_data['plot_type'], plot_data['plot_params_here_ax'], 
        #                                                         plot_data['data_for_plot'],
        #                                                         ax, xlabels_pull[iplot], ylabels_pull[iplot], 
        #                                                         titles_pull[iplot], inlines,
        #                                                     title_params, xlabel_params, ylabel_params, font_params, 
        #                                                     rng=rng_dict['titles'])
            
        #                 xlabels_pull2, ylabels_pull2, titles_pull2, err = collect_saved_labels(xlabel, ylabel, title)

        #                 if err: # issue getting labels, pull again
        #                     del title, xlabel, ylabel
        #                     continue
        #                 xp.append(xlabels_pull2); yp.append(ylabels_pull2); tp.append(titles_pull2)
        #                 xpt.append(xlabel); ypt.append(ylabel); tpt.append(title)
        #                 success_loop_labels = True
        #         if not success_loop_labels or itries_labels >= figure.itriesMax:
        #             figure.success_flags['get titles'] = False
        #             success_plot = False
        #             plt.close('all')
        #             # have to reset everybody
        #             figure = FigureRun()
        #             # rng_dict, seeds_dict, figure_params, \
        #             #     font_params, xlabels_pull, ylabels_pull, \
        #             #         titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
        #             #                                                 aspect_fig_params, dpi_params, 
        #             #                                                 panel_params, tight_layout_params, 
        #             #                                                 fontsizes, font_names, popular_nouns, success_flags)
        #             # del fig, datas, data_save,  axes_from_loop, axes_save, \
        #             #     cbar_axes_save, cbars, plot_data_all, plot_data
        #             gc.collect()
        #             #data_save = create_data_save_dict()
        #         else: # all is well so far!
        #             try:
        #                 if figdraw: fig.canvas.draw() # try again
        #                 figure.data_save['titles'] = tpt
        #                 figure.data_save['xlabels'] = xpt
        #                 figure.data_save['ylabels'] = ypt
        #                 fontcolor = xpt[0].get_color()
        #                 xlabels_pull = deepcopy(xp)
        #                 ylabels_pull = deepcopy(yp)
        #                 titles_pull = deepcopy(tp) 
        #                 success_flags['get titles'] = True  
        #             except Exception as e44:   
        #                 figure = check_exceptions(e44,figure,verbose=True)
        #             #         success_plot, rng_dict, seeds_dict, figure_params, \
        #             #         font_params, xlabels_pull, ylabels_pull, \
        #             #             titles_pull, data_save, \
        #             #                 success_flags = check_exceptions1(e44, fontsizes, 
        #             #                                                 font_names, 
        #             #                     rng_dict, seeds_dict, figure_params, font_params, 
        #             #                     xlabels_pull, ylabels_pull, titles_pull, 
        #             #                     data_save, success_flags,color_maps, plot_styles, 
        #             # aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
        #             #                     verbose = True)
        #             #print('  *** titles, xlabels, ylabels:', tpt, xpt, ypt)
        # except Exception as e4:  
        #     figure = check_exceptions(e4,figure,verbose=True) 
        #         # success_plot, rng_dict, seeds_dict, figure_params, \
        #         # font_params, xlabels_pull, ylabels_pull, \
        #         #     titles_pull, data_save, \
        #         #         success_flags = check_exceptions1(e4, fontsizes, 
        #         #                                         font_names, 
        #         #             rng_dict, seeds_dict, figure_params, font_params, 
        #         #             xlabels_pull, ylabels_pull, titles_pull, 
        #         #             data_save, success_flags,color_maps, plot_styles, 
        #         #     aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
        #         #             verbose = True)
        # if not figure.success_flags['get titles']:
        #     continue

        ################# SET TITLES AND AXIS LABELS ##############
        try:
            if not figure.success_flags['get titles']:
                if verbose: print('  -- generating titles and axis labels')
                xp,yp,tp = [],[],[]
                xpt,ypt,tpt = [],[],[]
                for iplot, ax in enumerate(axes_from_loop):
                    # get data for this plot
                    plot_data = plot_data_all[iplot]
                    success_loop_labels = False
                    itries_labels = 0
                    while not success_loop_labels and itries_labels <= figure.itriesMax:
                        gc.collect()
                        itries_labels +=1
                        # title, xlabel, ylabel = add_titles_and_labels(plot_data['plot_type'], plot_data['plot_params_here_ax'], 
                        #                                         plot_data['data_for_plot'],
                        #                                         ax, xlabels_pull[iplot], ylabels_pull[iplot], 
                        #                                         titles_pull[iplot], inlines,
                        #                                     title_params, xlabel_params, ylabel_params, font_params, 
                        #                                     rng=rng_dict['titles'])
                        title, xlabel, ylabel = add_titles_and_labels(figure, plot_data, ax, iplot)
            
                        xlabels_pull2, ylabels_pull2, titles_pull2, err = collect_saved_labels(xlabel, ylabel, title)

                        if err: # issue getting labels, pull again
                            del title, xlabel, ylabel
                            continue
                        xp.append(xlabels_pull2); yp.append(ylabels_pull2); tp.append(titles_pull2)
                        xpt.append(xlabel); ypt.append(ylabel); tpt.append(title)
                        success_loop_labels = True
                if not success_loop_labels or itries_labels >= figure.itriesMax:
                    figure.success_flags['get titles'] = False
                    figure.success_plot = False
                    plt.close('all')
                    # have to reset everybody
                    #figure = FigureRun()
                    figure = reset_figure(**kwargs)
                    # rng_dict, seeds_dict, figure_params, \
                    #     font_params, xlabels_pull, ylabels_pull, \
                    #         titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                    #                                                 aspect_fig_params, dpi_params, 
                    #                                                 panel_params, tight_layout_params, 
                    #                                                 fontsizes, font_names, popular_nouns, success_flags)
                    # del fig, datas, data_save,  axes_from_loop, axes_save, \
                    #     cbar_axes_save, cbars, plot_data_all, plot_data
                    gc.collect()
                    #data_save = create_data_save_dict()
                    try:
                        del fig
                        del datas
                        del axes_from_loop
                    except:
                        pass
                else: # all is well so far!
                    try:
                        if figdraw: fig.canvas.draw() # try again
                        figure.data_save['titles'] = tpt
                        figure.data_save['xlabels'] = xpt
                        figure.data_save['ylabels'] = ypt
                        fontcolor = xpt[0].get_color()
                        figure.xlabels_pull = deepcopy(xp)
                        figure.ylabels_pull = deepcopy(yp)
                        figure.titles_pull = deepcopy(tp) 
                        figure.success_flags['get titles'] = True  
                    except Exception as e44:   
                        figure = check_exceptions(e44,figure, **kwargs)
                    #         success_plot, rng_dict, seeds_dict, figure_params, \
                    #         font_params, xlabels_pull, ylabels_pull, \
                    #             titles_pull, data_save, \
                    #                 success_flags = check_exceptions1(e44, fontsizes, 
                    #                                                 font_names, 
                    #                     rng_dict, seeds_dict, figure_params, font_params, 
                    #                     xlabels_pull, ylabels_pull, titles_pull, 
                    #                     data_save, success_flags,color_maps, plot_styles, 
                    # aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
                    #                     verbose = True)
        except Exception as e4:   
            figure = check_exceptions(e4, figure, **kwargs)
                # success_plot, rng_dict, seeds_dict, figure_params, \
                # font_params, xlabels_pull, ylabels_pull, \
                #     titles_pull, data_save, \
                #         success_flags = check_exceptions1(e4, fontsizes, 
                #                                         font_names, 
                #             rng_dict, seeds_dict, figure_params, font_params, 
                #             xlabels_pull, ylabels_pull, titles_pull, 
                #             data_save, success_flags,color_maps, plot_styles, 
                #     aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
                #             verbose = True)
        if not figure.success_flags['get titles']:
            continue


        #import sys; sys.exit()
        # get fontcolor
        figure.figure_params['fontcolor'] = fontcolor
        
        ############# GET COLOR BARS ##############
        try:
            # get colorbar stuff for each plot
            if not figure.success_flags['get colorbar titles']:
                cbar_words_list = figure.popular_nouns
                cbar_inlines = figure.inlines
                cbar_nums = []; cbar_words = []; cbars = []
                for iplot, ax in enumerate(axes_from_loop):
                    #**HERE**
                    # cbar, colorbar_words = parse_colorbar_data(data_save['plot_types'][iplot],  
                    #                                     data_save['data_from_plots'][iplot], 
                    #                                     fig, rng_dict['inner'], 
                    #                                     font_params, title_params,colorbar_params,
                    #                                     data_save['data_for_plots'][iplot],
                    #                                     popular_nouns=cbar_words_list,
                    #                                     inlines=cbar_inlines)
                    cbar, colorbar_words = parse_colorbar_data(figure,fig, iplot,
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
                figure.success_flags['get colorbar titles'] = True
                figure.data_save['cbars'] = cbars
                figure.data_save['cbar_words'] = deepcopy(cbar_words)
                figure.data_save['cbar_nums'] = deepcopy(cbar_nums)
        except Exception as ec:
            figure.success_plot = False
            figure.success_flags['get colorbar titles'] = False
            figure = check_exceptions(ec, figure, error_front=' in parse_colorbar_data -- ', **kwargs)
            # success_plot, rng_dict, seeds_dict, figure_params, \
            #     font_params, xlabels_pull, ylabels_pull, \
            #         titles_pull, data_save, \
            #             success_flags = check_exceptions1(ec, fontsizes, 
            #                                             font_names, 
            #                 rng_dict, seeds_dict, figure_params, font_params, 
            #                 xlabels_pull, ylabels_pull, titles_pull, 
            #                 data_save, success_flags,color_maps, plot_styles, 
            #         aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
            #                 verbose = True, error_front=' in parse_colorbar_data -- ')                    
        if not figure.success_flags['get colorbar titles']:
            continue


        ############# SET FINAL COLORS ###########
        plt.set_cmap(figure.figure_params['color map'])
        plt.style.use(figure.figure_params['plot style'])
        plt.rcParams['font.family'] = str(figure.font_params['csfont']['fontname'])
        f2 = fig.get_facecolor()
        figure.success_flip = False
        # flip?
        if figure.figure_params['flipped font/face colors']:
            #fig, facecolor, fontcolor, cbarsout = flip_colors(fig, data_save, figure_params, axes_from_loop)
            fig, facecolor, fontcolor, cbarsout = flip_colors(fig, figure, axes_from_loop)
            figure.figure_params['fontcolor'] = fontcolor
            figure.figure_params['facecolor'] = facecolor
        else:
            cbarsout = figure.data_save['cbars']
        try:
            fig.canvas.draw()
            figure.data_save['cbars'] = cbarsout
            figure.success_flip = True
        except Exception as ec11:
            figure.success_flip = False
            # success_plot, rng_dict, seeds_dict, figure_params, \
            #     font_params, xlabels_pull, ylabels_pull, \
            #         titles_pull, data_save, \
            #             success_flags = check_exceptions1(ec11, fontsizes, 
            #                                             font_names, 
            #                 rng_dict, seeds_dict, figure_params, font_params, 
            #                 xlabels_pull, ylabels_pull, titles_pull, 
            #                 data_save, success_flags,color_maps, plot_styles, 
            #         aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
            #                 verbose = True, error_front=' in fliping colors -- ')
            figure = check_exceptions(ec11, figure, error_front=' in flipping colors -- ', **kwargs)

        if not figure.success_flip:
            continue


        ##############################################     
        ########## END OF TRYING TO MAKE PLOT ########
        ##############################################

        # import sys; sys.exit()

        ####### SAVE DATA #########
        # if we've made it thus far, lets collect all the data
        success_fill_data = False
        try:
            #datas, width, height = fill_datas(fig, figure_params, font_params, plot_inds)
            datas, width, height = fill_datas(fig, figure, plot_inds)
            success_fill_data = True
        except Exception as e_fill_data1:
            success_fill_data = False
            if 'Tight layout not applied' in str(e_fill_data1): # issue with tight layout, redo
                if verbose: print('[ERROR]: tight layout not applied, take 2 - ', str(e_fill_data1))
                #success_plot = False
                plt.close('all')
                #figure = FigureRun()
                figure = reset_figure(**kwargs)
                # # have to reset everybody
                # rng_dict, seeds_dict, figure_params, \
                #     font_params, xlabels_pull, ylabels_pull, \
                #         titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                #                                                  aspect_fig_params, dpi_params, 
                #                                                  panel_params, tight_layout_params, 
                #                                                  fontsizes, font_names, popular_nouns, success_flags)  
            else:   
                if verbose: print('[ERROR]: in getting data from plot - ', str(e_fill_data1))
                plt.close('all')
                #figure.success_plot = False
                # have to reset everybody
                #figure = FigureRun()
                figure = reset_figure(**kwargs)
                # rng_dict, seeds_dict, figure_params, \
                #     font_params, xlabels_pull, ylabels_pull, \
                #         titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                #                                                  aspect_fig_params, dpi_params, 
                #                                                  panel_params, tight_layout_params, 
                #                                                  fontsizes, font_names, popular_nouns, success_flags)  
                # del fig, datas, data_save,  axes_from_loop, axes_save, \
                #         cbar_axes_save, cbars, plot_data_all, plot_data
                # del fig, datas, data_save,  axes_from_loop, axes_save, \
                #         cbar_axes_save, cbars, plot_data_all, plot_data
                try:
                    del fig
                    del datas
                    del axes_from_loop
                    del axes_save
                except:
                    pass
                gc.collect()
                #data_save = create_data_save_dict()
        if not success_fill_data:    
            continue   


        # which are axis and which are not?
        axes_save, cbar_axes_save, err = detect_cb_axes(fig, figure.data_save['cbar_nums'])
        if err:
            plt.close('all')
            #figure = FigureRun()
            figure = reset_figure(**kwargs)
            # success_plot = False
            # # have to reset everybody
            # rng_dict, seeds_dict, figure_params, \
            #     font_params, xlabels_pull, ylabels_pull, \
            #         titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
            #                                                     aspect_fig_params, dpi_params, 
            #                                                     panel_params, tight_layout_params, 
            #                                                     fontsizes, font_names, popular_nouns, success_flags) 
            # del fig, datas, data_save,  axes_from_loop, axes_save, \
            #             cbar_axes_save, cbars, plot_data_all, plot_data
            try:
                del fig
                del datas
                del axes_from_loop
                del plot_data
            except:
                pass
            gc.collect()
            #data_save = create_data_save_dict()
            continue


        # save the fig
        success_save = False
        try:
            for iformat in img_format:
                fig.tight_layout(h_pad=figure.figure_params['layout h_pad'], w_pad=figure.figure_params['layout w_pad'], pad=figure.figure_params['layout pad'])
                figure_name = figure.figure_name
                if figure_name is None:
                    figure_name = 'Picture_' + str(ifigure+1).zfill(6)
                fig.savefig(fake_figs_dir + 'imgs/' +figure_name+ '.'+iformat, 
                            dpi=figure.figure_params['dpi'], facecolor=figure.figure_params['facecolor'])
                if verbose: print('saved:', fake_figs_dir + 'imgs/' + figure_name + '.' +iformat)
            success_save = True
        except Exception as esave:
            success_save = False
            figure = check_exceptions(esave, figure, error_front=' saving figure failed -- ', **kwargs)

            # success_plot, rng_dict, seeds_dict, figure_params, \
            #     font_params, xlabels_pull, ylabels_pull, \
            #         titles_pull, data_save, \
            #             success_flags = check_exceptions1(esave, fontsizes, 
            #                                             font_names, 
            #                 rng_dict, seeds_dict, figure_params, font_params, 
            #                 xlabels_pull, ylabels_pull, titles_pull, 
            #                 data_save, success_flags,color_maps, plot_styles, 
            #         aspect_fig_params, dpi_params, panel_params, tight_layout_params,popular_nouns,
            #                 verbose = True, error_front=' saving figure failed -- ')

        if not success_save:
            continue


        # Save the data from the fig and for the fig
        success_fill_data = False
        try:
            for iplot, (ax,cbar_ax) in enumerate(zip(axes_save,cbar_axes_save)): ### XYZ, only 1 axis here
                datas['plot' + str(iplot)], err = collect_plot_data_axes(ax, fig, 
                                figure, iplot, 
                                height, width,
                                cbar_ax=cbar_ax,
                                colorbar_verbose=False,
                                verbose=True)
                # datas['plot' + str(iplot)], err = collect_plot_data_axes(ax, fig,
                #                 height, width,
                #                 data_save['data_from_plots'][iplot], 
                #                 data_save['data_for_plots'][iplot], 
                #                 data_save['plot_types'][iplot], data_save['titles'][iplot], 
                #                 data_save['xlabels'][iplot], data_save['ylabels'][iplot],
                #                 data_save['distribution_types'][iplot], cbar_ax=cbar_ax,
                #                 colorbar_verbose=False,
                #                 verbose=True)#, error_out=False)
            # one extra
            datas['figure']['figsize'] = figure.data_save['figsize']
            datas['figure']['facecolor'] = figure.figure_params['facecolor']
            if not err: 
                success_fill_data = True
                if verbose: print('  -- filled "datas" with to/from plot')
            else: # no idea, reset everybody
                #laksjflasj
                success_fill_data = False
                plt.close('all')
                # have to reset everybody
                #figure = FigureRun()
                figure = reset_figure(**kwargs)
                # rng_dict, seeds_dict, figure_params, \
                #     font_params, xlabels_pull, ylabels_pull, \
                #         titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                #                                                  aspect_fig_params, dpi_params, 
                #                                                  panel_params, tight_layout_params, 
                #                                                  fontsizes, font_names, popular_nouns, success_flags)
                # del fig, datas, data_save,  axes_from_loop, axes_save, \
                #         cbar_axes_save, cbars, plot_data_all, plot_data
                try:
                    del fig
                    del datas
                    del axes_from_loop
                except:
                    pass
                gc.collect()
                #data_save = create_data_save_dict()
        except Exception as e_fill_data:
            laskjfal
            success_fill_data = False
            if verbose:
                print('[ERROR] 2: ' + str(e_fill_data))
            if 'Glyph' in str(e_fill_data) and 'missing' in str(e_fill_data): # missing a glyph, try different font
                _, _, _, _, _, _, csfont = get_font_info(fontsizes, figure.font_names, rng=figure.rng_dict['font'])
                figure.font_params['csfont'] = csfont
                figure.success_flags['get titles'] = False
            else: # no idea! reset everybody
                # have to reset everybody
                plt.close('all')
                #figure = FigureRun()
                figure = reset_figure(**kwargs)
                # rng_dict, seeds_dict, figure_params, \
                #     font_params, xlabels_pull, ylabels_pull, \
                #         titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
                #                                                  aspect_fig_params, dpi_params, 
                #                                                  panel_params, tight_layout_params, 
                #                                                  fontsizes, font_names, popular_nouns, success_flags)
                # del fig, datas, data_save,  axes_from_loop, axes_save, \
                #         cbar_axes_save, cbars, plot_data_all, plot_data
                try:
                    del fig
                    del datas
                    del axes_from_loop
                except:
                    pass
                gc.collect()
                #data_save = create_data_save_dict()
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
            #figure = FigureRun()
            figure = reset_figure(**kwargs)
            # rng_dict, seeds_dict, figure_params, \
            #     font_params, xlabels_pull, ylabels_pull, \
            #         titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
            #                                                     aspect_fig_params, dpi_params, 
            #                                                     panel_params, tight_layout_params, 
            #                                                     fontsizes, font_names, popular_nouns, success_flags)
            # del fig, datas, data_save,  axes_from_loop, axes_save, \
            #             cbar_axes_save, cbars, plot_data_all, plot_data
            gc.collect()
            #data_save = create_data_save_dict()
            try:
                del fig
                del datas
                del axes_from_loop
            except:
                pass
            continue

        # 2. Check if titles or x/y axis labels are running off the page     
        # font_params, xlabels_pull, ylabels_pull, \
        #     titles_pull, rng_dict, reset_all, remake_plot = check_labels_titles_off_page(datas, 
        #                                                                                 font_params, 
        #                                                                                 rng_dict, 
        #                                                                                 popular_nouns,
        #                                                                                 xlabels_pull, 
        #                                                                                 ylabels_pull, 
        #                                                                                 titles_pull,
        #                                                                                 fontsizes, font_names,
        #                                                                                 fontsize_min = fontsize_min, 
        #                                                                                 verbose=verbose)
        figure, reset_all, remake_plot = check_labels_titles_off_page(datas, figure,
                                                                        fontsizes,
                                                                        fontsize_min = fontsizes['fontsize min'], 
                                                                        verbose=verbose)
        if reset_all:
            plt.close('all')
            if verbose: print('[ERROR]: in checking for titles off page')
            # have to reset everybody
            #figure = FigureRun()
            figure = reset_figure(**kwargs)
            # rng_dict, seeds_dict, figure_params, \
            #     font_params, xlabels_pull, ylabels_pull, \
            #         titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
            #                                                     aspect_fig_params, dpi_params, 
            #                                                     panel_params, tight_layout_params, 
            #                                                     fontsizes, font_names, popular_nouns, success_flags)
            # del fig, datas, data_save,  axes_from_loop, axes_save, \
            #             cbar_axes_save, cbars, plot_data_all, plot_data
            try:
                del fig
                del datas
                del axes_from_loop
            except:
                pass
            gc.collect()
            #data_save = create_data_save_dict()
        if remake_plot:
            if verbose: print('[ERROR]: need to remake plot')
            continue


        # 3. Save the figure, check if issues opening it    
        # check if issue opening plot
        e = ''
        success_reopen = False
        try:
            for iformat in img_format:
                #img = np.array(Image.open(fake_figs_dir + 'imgs/Picture_' + str(ifigure+1).zfill(6) + '.' + iformat))
                img = np.array(Image.open(fake_figs_dir + 'imgs/' + figure_name + '.' + iformat))
            success_reopen = True
        except Exception as e:
            success_reopen = False
            plt.close('all')
            if verbose: 
                print('[ERROR]: Issue with opening image!')
                if str(e) != '': print('Full error:', str(e))
            # have to reset everybody
            #figure = FigureRun()
            figure = reset_figure(**kwargs)
            # rng_dict, seeds_dict, figure_params, \
            #     font_params, xlabels_pull, ylabels_pull, \
            #         titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
            #                                                     aspect_fig_params, dpi_params, 
            #                                                     panel_params, tight_layout_params, 
            #                                                     fontsizes, font_names, popular_nouns, success_flags)
            # del fig, datas, data_save,  axes_from_loop, axes_save, \
            #             cbar_axes_save, cbars, plot_data_all, plot_data
            gc.collect()
            #data_save = create_data_save_dict()
            try:
                del fig
                del datas
                del axes_from_loop
            except:
                pass
        if not success_reopen:
            continue


        # 4. check if any figure boxes, title boxes, axis label boxes, etc overlap with eachother
        success_boxes, boxes_check, names_overlap = collect_boxes(datas, grace_ticks=grace_ticks)
        fignamesout = {}
        #fignamesout['figure'] = fake_figs_dir + 'imgs/Picture_' + str(ifigure+1).zfill(6) + '.' + img_format[0]
        fignamesout['figure'] = fake_figs_dir + 'imgs/' + figure_name + '.' + img_format[0]
        # save diagnostics plot
        if figure.save_diagnostic_plot:
            #img_diag = np.array(Image.open(fake_figs_dir + 'imgs/Picture_' + str(ifigure+1).zfill(6) + '.' + img_format[0]).convert('RGB'))
            img_diag = np.array(Image.open(fake_figs_dir + 'imgs/' + figure_name + '.' + img_format[0]).convert('RGB'))
            imgplot = add_annotations(img_diag, deepcopy(datas), verbose=False)
            #imgplot = Image.fromarray(imgplot).save(fake_figs_dir + 'diags/Picture_' + str(ifigure+1).zfill(6) + '.' + img_format[0])
            imgplot = Image.fromarray(imgplot).save(fake_figs_dir + 'diags/' + figure_name + '.' + img_format[0])
            if verbose:
                #print('saved diagnostic plot:', fake_figs_dir + 'diags/Picture_' + str(ifigure+1).zfill(6) + '.' + img_format[0])
                print('saved diagnostic plot:', fake_figs_dir + 'diags/' + figure_name + '.' + img_format[0])
            del imgplot
            fignamesout['diagnostic'] = fake_figs_dir + 'diags/' + figure_name + '.' + img_format[0]


        if not success_boxes:
            figure.success_plot = False
            if verbose:
                print('[ERROR]: bounding boxes overlap')
            # try making everything smaller
            # success_flags, rng_dict, seeds_dict, font_params, \
            #     popular_nouns, xlabels_pull, ylabels_pull, \
            #         titles_pull = update_fonts_boxes_overlap(names_overlap, 
            #                                                  success_flags, rng_dict, 
            #                                                  seeds_dict, font_params, figure_params,
            #                    popular_nouns, xlabels_pull, ylabels_pull, titles_pull,
            #                    fontsizes, font_names,
            #                     fontsize_min=fontsize_min)
            figure = update_fonts_boxes_overlap(names_overlap,figure,
                               fontsizes,
                                fontsize_min=fontsizes['fontsize min'])
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
            #figure = FigureRun()
            figure = reset_figure(**kwargs)
            # rng_dict, seeds_dict, figure_params, \
            #     font_params, xlabels_pull, ylabels_pull, \
            #         titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
            #                                                     aspect_fig_params, dpi_params, 
            #                                                     panel_params, tight_layout_params, 
            #                                                     fontsizes, font_names, popular_nouns, success_flags)
            # del fig, datas, data_save,  axes_from_loop, axes_save, \
            #             cbar_axes_save, cbars, plot_data_all, plot_data
            gc.collect()
            #data_save = create_data_save_dict()
            try:
                del fig
                del datas
                del axes_from_loop
            except:
                pass
            continue


        ############################################################
        ############### DONE -- SAVE EVERYTHING ####################
        ############################################################

        # made it to the end -- success!
        figure.success_plot = True
        #import sys; sys.exit()

        diagsout = {'success': True} # whatelse to save??

        if figure.success_plot:
            dirsout = close_plot_success(fig, datas, ifigure, fake_figs_dir, figure.figure_params, figure.font_params, 
                                        return_dirs=True, figure_name=figure.figure_name)
            for k,v in dirsout.items():
                fignamesout[k] = v
            # del fig, datas, data_save,  axes_from_loop, axes_save, \
            #             cbar_axes_save, cbars, plot_data_all, plot_data, ax
            try:
                del fig
                del datas
                del axes_from_loop
                del axes_save
                del cbar_axes_save
                del cbars
                del plot_data_all
                del plot_data
                del ax
            except:
                pass
            gc.collect()
            #data_save = create_data_save_dict()
            plt.close('all')
            #import sys; sys.exit()
            # rng_dict, seeds_dict, figure_params, \
            #     font_params, xlabels_pull, ylabels_pull, \
            #         titles_pull, data_save, success_flags = reset_everybody(color_maps, plot_styles, 
            #                                                     aspect_fig_params, dpi_params, 
            #                                                     panel_params, tight_layout_params, 
            #                                                     fontsizes, font_names, popular_nouns, success_flags)
            #figure = FigureRun()
            figure = reset_figure(**kwargs)


            return diagsout
