import os
import matplotlib.pyplot as plt
import pandas as pd
from copy import deepcopy
import numpy as np

from synthetic_training_figures.utils.text_utils import get_popular_nouns, get_inline_math

from synthetic_training_figures.utils.plot_parameters import aspect_fig_params, dpi_params, \
    panel_params, tight_layout_params, base, plot_flip_params, fontsizes, \
        plot_types_params, colorbar_params, ylabel_params
            

from .misc_plot_utils import make_plotplotparams

from synthetic_training_figures.utils.synthetic_fig_utils import get_font_params, normalize_params_prob


from synthetic_training_figures.utils.tmp_port_from_script import set_figure_params
from synthetic_training_figures.utils.plot_check_utils import set_all_seeds


tight_layout_params = {'prob':1.0, # prob of tight layout
                       'pad':{'min':0.0, 'max':0.1}, 
                       'w_pad':{'min':0.0, 'max':0.1}, 
                       'h_pad':{'min':0.0, 'max':0.1}
                       }






def get_aspects(d): 
    """ 
    d : one row representing 1 article page
    """
    aspects = {}
    img_size = d['page size']
    for b, v in d['boxes'].items(): # each figure
        #hasSubfigs = False
        aspects[b] = {}
        w = np.abs(v['xmax']-v['xmin'])
        h = np.abs(v['ymax']-v['ymin'])
        aspects[b]['fw'] = w/img_size[1]
        aspects[b]['fh'] = h/img_size[0]
        sx = np.abs(d['shift-x']); sy = np.abs(d['shift-y'])
        shift = np.sqrt(sx**2 + sy**2)
        aspects[b]['shift'] = shift
        w = np.abs(v['xmax']-v['xmin'])
        h = np.abs(v['ymax']-v['ymin'])
        aspects[b]['aspect ratio'] = w/h
        if 'subfig 0' in v: # have a subfig
            for bb,vv in v.items():
                if 'subfig ' in bb:
                    w = np.abs(vv['xmax']-vv['xmin'])
                    h = np.abs(vv['ymax']-vv['ymin'])
                    aspects[b][bb + ' aspect ratio'] = w/h
        else:
            pass

    return aspects


from scipy.cluster.hierarchy import fclusterdata
from sklearn.cluster import DBSCAN

def organize_boxes_into_grid(boxes, row_eps=None, col_eps=None):
    """
    Organize bounding boxes into rows and columns using DBSCAN clustering.
    More robust to small coordinate variations.
    """
    boxes = np.array(boxes)
    
    # Ensure consistent coordinate system
    boxes_normalized = boxes.copy()
    boxes_normalized[:, [1, 3]] = np.sort(boxes[:, [1, 3]], axis=1)
    boxes_normalized[:, [0, 2]] = np.sort(boxes[:, [0, 2]], axis=1)
    
    # Calculate centers
    centers = np.column_stack([
        (boxes_normalized[:, 0] + boxes_normalized[:, 2]) / 2,
        (boxes_normalized[:, 1] + boxes_normalized[:, 3]) / 2
    ])
    
    # Auto-detect eps for rows (y-coordinate)
    if row_eps is None:
        box_heights = np.abs(boxes[:, 3] - boxes[:, 1])
        row_eps = np.mean(box_heights) * 0.2  # 20% of average box height
    
    # Cluster rows
    row_clusterer = DBSCAN(eps=row_eps, min_samples=1)
    row_labels = row_clusterer.fit_predict(centers[:, 1].reshape(-1, 1))
    
    # Sort row labels by y-position
    unique_rows = np.unique(row_labels)
    row_positions = [np.mean(centers[row_labels == r, 1]) for r in unique_rows]
    row_mapping = {old: new for new, old in enumerate(np.argsort(row_positions))}
    rows = np.array([row_mapping[r] for r in row_labels])
    
    # Auto-detect eps for columns (x-coordinate)
    if col_eps is None:
        box_widths = np.abs(boxes[:, 2] - boxes[:, 0])
        col_eps = np.mean(box_widths) * 0.2  # 20% of average box width
    
    # Cluster columns
    col_clusterer = DBSCAN(eps=col_eps, min_samples=1)
    col_labels = col_clusterer.fit_predict(centers[:, 0].reshape(-1, 1))
    
    # Sort column labels by x-position
    unique_cols = np.unique(col_labels)
    col_positions = [np.mean(centers[col_labels == c, 0]) for c in unique_cols]
    col_mapping = {old: new for new, old in enumerate(np.argsort(col_positions))}
    cols = np.array([col_mapping[c] for c in col_labels])
    
    n_rows = len(unique_rows)
    n_cols = len(unique_cols)
    
    grid = {}
    for idx, (row, col) in enumerate(zip(rows, cols)):
        grid[(row, col)] = idx
    
    return grid, rows, cols, n_rows, n_cols



