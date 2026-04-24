# for plotting final results
import seaborn as sns
from glob import glob
import os

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