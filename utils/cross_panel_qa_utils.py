import numpy as np
from .plot_qa_utils import get_nplots, persona, context_single_multi, how_many, how_much_data_values, get_format_adder, plot_index_to_words

def format_index(data):
    index_format = 'Assume the following indexing for the panels in this figure:'
    for k,v in data.items():
        if 'plot' in k:
            kind = k.split('plot')[-1]
            index_format += ' plot ' + kind + ' is the ' + plot_index_to_words(data['figure']['plot indexes'][int(kind)]) + ' panel,'
    index_format = index_format.removesuffix(',') + '.'
    return index_format


def calc_strongest(data, verbose=False):
    relations = {'plots':[], 'avalues':[]}

    for k,v in data.items():
        if 'plot' in k:
            if data[k]['distribution'] == 'linear' and data[k]['type'] != 'contour' and data[k]['type'] != 'histogram':
                relations['plots'].append(k)
                try:
                    relations['avalues'].append(data[k]['data']['data params']['points']['a'])
                except:
                    try:
                        relations['avalues'].append(data[k]['data']['data params']['a'])
                    except:
                        if 'line0' in data[k]['data']['data params']: # multiline plot
                            if verbose:
                                print('Multi-line plot with more than 1 linear relationship -- taking max')
                            aa = []
                            for lk, l in data[k]['data']['data params'].items():
                                aa.append(l['a'])
                            i = np.argmax(np.abs(aa))
                            relations['avalues'].append(aa[i])
                        else:
                            return '','',True

    # are there no linear relationships? if not, ignore
    if len(relations['plots']) <= 1: # only 1 or less -- can't compare
        return '','', True

    max_relation = np.argmax(np.abs(relations['avalues']))
    plot_strongest = 'Plot ' + str(relations['plots'][max_relation].split('plot')[-1])
    if verbose:
        print('all relations:')
        for p,a in zip(relations['plots'],relations['avalues']):
            print('  ', p, ', a =', a, ', type =', data[p]['type'])
        print('')
        print('Plot with strongest linear relationship:')
        print('  ', plot_strongest)
    return plot_strongest,relations['plots'],False



#### L3(?) ####
# for only lines and scatters
def q_strongest_relationship(data, qa_pairs, 
                               return_qa=True, verbose=True, use_list=True,
                               single_figure_flag=True, 
                               text_persona = None, level='Level 3'):
    """
    Construct Q/A for how many lines are in the plot.
    """
    tag = 'cross - strongest linear'
    # get answer
    ans1, ans_list1, err = calc_strongest(data)#,verbose=verbose)
    if err:
        #if verbose: print('ERROR in q_strongest_relationship (or missing linear plots)')
        return qa_pairs, True
    # ans into integer
    ans = int(ans1.lower().replace('plot',''))
    ans_list = []
    for a in ans_list1:
        ans_list.append(int(a.replace('plot','')))

    ### persona of assistant
    text_persona = persona(text=text_persona)
    ## context for question
    #text_context = context_single_multi(data, nplots, plot_num, use_words, single_figure_flag)
    index_format = format_index(data)
    text_context = index_format
    
    ### return format
    adder, _ = get_format_adder('', tag, val_type = 'a string', 
                                nplots = 2, use_words=False, use_list=use_list)
    adder = adder.replace('(plot numbers) ','')
    #text_format = 'Please format the output as a json as {"'+tag+'"}'
    text_format = 'Please format the output as a json as {"'+tag+'":""} for this figure panel, where the "'+tag+'" value should be an integer referring to the panel number which contains the strongest linear relationship.'

    ### basic question
    text_question = 'Which plot shows the strongest linear relationship between its x and y values?'
    if use_list:
        text_question += ' Please choose from the following list of plot numbers: ' + str(ans_list) + '.'

    # construct question:
    q = text_persona + " " + text_context + " " + text_question + " " + text_format
    # get answer, formatted
    a = {tag + adder: ans}
    if verbose:
        print('QUESTION:', q)
        print('ANSWER:', a)
    if return_qa: 
        #         qa_pairs['Level 1']['Figure-level questions'][outtag] = {'Q':q, 'A':a1, 
        if 'Figure-level questions' not in qa_pairs[level]:
            qa_pairs[level]['Figure-level questions'] = {}
        if tag + adder not in qa_pairs[level]['Figure-level questions']:
            qa_pairs[level]['Figure-level questions'][tag +  adder] = {'Q':q, 'A':a, 
                                                                            'persona':text_persona, 
                                                                            'context':text_context,
                                                                            'question':text_question, 
                                                                            'format':text_format}
        else:
            qa_pairs[level]['Figure-level questions'][tag + adder] = {'Q':q, 'A':a, 
                                                                            'persona':text_persona, 
                                                                            'context':text_context,
                                                                            'question':text_question, 
                                                                            'format':text_format}
        return qa_pairs, False
    



##### L3(?) #####

