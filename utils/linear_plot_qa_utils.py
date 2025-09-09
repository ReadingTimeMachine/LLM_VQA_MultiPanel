import numpy as np

#from utils.plot_qa_utils import plot_index_to_words

#q_gmm_ngaussians_hists



from .plot_qa_utils import get_nplots, persona, context_single_multi, how_many, how_much_data_values#, check_relationship




####### CONSTRUCT QUESTIONS ########

# how many lines are in the plot?
def q_nlines_plot_plotnums(data, qa_pairs, plot_num = [0,0], 
                               return_qa=True, verbose=True, use_words=True, 
                               single_figure_flag=True, 
                               text_persona = None):
    """
    Construct Q/A for how many lines are in the plot.
    """
    big_tag = 'nlines'
    object = 'lines'
    # get answer
    ans = len(data['plot'+str(plot_num)]['data']['ys'])

    #--- typically don't need to change below ----

    nplots = get_nplots(data)
    #print('nplots = ', nplots)

    ### persona of assistant
    text_persona = persona(text=text_persona)
    ## context for question
    text_context = context_single_multi(data, nplots, plot_num, use_words, single_figure_flag)
    if text_context != '':
        print('CONTEXT:', text_context)

    ### question, format of output
    text_question, adder, text_format = how_many(object, big_tag, 
                                                       val_type = 'an integer', 
                                                       nplots = nplots, 
                                                       use_words=use_words)
    # check adder
    # if adder != '':
    #     adder = adder
    # construct question:
    q = text_persona + " " + text_context + " " + text_question + " " + text_format
    # get answer, formatted
    a = {big_tag + adder: ans}
    if verbose:
        print('QUESTION:', q)
        print('ANSWER:', a)
    if return_qa: 
        if big_tag + adder not in qa_pairs['Level 1']['Plot-level questions']:
            qa_pairs['Level 1']['Plot-level questions'][big_tag +  adder] = {'plot'+str(plot_num):{'Q':q, 'A':a, 
                                                                                                        'persona':text_persona, 
                                                                                                        'context':text_context,
                                                                                                        'question':text_question, 
                                                                                                        'format':text_format}}
        else:
            qa_pairs['Level 1']['Plot-level questions'][big_tag + adder]['plot'+str(plot_num)] = {'Q':q, 'A':a, 
                                                                                                        'persona':text_persona, 
                                                                                                        'context':text_context,
                                                                                                        'question':text_question, 
                                                                                                        'format':text_format}
        return qa_pairs
    

def q_stats_lines(data, qa_pairs, stat = {'minimum':np.min}, axis = 'x',
                  plot_num = 0, 
                     return_qa=True, use_words=True, verbose=True, 
                     single_figure_flag=True, 
                               text_persona = None):
    """
    stat: {'name':stat} which gives name of stat and function to calculate it, like {'minimum':np.min}
    use_words : set to True to translate row, column to words; False will use C-ordering indexing
    stat : dictionary of the name and function to use for each stat
    """
    # output type
    val_type = 'a list of floats'

    # check
    if axis.lower() == 'x': 
        axis = 'x'
    elif axis.lower() == 'y':
        axis = 'y'
    else:
        print('Axis not chosen correctly:', axis)
        import sys; sys.exit()

    #### Answer
    f = list(stat.values())[0] # what statical function
    zs = data['plot'+str(plot_num)]['data'][axis+'s']
    list_stat = []
    for z in zs:
        list_stat.append(f(z))

    for_each = ', where each element of the list corresponds to one line in the plot'

    #---- Don't have to change much below ----
    big_tag = list(stat.keys())[0]
    # get nplots    
    nplots = get_nplots(data)

    ### persona of assistant
    text_persona = persona(text=text_persona)
    ## context for question
    text_context = context_single_multi(data, nplots, plot_num, use_words, single_figure_flag)
    if text_context != '':
        print('CONTEXT:', text_context)

    text_question, adder, text_format  = how_much_data_values(big_tag, nplots=nplots, 
                                                              axis=axis, 
                                                              val_type=val_type, 
                                                              use_words=use_words, 
                                                              along_an_axis=True,
                                                              for_each=for_each)
    # big tag update
    big_tag += ' ' + axis
    # format answer
    #la = {big_tag + " "+axis:list_stat}
    la = {big_tag:list_stat}
    ans = {big_tag +  adder:{'plot'+str(plot_num):la}} 
    a = {big_tag +  adder:la}
    # construct question:
    q = text_persona + " " + text_context + " " + text_question + " " + text_format

    if verbose:
        print('QUESTION:', q)
        print('ANSWER:', ans)
    if return_qa: 
        if big_tag + adder not in qa_pairs['Level 2']['Plot-level questions']:
            qa_pairs['Level 2']['Plot-level questions'][big_tag + adder] = {'plot'+str(plot_num):{'Q':q, 'A':a, 
                                                                                                        'persona':text_persona, 
                                                                                                        'context':text_context,
                                                                                                        'question':text_question, 
                                                                                                        'format':text_format}}
        else:
            qa_pairs['Level 2']['Plot-level questions'][big_tag + adder]['plot'+str(plot_num)] = {'Q':q, 'A':a, 
                                                                                                        'persona':text_persona, 
                                                                                                        'context':text_context,
                                                                                                        'question':text_question, 
                                                                                                        'format':text_format}
        return qa_pairs
    



