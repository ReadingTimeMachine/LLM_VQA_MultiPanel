# for plotting final results
import seaborn as sns
from glob import glob
import os
import numpy as np
import pandas as pd
from copy import deepcopy

def get_dirs_names_files(main_llm_dir, dirs_to_use,
    verbose=True, 
    replace_names = {'chatgpt_api':'ChatGPT'}):
    """
    replace_names : replacement directories for how directories
      are named and how you want them to be plotting on labels
    """
    dirs_tmp = glob(main_llm_dir + '*')
    if verbose:
        print('DIRS:')
        for d in dirs_tmp:
            print(d)
        print('')

    dirnames = []

    dirs = []
    for d in dirs_to_use:
        dn = d.replace('/','')
        for k,v in replace_names.items():
            if dn == k:
                dn = v
        dirnames.append(dn)
        dirs.append(main_llm_dir + d)

    if verbose:
        print('ONLY USED DIRNAMES, DIRS')
        for d,dn in zip(dirs,dirnames):
            print(dn, ', ', d)
        print('')


    # find total overlap of files
    files_parsed = []
    for d in dirs:
        files = glob(d + '/*.pickle')
        for f in files:
            files_parsed.append(f.split('/')[-1])
    files_parsed1 = list(set(files_parsed))
    # now check all exist
    files_parsed = []
    for f in files_parsed1:
        exists = True
        for d in dirs:
            if not os.path.exists(d + '/' + f):
                exists = False
        if exists:
            files_parsed.append(f)

    if verbose:
        print("there are:", len(files_parsed), 'overlapping files so far')

    return dirnames, dirs, files_parsed

# For levels:
# Number of contour levels or values to draw contours at. 
# A vector argument must have increasing values in [0, 1]. 
# Levels correspond to iso-proportions of the density: 
# e.g., 20% of the probability mass will lie below the 
# contour drawn for 0.2. Only relevant with bivariate data.

# Alternative approach using seaborn's kdeplot directly
def add_kde_contours(ax, x_data, y_data, color, label, marker, marker_size, 
                     levels=3, alpha=0.5, plot_kde=True, linestyle='-'):
    """Add KDE contours directly using seaborn"""
    # Add contour lines
    if plot_kde:
        sns.kdeplot(x=x_data, y=y_data, ax=ax, color=color, 
                fill=False, alpha=alpha, linewidths=2, levels=levels, 
                linestyles=linestyle)
    
    # Add scatter points
    if label is not None:
        ax.scatter(x_data, y_data, c=color, marker=marker, s=marker_size, 
              alpha=0.8, label=label, edgecolors='white', linewidth=0.5)
    else:
        ax.scatter(x_data, y_data, c=color, marker=marker, s=marker_size, 
              alpha=0.8, edgecolors='white', linewidth=0.5)


#####################################################
from .parse_lmm_output_utils import get_lmm_gt
from Levenshtein import distance as levenshtein_distance # Assuming you have python-Levenshtein installed