def df_with_aspects(df_full_clean, verbose=False, flip_y = True, get_grid = True):
    """ 
    Create the distribution for number of subfigures, columns/rows.  
    This uses the "organize boxes into grid" function to estimate nrows/ncols.
    Note that this will mess up for figures with complex, non-grid layouts.

    df_full_clean : all cleaned up pages
    flip_y : if typically ymax < ymin (i.e. for figure type things)
    get_grid : estimate nrows/ncols based on boxes
    """
    aspects_all = []
    nfigs_all = []
    fw_all = []
    #subboxes_all = []
    nrows = []; ncols = []
    articles = []
    # run the thing
    for i, d in df_full_clean.iterrows():
        for k,v in d['boxes'].items():
            if 'subfig 0' in v: # have subfigs
                aspects = get_aspects(d)
                articles.append(d['article'])
                nfigs = 0
                subboxes = []
                for kk,vv in v.items():
                    if 'subfig ' in kk:
                        nfigs += 1
                        #subboxes.append( (int(vv['xmin']), int(vv['ymax']), int(vv['xmax']), int(vv['ymin'])) )
                        #subboxes.append( (vv['xmin'], vv['ymin'], vv['xmax'], vv['ymax']) )
                        if flip_y:
                            subboxes.append( (vv['xmin'], vv['ymax'], vv['xmax'], vv['ymin']) )
                        else:
                            subboxes.append( (vv['xmin'], vv['ymin'], vv['xmax'], vv['ymax']) )

                aspects_all.append(aspects[k]['aspect ratio'])
                fw_all.append(aspects[k]['fw'])

                nfigs_all.append(nfigs)
                if get_grid:
                    try:
                        grid, rows, cols, n_rows, n_cols = organize_boxes_into_grid(subboxes)
                    except:
                        rows = np.nan; cols = np.nan
                        n_rows = np.nan; n_cols = np.nan
                    nrows.append(n_rows)
                    ncols.append(n_cols)
                    if not pd.isnull(n_rows):
                        if n_rows*n_cols != nfigs:
                            if verbose:
                                print(d['article'])
                                print('n_rows,n_cols=', n_rows, n_cols)
                                print('nfigs=', nfigs)
                                print('')
                            pass
                            #import sys; sys.exit()


    df_af = pd.DataFrame({'aspects':aspects_all, 'nfigs':nfigs_all, 'fw':fw_all, 'article':articles})
    if get_grid:
        df_af['nrows'] = nrows
        df_af['ncols'] = ncols

    return df_af


## JPN: I think this is now a class???
def get_various_plot_params(fullproc_r = "~/ArXiv_figure_injection/resources/", 
        use_uniques = True, seeds_dict=None, 
        ncols=None, nrows=None, aspect_ratio=None,
        verbose=False):
    # set all seeds and random generators for this figure
    rng_dict, seeds_dict = set_all_seeds(reset_outer = True, 
                            reset_inner = True, 
                            reset_titles=True, 
                            reset_fonts = True, 
                            reset_aspect = True, 
                            reset_ptype=True, 
                            seeds_dict=seeds_dict, 
                            verbose=verbose)

    # expand paths
    fullproc_r = os.path.expanduser(fullproc_r)
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


    # set other params
    figure_params = set_figure_params(rng_dict, color_maps, plot_styles, 
                                        aspect_fig_params, dpi_params, 
                                        panel_params, tight_layout_params, base, plot_flip_params,
                                        verbose=verbose)
    # update as needed
    if aspect_ratio is not None:
        figure_params['aspect ratio'] = aspect_ratio
    if ncols is not None:
        figure_params['# columns'] = ncols
    if nrows is not None:
        figure_params['# rows'] = nrows
    figure_params['# panels'] = int(figure_params['# columns']*figure_params['# rows'])

    font_params = get_font_params(rng_dict, fontsizes, font_names)

    return figure_params, font_params