########## L2/L3 #############
from .plot_qa_utils import what_is_relationship
def q_relationship_lines(data, qa_pairs, plot_num = 0, 
                         return_qa=True, use_words=True, 
                         use_list=True, use_nlines = True,
                        line_list = ['random','linear','gaussian mixture model'], 
                        single_figure_flag=True,
                        verbose=True, text_persona = None):
    """
    use_words : set to True to translate row, column to words; False will use C-ordering indexing
    use_list : give a list of possible distributions
    use_nplots : give the number of lines in the prompt
    """
    
    # how many plots
    big_tag = 'distribution'
    val_type = 'a list of strings'
    for_each = ', where each element of the list corresponds to one line in the plot'
    mark = 'line'

    # ---- don't have to change much below this -----
    # get nplots    
    nplots = get_nplots(data)
    #adder = get_adder(nplots, use_words)
    text_question, adder, text_format = what_is_relationship(big_tag, nplots=nplots, 
                                                              val_type=val_type, 
                                                              use_words=use_words, 
                                                              along_an_axis=False,
                                                              for_each=for_each)
    
    ### persona of assistant
    text_persona = persona(text=text_persona)
    ## context for question
    text_context = context_single_multi(data, nplots, plot_num, use_words, single_figure_flag)
    if text_context != '':
        print('CONTEXT:', text_context)

    if use_nlines:
        adder = adder.split(')')[0] + ' + nlines)'
        text_format += ' Please note that there are a total of ' + str(int(len(data['plot' + str(plot_num)]['data']['ys']))) + ' lines in this plot, so the list should have a '
        text_format += 'total of ' +str(int(len(data['plot' + str(plot_num)]['data']['ys'])))+ ' entries. '

    if use_list:
        adder = adder.split(')')[0] + ' + list)'
        text_format += ' Please choose each '+big_tag+' for each '+mark+' from the following list: ['
        for pt in line_list:
            text_format += pt + ', '
        text_format = text_format[:-2] # take off the last bit
        text_format += '].'

    q = text_persona + " " + text_context + " " + text_question + " " + text_format

    # answer
    la = []
    for i in range(len(data['plot' + str(plot_num)]['data']['ys'])):
        dist = data['plot'+str(plot_num)]['distribution']
        # to match
        if dist == 'gmm': dist = 'gaussian mixture model'
        la.append(dist) # note: assumes same for all!
    #a = la
    a = {big_tag + ' ' + adder:la}

    if verbose:
        print('QUESTION:', q)
        print('ANSWER:', a)
    if return_qa: 
        if big_tag + ' ' + adder not in qa_pairs['Level 3']['Plot-level questions']:
            #print('yes', big_tag_short + ' ' + adder)
            qa_pairs['Level 3']['Plot-level questions'][big_tag + ' ' + adder] = {'plot'+str(plot_num):{'Q':q, 'A':a, 
                                                                                                              'note':'this currently assumes all elements on a single plot have the same relationship type', 
                                                                                                        'persona':text_persona, 
                                                                                                        'context':text_context,
                                                                                                        'question':text_question, 
                                                                                                        'format':text_format}}
        else:
            qa_pairs['Level 3']['Plot-level questions'][big_tag + ' ' + adder]['plot'+str(plot_num)] = {'Q':q, 'A':a, 
                                                                                                              'note':'this currently assumes all elements on a single plot have the same relationship type', 
                                                                                                        'persona':text_persona, 
                                                                                                        'context':text_context,
                                                                                                        'question':text_question, 
                                                                                                        'format':text_format}
        return qa_pairs
    
   