def calculate_plot_accuracies(df, questions_figure, df_question_tags, 
        plot_diffs = {'float':False}, normalize_diffs = {'float':False}):
    df_F_question_tags = {}
    for k,v in df_question_tags.items():
        df_F_question_tags[k] = []

    use_float_average = True # if so, will divide floats by average gt

    dfplot = {'Tag':[]}
    

    # fill level and level types
    for iq,q in enumerate(questions_figure):
        if iq > 0: continue
        dfplot[q['tag'] + ' GT'] = []
        dfsub = df[df['question']==q['question']]
        for model in dfsub['model'].unique():
            dfplot[model + ' ' + q['tag']] = []
            dfsub2 = dfsub[dfsub['model']==model]
            if q['tag'] == '# panels': # something special
                gt = []
                for g in dfsub2['GT Answer'].values:
                    gt.append(g['nrows']*g['ncols'])
                lmm = []
                for l in dfsub2['LMM Answer'].values:
                    lmm.append(l['nrows']*l['ncols'])
                # fill
                dfplot[model + ' ' + q['tag']].extend(lmm)
        # include gt
        dfplot[q['tag'] + ' GT'].extend(gt)
        dfplot['Tag'].extend([q['tag']]*len(gt))
        #df_question_tags['Level'].append(np.unique(dfsub['Level'])[0])

    # now add other questions
    for iq,q in enumerate(questions_figure):
        if iq < 1: continue # don't re-do add of panels
        dfsub = df[df['question']==q['question']]
        # if length is zero, look at subset
        #df_question_tags['Level'].append(np.unique(dfsub['Level'])[0])
        for model in dfsub['model'].unique():
            dfplot[model + ' ' + q['tag']] = []
            dfsub2 = dfsub[dfsub['model']==model]    
            if q['type'] == 'binary string': 
                gt, lmm = get_lmm_gt(dfsub2, q['type'])
                calc = []
                for g,l in zip(gt,lmm):
                    if g == l:
                        calc.append(1)
                    else:
                        calc.append(0)
                # fill
                dfplot[model + ' ' + q['tag']].extend(calc)
                # gt
                #dfplot[q['tag'] + ' GT'].extend(gt)

            elif q['type'] == 'string list':
                # loop over every figure
                calc = [] # normalized distance
                #l_tot = []
                #total_d = 0; total_l = 0
                for iq in range(len(dfsub2)): # over each image
                    dfsub22 = dfsub2.iloc[iq]
                    gt, lmm = get_lmm_gt(dfsub22.to_frame().T, q['type'], verbose=False)
                    #lmm_tot.extend(lmm)
                    # get distance/length
                    total_d = 0; total_l = 0
                    for g, l in zip(gt,lmm): # over all titles in each image
                        d = levenshtein_distance(g,l)
                        total_d += d
                        if len(g) > 0:
                            total_l += len(g)
                        else:
                            total_l += len(l)
                    if total_l > 0:
                        calc.append(total_d*1.0/total_l)
                    else:
                        calc.append(0)
                # fill
                dfplot[model + ' ' + q['tag']].extend((1.0-np.array(calc)).tolist()) # 1 - so closer to other acc

            elif q['type'] == 'float':
                gt, lmm1 = get_lmm_gt(dfsub2, q['type'])
                if plot_diffs['float']:
                    calc = (lmm1-gt)
                    if normalize_diffs['float']:
                        calc = calc/gt
                else:
                    calc = deepcopy(lmm1)       
                dfplot[model + ' ' + q['tag']].extend(calc) # 1 - so closer to other acc
                #dfplot[q['tag'] + ' GT'].extend(gt)
                
            elif q['type'] == 'binary string list':
                calc = []
                if 'use list' in q:
                    if q['use list']: # if yes to it
                        dfsub2t = dfsub2[dfsub2['use list']]
                    elif not q['use list']:
                        dfsub2t = dfsub2[~dfsub2['use list']]
                    dfsub2 = dfsub2t.copy()
                for iq in range(len(dfsub2)): # over each image
                    dfsub22 = dfsub2.iloc[iq]
                    gt, lmm = get_lmm_gt(dfsub22.to_frame().T, q['type'], verbose=False) # for full image, will align
                    total_count = 0.0
                    for g,l in zip(gt,lmm):
                        if g.lower().replace(' ', '').strip() == l.lower().replace(' ', '').strip():
                            total_count += 1
                    calc.append(total_count/len(gt))
                dfplot[model + ' ' + q['tag']].extend(calc) # 1 - so closer to other acc



    dfplot = pd.DataFrame(dfplot)

    # also track questions
    for qa in questions_figure:
        dfsub = df[df['question']==qa['question']]
        df_F_question_tags['tag'].append(qa['tag'].replace('#', '\\#'))
        df_F_question_tags['question'].append(qa['question'].replace('#', '\\#'))
        level = np.unique(dfsub['Level'])[0].split('Level')[-1].replace(' ','')
        df_F_question_tags['Level'].append(level)
        ltype = np.unique(dfsub['Level Type'])[0].split('-level questions')[0]
        df_F_question_tags['Type'].append(ltype)

    return df_F_question_tags, dfplot

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import math