from synthetic_training_figures.utils.tmp_port_from_script import create_data_save_dict, reset_everybody, \
    close_plot_fail, make_base_plot, print_figure_params

import gc




            

########### MOVE ###########

def add_text_value(axes, i, kp, d, aspects, aspect_key, 
    location = 'top-center', roundint = 3, 
    fontsize=12, color='white', backgroundcolor='blue'):
    """ 
    i : plot (row) number
    kp : column number (same base article)
    d : row of dataframe representing 1 page
    """
                    # # all stats
                    # for vp in vpp: # list of stats, e.g. [{'stat':'mean', 'loc':'top-center'}]
                    #     stat_print2 = vp['stat']
                    #     #print("STAT", stat_print2)
    for k,v in d['boxes'].items(): # k is figure number
        xmin=int(round(v['xmin'])); xmax = int(round(v['xmax']))
        ymin=int(round(v['ymin'])); ymax = int(round(v['ymax']))
        avalue = aspects[k][aspect_key]
        akey = aspect_key
        atext = akey + '=' + str(round(avalue, roundint))
        
        if (location == 'top-center') or (location == 'bottom-center'):
            x = int(0.5*(xmin+xmax))
        elif (location == 'right-center'):
            x = min(int(xmin)-10,0)
            y = int(np.abs(ymax+ymin)*0.5)
        elif (location == 'left-center'):
            x = int(xmax)+10
            y = int(np.abs(ymax+ymin)*0.5)
        if 'top' in location:
            y = ymax + 10
        elif 'bottom' in location:
            y = ymin - 10
        axes[i][kp].text(x,y,atext,fontsize=fontsize, color=color, backgroundcolor=backgroundcolor)


import altair as alt

# plot aspects and nrows/cols distributions
def plot_nrows_ncols_aspect(df_af):
    brush = alt.selection_interval(name='brush')

    # Create the heatmap
    heatmap = alt.Chart(df_af).mark_rect().encode(
        x=alt.X('aspects:Q', title='Aspect Ratio', bin={'maxbins':50}),
        y=alt.Y('fw:Q', title='Fractional Width', bin={'maxbins':50}),
        color=alt.Color('mean(nfigs):Q', 
                        scale=alt.Scale(scheme='viridis'),
                        title='<# figures>'),
    ).add_params(
        brush
    ).properties(
        width=400,
        height=300,
    )
    #heatmap

    hist = alt.Chart(df_af).mark_bar().encode(
        x=alt.X('nfigs'),
        y=alt.Y('count()')
    ).transform_filter(
        brush
    )

    return heatmap | hist


# same deal, 3 hists
def plot_nrows_ncols_aspect_hists(df_af, width=400, height = 300, 
    maxbins_aspect=50, maxbins_fw=50):

    brush = alt.selection_interval(name='brush')

    # Create the heatmap
    heatmap = alt.Chart(df_af).mark_rect().encode(
        x=alt.X('aspects:Q', title='Aspect Ratio', bin={'maxbins':maxbins_aspect}),
        y=alt.Y('fw:Q', title='Fractional Width', bin={'maxbins':maxbins_fw}),
        color=alt.Color('mean(nfigs):Q', 
                        scale=alt.Scale(scheme='viridis'),
                        title='<# figures>'),
    ).add_params(
        brush
    ).properties(
        width=width,
        height=height,
    )
    #heatmap

    hist1 = alt.Chart(df_af).mark_bar().encode(
        x=alt.X('nrows'),
        y=alt.Y('count()')
    ).transform_filter(
        brush
    ).properties(
        height=height//3
    )

    hist2 = alt.Chart(df_af).mark_bar().encode(
        x=alt.X('nfigs'),
        y=alt.Y('count()'), 
        tooltip=['nfigs']
    ).transform_filter(
        brush
    ).properties(
        height=height//3
    )

    hist3 = alt.Chart(df_af).mark_bar().encode(
        x=alt.X('ncols'),
        y=alt.Y('count()')
    ).transform_filter(
        brush
    ).properties(
        height=height//3
    )

    hists = hist1 & hist3 & hist2

    return heatmap | hists