####### JPN: below needs to be cleaned more #######

def q_colors_lines(data, qa_pairs, plot_num = 0, return_qa=True, use_words=True, verbose=True, 
                   text_persona=None, single_figure_flag=True):
    """
    use_words : set to True to translate row, column to words; False will use C-ordering indexing
    """
    big_tag = 'line colors'
    ### question
    text_question = 'What are the colors of the lines in this figure panel?'
    ### format
    text_format = 'Please format the output as a json as {"line colors":[]}, where each element of the list refers to the '
    text_format += ' color of each line in the figure panel in the form of an RGBA list with values between 0 and 1. '
    # answer
    la = []
    for k,v in data.items():
        if 'plot' + str(plot_num) == k: # is a plot
            #if 'plot params' in v['data from plot']:
            for c in v['data from plot']['plot params']['colors']:
                la.append(c[0]) # the "0" here is because, in theory, the line could be made up of more than one color
    answer = {big_tag + ' ' + adder:{'plot'+str(plot_num):la}} 

    # ------ don't have to change much below ------
    # get nplots    
    nplots = get_nplots(data)
    ### persona of assistant
    text_persona = persona(text=text_persona)
    ## context for question
    text_context = context_single_multi(data, nplots, plot_num, use_words, single_figure_flag)
    if text_context != '':
        print('CONTEXT:', text_context)
    if use_words:
        adder = '(words)'
    # all together
    q = text_persona + " " + text_context + " " + text_question + " " + text_format
    if verbose:
        print('QUESTION:', q)
        print('ANSWER:', answer)
    if return_qa: 
        if big_tag + ' ' + adder not in qa_pairs['Level 1']['Plot-level questions']:
            qa_pairs['Level 1']['Plot-level questions'][big_tag + ' ' + adder] = {'plot'+str(plot_num):{'Q':q, 'A':answer, 
                                                                                                        'persona':text_persona, 
                                                                                                        'context':text_context,
                                                                                                        'question':text_question, 
                                                                                                        'format':text_format}}
        else:
            qa_pairs['Level 1']['Plot-level questions'][big_tag + ' ' + adder]['plot'+str(plot_num)] = {'Q':q, 'A':answer, 
                                                                                                        'persona':text_persona, 
                                                                                                        'context':text_context,
                                                                                                        'question':text_question, 
                                                                                                        'format':text_format}
        return qa_pairs




