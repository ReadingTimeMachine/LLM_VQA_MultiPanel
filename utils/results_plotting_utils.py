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
                     levels=3, alpha=0.5, plot_kde=True):
    """Add KDE contours directly using seaborn"""
    # Add contour lines
    if plot_kde:
        sns.kdeplot(x=x_data, y=y_data, ax=ax, color=color, 
                fill=False, alpha=alpha, linewidths=2, levels=levels)
    
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