def get_names_rel_and_stat(relation, stat, verbose=False):
    if 'max' in str(relation.__name__).lower():
        lam = 'largest'
    elif 'min' in str(relation.__name__).lower():
        lam = 'smallest'
    else: # just best guess?
        lam = str(relation.__name__).lower()
        if verbose:
            print('[ERROR]: not sure how to name relationship --', lam)
        return '','', True

    statname = str(stat.__name__).lower()
    return lam, statname, False


def calc_strongest_stat_hists(data, stat=np.median, verbose=False, relation = np.argmax, use_abs=False):

    relations = {'plots':[], 'mvalues':[]}

    for k,v in data.items():
        if 'plot' in k:
            if data[k]['type'] == 'histogram':
                relations['plots'].append(k)
                relations['mvalues'].append(stat(data[k]['data']['xs']))

    if len(relations['plots']) <= 1: # only 1 or less
        return '','',True

    if 'max' in str(relation.__name__).lower():
        lam = 'largest'
    elif 'min' in str(relation.__name__).lower():
        lam = 'smallest'
    else:
        lam = '<UNKNOWN QUANT>'

    if use_abs:
        max_relation = relation(np.abs(relations['mvalues']))
    else:
        max_relation = relation(relations['mvalues'])
    plot_strongest = 'Plot ' + str(relations['plots'][max_relation].split('plot')[-1])
    if verbose:
        print('all '+str(stat.__name__)+'s:')
        for p,a in zip(relations['plots'],relations['mvalues']):
            print('  ', p, ', stat =', a, ', type =', data[p]['type'])
        print('')
        print('Plot with '+lam+' '+str(stat.__name__)+':')
        print('  ', plot_strongest)
    return plot_strongest,relations['plots'],False   


# only histograms
# for only lines and scatters
def q_large_small_stat_hists(data, qa_pairs, stat = np.median, relation = np.argmax, 
                                use_abs = False,
                               return_qa=True, verbose=True, use_list=True,
                               single_figure_flag=True, 
                               text_persona = None, level='Level 3'):
    """
    Construct Q/A for how many lines are in the plot.
    """
    tag = 'cross - ' # base
    lname,sname, err = get_names_rel_and_stat(relation, stat)#, verbose=verbose)
    if err:
        # if verbose:
        #     print('Error in q_large_small_stat_hists')
        return qa_pairs, True
    tag += lname + ' ' + sname

    # get answer
    ans1, ans_list1, err = calc_strongest_stat_hists(data, relation=relation, 
                                                    stat=stat, use_abs=use_abs, verbose=False)
    if err:
        #if verbose: print('ERROR in q_large_small_stat_hists')
        return qa_pairs, True
    # ans into integer
    ans = int(ans1.lower().replace('plot',''))
    ans_list = []
    for a in ans_list1:
        ans_list.append(int(a.replace('plot','')))

    ### persona of assistant
    text_persona = persona(text=text_persona)
    ## context for question
    #text_context = context_single_multi(data, nplots, plot_num, use_words, single_figure_flag)
    index_format = format_index(data)
    text_context = index_format
    
    ### return format
    adder, _ = get_format_adder('', tag, val_type = 'a string', 
                                nplots = 2, use_words=False, use_list=use_list)
    adder = adder.replace('(plot numbers) ','')
    add_abs = ''
    if use_abs:
        add_abs = ' absolute value'
        adder += ' (abs)'
    #text_format = 'Please format the output as a json as {"'+tag+'"}'
    text_format = 'Please format the output as a json as {"'+tag+'":""} for this figure panel, where the "'+tag+'" value should be an integer referring to the panel number which shows the '+lname+add_abs+' data '+sname+'.'

    ### basic question
    text_question = 'Which plot shows the '+lname+add_abs+' ' +sname+ ' data values?'
    if use_list:
        text_question += ' Please choose from the following list of plot numbers: ' + str(ans_list) + '.'

    # construct question:
    q = text_persona + " " + text_context + " " + text_question + " " + text_format
    # get answer, formatted
    a = {tag + adder: ans}
    if verbose:
        print('QUESTION:', q)
        print('ANSWER:', a)
    if return_qa: 
        #         qa_pairs['Level 1']['Figure-level questions'][outtag] = {'Q':q, 'A':a1, 
        if 'Figure-level questions' not in qa_pairs[level]:
            qa_pairs[level]['Figure-level questions'] = {}
        if tag + adder not in qa_pairs[level]['Figure-level questions']:
            qa_pairs[level]['Figure-level questions'][tag +  adder] = {'Q':q, 'A':a, 
                                                                            'persona':text_persona, 
                                                                            'context':text_context,
                                                                            'question':text_question, 
                                                                            'format':text_format}
        else:
            qa_pairs[level]['Figure-level questions'][tag + adder] = {'Q':q, 'A':a, 
                                                                            'persona':text_persona, 
                                                                            'context':text_context,
                                                                            'question':text_question, 
                                                                            'format':text_format}
        return qa_pairs, False