def make_square_grid_figure(n_plots, figsize_per_plot=(3, 3), **fig_kwargs):
    """
    Create a figure with n_plots axes of identical size, arranged as
    squarely as possible.

    Layout rules:
    - Rows may have different column counts (last row can have fewer).
    - All axes have the same width and height.
    - Axes in a full row share the same x/y grid positions (alignable).
    - Axes in a short row are horizontally centered.
    - Returns (fig, axes) where axes is a flat list of length n_plots.

    Parameters
    ----------
    n_plots : int
        Number of axes to create.
    figsize_per_plot : (float, float)
        Width and height (in inches) of each individual subplot.
    **fig_kwargs
        Extra keyword arguments forwarded to plt.figure().

    Returns
    -------
    fig : matplotlib.figure.Figure
    axes : list of matplotlib.axes.Axes, length n_plots
    """
    if n_plots < 1:
        raise ValueError("n_plots must be at least 1")

    # --- determine grid dimensions ---
    ncols = math.ceil(math.sqrt(n_plots))   # columns in a full row
    nrows = math.ceil(n_plots / ncols)

    pw, ph = figsize_per_plot
    fig_w = pw * ncols
    fig_h = ph * nrows
    # fig = plt.figure(figsize=(fig_w, fig_h), **fig_kwargs)
    fig = plt.figure(figsize=(fig_w, fig_h), layout="constrained", **fig_kwargs)

    axes = []
    for row in range(nrows):
        # how many plots live in this row?
        first_in_row = row * ncols
        n_this_row = min(ncols, n_plots - first_in_row)

        # fractional width/height of one cell in figure coordinates
        cell_w = 1.0 / ncols
        cell_h = 1.0 / nrows

        # vertical position (top-down)
        y0 = 1.0 - (row + 1) * cell_h

        # horizontal offset so a short row is centered
        x_start = (1.0 - n_this_row * cell_w) / 2.0

        for col in range(n_this_row):
            x0 = x_start + col * cell_w

            # small margin so axes don't touch each other or the figure edge
            margin = 0.04
            ax = fig.add_axes([
                x0 + margin * cell_w,
                y0 + margin * cell_h,
                cell_w * (1 - 2 * margin),
                cell_h * (1 - 2 * margin),
            ])
            axes.append(ax)

    return fig, axes


# import matplotlib.pyplot as plt
# import matplotlib.gridspec as gridspec
# import math

def make_square_grid_figure_gs(n_plots, figsize_per_plot=(3, 3),
                            hspace=0.4, wspace=0.4, **fig_kwargs):
    if n_plots < 1:
        raise ValueError("n_plots must be at least 1")

    ncols = math.ceil(math.sqrt(n_plots))
    nrows = math.ceil(n_plots / ncols)
    n_last_row = n_plots - (nrows - 1) * ncols
    last_row_is_short = n_last_row < ncols

    pw, ph = figsize_per_plot
    fig = plt.figure(figsize=(pw * ncols, ph * nrows), **fig_kwargs)

    # One GridSpec for the whole figure
    gs = gridspec.GridSpec(nrows, ncols, figure=fig, hspace=hspace, wspace=wspace)

    axes = []

    # All full rows — standard subplot cells
    full_rows = nrows - 1 if last_row_is_short else nrows
    for row in range(full_rows):
        for col in range(ncols):
            ax = fig.add_subplot(gs[row, col])
            axes.append(ax)

    # Short last row — center it by spanning columns symmetrically
    if last_row_is_short:
        # Figure out which columns to occupy for centering.
        # We nest a sub-GridSpec inside a merged cell span.
        empty_cols = ncols - n_last_row
        left_empty = empty_cols // 2      # columns to leave blank on the left
        right_empty = empty_cols - left_empty

        col_start = left_empty
        col_end = ncols - right_empty     # exclusive

        # Nest a GridSpec inside the merged last-row span
        sub_gs = gridspec.GridSpecFromSubplotSpec(
            1, n_last_row,
            subplot_spec=gs[nrows - 1, col_start:col_end],
            hspace=hspace,
            wspace=wspace,
        )
        for col in range(n_last_row):
            ax = fig.add_subplot(sub_gs[0, col])
            axes.append(ax)

    fig.tight_layout()   # now works without warnings
    return fig, axes


def create_output_marks(df, marker_min = 15, marker_max = 65,
    colors_levels = ['darkblue', 'orange', 'cyan', 'green', 'magenta', 'gold', 'orangered', 'purple', 'deepskyblue', 'red'], 
    marker_styles_levels = ['s','o','^', 'D', 'X','*','h']
    ):

    marker_sizes = {}
    marker_sizes_levels = np.round(np.linspace(marker_min, marker_max, df['model'].nunique())).astype('int')[::-1]
    for i,m in enumerate(df['model'].unique()):
        marker_sizes[m] = marker_sizes_levels[i]
    # fill marker styles
    marker_styles = {}
    if df['model'].nunique() > len(marker_styles_levels):
        print('Not enough markers!')
        import sys; sys.exit()
    for i,m in enumerate(df['model'].unique()):
        marker_styles[m] = marker_styles_levels[i]
    # fill colors
    colors = {}
    if df['model'].nunique() > len(colors_levels):
        print('Not enough colors!')
        import sys; sys.exit()
    for i,m in enumerate(df['model'].unique()):
        colors[m] = colors_levels[i]
    # fill labels
    labels = {}
    labels_levels = []
    for i,m in enumerate(df['model'].unique()):
        if len(labels_levels) < df['model'].nunique(): # not enough labels
            labels[m] = str(m)

    return marker_sizes, marker_styles, colors, labels