def q_linestyles_lines(data, qa_pairs, plot_num = 0, return_qa=True, use_words=True, use_list=False,
                      linestyle_list = [], verbose=True, 
                      text_persona=None, single_figure_flag=True):
    """
    use_words : set to True to translate row, column to words; False will use C-ordering indexing
    use_list : use a list of linestyle options for prompting
    """
    
    big_tag = 'line styles'
    plot_param_tag = 'linestyles'
    adder_adder = ''; text_context_adder = ''
    ### question
    text_question = 'What are the matplotlib linestyles in this figure panel?'
    ### format
    text_format = 'Please format the output as a json as {"line styles":[]}, where each element of the list refers to the'
    text_format += ' linestyle of each line in the figure panel in the form a matplotlib linestyle type.'
    if use_list:
        adder_adder = ' + list'
        text_context_adder = ' Please choose each linestyle from the following list: ['
        for pt in linestyle_list:
            text_context_adder += pt + ', '
        text_context_adder = text_context_adder[:-2] # take off the last bit
        text_context_adder += '].'
    if use_words:
        adder = 'words' + adder_adder
        adder = '(' + adder + ')'
    # answer
    la = []
    for k,v in data.items():
        if 'plot' + str(plot_num) == k: # is a plot
            #if 'plot params' in v['data from plot']:
            for c in v['data from plot']['plot params'][plot_param_tag]:
                la.append(c[0]) # the "0" here is because, in theory, the line could be made up of more than one color
    answer = {big_tag + ' ' + adder:{'plot'+str(plot_num):la}} 

    # ------ don't have to change much below ------
    # get nplots    
    nplots = get_nplots(data)
    ### persona of assistant
    text_persona = persona(text=text_persona)
    ## context for question
    text_context = context_single_multi(data, nplots, plot_num, use_words, single_figure_flag)
    text_context += text_context_adder
    if text_context != '':
        print('CONTEXT:', text_context)

    # all together
    q = text_persona + " " + text_context + " " + text_question + " " + text_format
    if verbose:
        print('QUESTION:', q)
        print('ANSWER:', answer)
    if return_qa: 
        if big_tag + ' ' + adder not in qa_pairs['Level 1']['Plot-level questions']:
            qa_pairs['Level 1']['Plot-level questions'][big_tag + ' ' + adder] = {'plot'+str(plot_num):{'Q':q, 'A':answer, 
                                                                                                        'persona':text_persona, 
                                                                                                        'context':text_context,
                                                                                                        'question':text_question, 
                                                                                                        'format':text_format}}
        else:
            qa_pairs['Level 1']['Plot-level questions'][big_tag + ' ' + adder]['plot'+str(plot_num)] = {'Q':q, 'A':answer, 
                                                                                                        'persona':text_persona, 
                                                                                                        'context':text_context,
                                                                                                        'question':text_question, 
                                                                                                        'format':text_format}
        return qa_pairs


#### JPN: maybe add "q_linethickness_lines"

#### JPN: maybe add "q_linemarkers_lines"

#### JPN: maybe add "q_linemarkersize_lines"

### HERE ###
def q_datapoints_lines(data, qa_pairs, plot_num = 0, return_qa=True, use_words=True, 
                      line_list = [], verbose=True):
    """
    use_words : set to True to translate row, column to words; False will use C-ordering indexing
    use_list : use a list of "property" options for prompting
    """
    big_tag = 'data values'
    # how many plots
    nplots = 0
    for k,v in data.items(): # count number of plots
        if 'plot' in k:
            nplots += 1
    if not use_words:
        adder = '(plot numbers)'
        # rows columns
        nrow = data['figure']['plot indexes'][plot_num][0]
        ncol = data['figure']['plot indexes'][plot_num][1]
        q = 'The following question refers to the figure panel on row number ' + str(nrow) + ' and column number ' + str(ncol) + '. '
        q += 'If there are multiple plots the panels will be in row-major (C-style) order, with the numbering starting at (0,0) in the upper left panel. '
        q += 'If there is one plot, then this row and column refers to the single plot. '
    else: 
        adder = '(words)'

    if nplots == 1: # single plot
        q = 'What are the data values in this figure? '
    else:
        if not use_words:
            q += 'What are the data values for the figure panel on row number ' + str(nrow) + ' and column number ' + str(ncol) + '? '
        else:
            q = 'What are the data values for the plot in the ' + plot_index_to_words(data['figure']['plot indexes'][plot_num]) + ' panel? '     

    q += 'You are a helpful assistant, please format the output as a json as {"x":[], "y":[]} where the values of "x" and "y" are the '
    q += 'data values used to create the plot.  '
    q += 'If there is one single array for x data values for all lines on the plot, "x" will be a single list, otherwise it will be a list of lists. '
    q += 'If there is one single array for y data values for all lines on the plot, "y" will be a single list, otherwise it will be a list of lists. '
    
    # get answer list
    la = {"x":data['plot'+str(plot_num)]['data']['xs'], "y":data['plot'+str(plot_num)]['data']['ys']}
    a = {big_tag + ' ' + adder:{'plot'+str(plot_num):la}} 
    if verbose:
        print('QUESTION:', q)
        print('ANSWER:', a)
    if return_qa: 
        if big_tag + ' ' + adder not in qa_pairs['Level 1']['Plot-level questions']:
            qa_pairs['Level 1']['Plot-level questions'][big_tag + ' ' + adder] = {'plot'+str(plot_num):{'Q':q, 'A':a}}
        else:
            qa_pairs['Level 1']['Plot-level questions'][big_tag + ' ' + adder]['plot'+str(plot_num)] = {'Q':q, 'A':a}
        return qa_pairs