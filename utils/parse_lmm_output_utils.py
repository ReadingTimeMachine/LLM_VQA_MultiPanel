import pandas as pd
import json
import pickle
import numpy as np
from copy import deepcopy


def parse_first_json(text):
    decoder = json.JSONDecoder()
    obj, idx = decoder.raw_decode(text)
    return obj

def parse_json_files(dirnames, dirs, files_parsed, dir_jsons, 
                     verbose=True):
    dfdict = {}
    for flag in ['image id', 'plot number', 'plot type', 'question', 
                'use list', 'model', 'model id', 'LMM Answer', 'GT Answer', 
                'Level', 'Level Type']: #, 'plot types']:
        dfdict[flag] = []
    for ifile,(dn,dr) in enumerate(zip(dirnames, dirs)):
        if verbose:
            print('')
            print('***********', dn, '****************')
            print('')
        for f in files_parsed:
            if verbose: print("-----------", f, '------------')

            # read in full data for some extra info
            with open(dir_jsons + f.removesuffix('.pickle')+'.json', 'r') as ff:
                j = json.load(ff)
                jfd = json.loads(j)
                #import sys; sys.exit()

            with open(dr + '/' + f,'rb') as ff:
                data,  model = pickle.load(ff)

            # loop through q/a
            for qa in data:
                # make row/file
                dfdict['image id'].append(f.removesuffix('.pickle'))
                dfdict['question'].append(qa['question'])
                dfdict['model'].append(dn)
                dfdict['model id'].append(model)
                dfdict['Level'].append(qa['Level'])
                dfdict['Level Type'].append(qa['type'])
                if 'plot number' in qa: # not figure-level
                    dfdict['plot number'].append(int(qa['plot number'].split('plot')[-1]))
                    dfdict['plot type'].append(jfd[qa['plot number']]['type'])
                else:
                    dfdict['plot type'].append(None)
                    dfdict['plot number'].append(None)
                use_list = False
                if 'choose' in qa['format']:
                    use_list = True
                elif 'please choose ' in qa['context'].lower():
                    use_list = True
                dfdict['use list'].append(use_list)
                # try loading response
                try:
                    jgt = qa['A']
                except:
                    print('no GT answer!')
                    import sys; sys.exit()
                # if string/number answer
                if type(jgt) != type({}):
                    q = qa['Q'] # {"npoints":""}
                    q = q.split('{')[-1].split('}')[0]
                    q = q.split(':')[0].replace('"','').replace("'",'')
                    #print(q)
                    #import sys; sys.exit()
                    jgt = {q:jgt}
                # llm
                raw_ans = qa['raw answer']
                jllm = {}
                if '`' not in raw_ans:
                    try:
                        jllm = json.loads(raw_ans)
                    except:
                        # try splitting
                        if '{' in raw_ans and '}' in raw_ans:
                            a = '{' + raw_ans.split('{')[-1].split('}')[0] + '}'
                            try:
                                jllm = json.loads(a)
                            except:
                                if verbose: print('could not load answer for non `:', raw_ans)
                                #fslkfjs
                                if verbose: print('')
                                jllm[list(jgt.keys())[0]] = np.nan
                elif '```json\n' in raw_ans:
                    try:
                        a = raw_ans.split('```json\n')[-1].split('```')[0]
                        jllm = json.loads(a)
                    except Exception as e:
                        if "Expecting ',' delimiter" in str(e):
                            if verbose: print('[ERROR]: json decode error -- ', str(e))
                            jllm[list(jgt.keys())[0]] = np.nan
                            if verbose: print('')
                        elif 'Unterminated string' in str(e):
                            if verbose: print('[ERROR]: json decode error -- ', str(e))
                            jllm[list(jgt.keys())[0]] = np.nan
                            if verbose: print('')
                        elif 'Expecting value:' in str(e):
                            if verbose: print('[ERROR]: json decode error -- ', str(e))
                            jllm[list(jgt.keys())[0]] = np.nan
                            if verbose: print('')
                        elif 'Invalid \\escape' in str(e):
                            try:
                                a = raw_ans.split('```json\n')[-1].split('```')[0]
                                a = a.replace('\\\\', '\\')
                                jllm = json.loads(a)
                            except Exception as e2:
                                if verbose: print('[ERROR]: json decode error, t2 -- ', str(e2))
                                if 'Invalid \\escape' in str(e2):
                                    jllm[list(jgt.keys())[0]] = np.nan
                                else:
                                    fjffj
                        elif 'Extra data:' in str(e):
                            try:
                                jllm = parse_first_json(raw_ans.split('```json\n')[-1].split('```')[0])
                            except Exception as e2:
                                if verbose: print('[ERROR]: json decode error --', str(e2))
                                jllm[list(jgt.keys())[0]] = np.nan
                        elif 'Expecting property name enclosed in double quotes:' in str(e):
                            if verbose: print('[ERROR]: json decode error --', str(e))
                            jllm[list(jgt.keys())[0]] = np.nan
                        elif 'Invalid control character at:' in str(e):
                            if verbose: print('[ERROR]: json decode error --', str(e))
                            jllm[list(jgt.keys())[0]] = np.nan
                        else:
                            print('could not load answer, 2:', raw_ans)
                            sljfsl
                else:
                    print('not sure:')
                    print(raw_ans)
                    import sys; sys.exit()

                # known issues
                if 'titles' in jllm:
                    j2 = {'title':jllm['titles']}
                    jllm = deepcopy(j2)
                if 'aspect ratio' in jllm:
                    if ':' in jllm['aspect ratio']:
                        ar = float(jllm['aspect ratio'].split(':')[0])/float(jllm['aspect ratio'].split(':')[1])
                        jllm['aspect ratio'] = ar

                # test for matching keys
                for k,v in jgt.items():
                    if k not in jllm:
                        if verbose:
                            print('missing key:', k)
                            print('question format:', qa['format'])
                            print('GT:', jgt)
                            print('LMM:', jllm)
                        jllm[k] = np.nan
                        #import sys; sys.exit()
                    elif type(jllm[k]) != type(v):
                        if jllm[k] is None:
                            continue
                        try:
                            a = type(v)(jllm[k])
                            #print('type', type(v), 'for', jllm[k])
                            jllm[k] = a
                        except:
                            try:
                                x = np.isnan(jllm[k])
                            except:
                                try:
                                    x = jllm[k].split(' ')[-1]
                                    a = type(v)(x)
                                    jllm[k] = a
                                except:
                                    if verbose:
                                        print('different types of values:')
                                        print('GT:', v, type(v))
                                        print('LLM:', jllm[k], type(jllm[k]))
                                    if type(jllm[k]) == type(''):
                                        jllm[k] = None
                                    else:
                                        laksjl
                            #import sys; sys.exit()
                # drop non-presents
                jllm_tmp = deepcopy(jllm)
                for k,v in jllm_tmp.items():
                    if k not in jgt:
                        del jllm[k]

                dfdict['LMM Answer'].append(jllm)
                dfdict['GT Answer'].append(jgt)
                    
                
    df = pd.DataFrame(dfdict)
    return df



# assume order is relatively correct -- associate closest to gt
from Levenshtein import distance as levenshtein_distance # Assuming you have python-Levenshtein installed

# sweet little algo to do associations
def map_lg_gt(l,g, verbose=True):
    g_index = 0
    l_gt_map_index = []
    for ll in l:
        darr = []
        for gg in g:
            darr.append(levenshtein_distance(gg, ll))
        darr = np.array(darr)[g_index:]
        if len(darr) == 0:
            import sys; sys.exit()
        min_ind = np.argmin(darr) + g_index
        l_gt_map_index.append(min_ind)
        #print('min_ind, g_index', min_ind, g_index)
        g_index = min_ind

    # see if any double counted
    skipMap = False; warning = False
    if len(np.unique(l_gt_map_index)) != len(l_gt_map_index):
        if len(np.unique(l_gt_map_index)) == 1: # just one option
            skipMap = True
            l_mapped = deepcopy(l)
            l_mapped = np.array(l_mapped).tolist()
            while len(l_mapped) < len(g):
                l_mapped.append('')
            l_mapped = np.array(l_mapped)
        else:
            warning = True
            if verbose: print('[WARNING]: dont have solution for non uniques! (gt)')
            #import sys; sys.exit()

    if not skipMap:
        l_mapped = []
        for i in range(len(g)):
            if i in l_gt_map_index:
                l_mapped.append(l[l_gt_map_index.index(i)])
            else:
                l_mapped.append('')

    g_mapped = deepcopy(g)

    if warning and verbose:
        for gm,lm in zip(g_mapped,l_mapped):
            if gm == '': gm = '<EMPTY>'
            if lm == '': lm = '<EMPTY>'
            print(gm, '||', lm)
        print('')

    return l_mapped, g_mapped


def map_lg_lt(l_save, g_save, verbose=True):
    # swap and loop
    g = deepcopy(l_save)
    l = deepcopy(g_save)

    g_index = 0
    l_gt_map_index = []
    g_nospace = []
    maxl = -1
    for ill,ll in enumerate(l):
        if ll.replace(' ', '') == '':
            continue
        darr = []
        g_nospace.append(ll)
        if len(ll) > maxl: maxl = len(ll)
        for gg in g:
            darr.append(levenshtein_distance(gg, ll))

        darr = np.array(darr)[g_index:]
        if len(darr) == 0:
            import sys; sys.exit()
        min_ind = np.argmin(darr) + g_index
        l_gt_map_index.append(min_ind)
        #print('min_ind, g_index', min_ind, g_index)
        g_index = min_ind

    skipMap = False; warning = False
    if len(np.unique(l_gt_map_index)) != len(l_gt_map_index):
        if len(np.unique(l_gt_map_index)) == 1: # just one option
            skipMap = True
            g_mapped = deepcopy(g_save)
            g_mapped = np.array(g_mapped).tolist()
            while len(g_mapped) < len(l_save):
                g_mapped.append('')
            g_mapped = np.array(g_mapped)
        else:
            warning = True
            if verbose: print('[WARNING]: dont have solution for non uniques! (lt)')
            #import sys; sys.exit()

    if not skipMap:
    # loop and fill g
        g_mapped = np.repeat('', len(l_save)).astype('<U'+str(maxl+1))
        for i in range(len(l_save)):
            if i in l_gt_map_index:
                g_mapped[i] = g_nospace[l_gt_map_index.index(i)]

    l_mapped = deepcopy(l_save)

    if warning and verbose:
        for gm,lm in zip(g_mapped,l_mapped):
            if gm == '': gm = '<EMPTY>'
            if lm == '': lm = '<EMPTY>'
            print(gm, '||', lm)
        print('')

    return l_mapped, g_mapped



def calc_iqr(diff1):
    diff1 = np.array(diff1)
    diff1 = diff1[~np.isnan(diff1)]
    q1 = np.percentile(diff1, 25)
    q3 = np.percentile(diff1, 75)
    iqr = q3 - q1
    return iqr

def count_nan(lmm):
    lmm = np.array(lmm)
    calc_nan = np.array(lmm)
    try:
        calc_nan = len(calc_nan[np.isnan(calc_nan)])    
    except:
        calc_nan = len(calc_nan[calc_nan == None])
    return calc_nan


def get_lmm_gt(dfsub2, type, verbose=True):
    if type == 'binary string':
        gt = []; lmm = []
        for v in dfsub2['GT Answer'].values:
            gt.append(list(v.values())[0].lower())
        gt = np.array(gt)
        for v in dfsub2['LMM Answer'].values:
            lmm.append(list(v.values())[0].lower())
        lmm = np.array(lmm)
    elif type == 'float' or type == 'float per panel':
        gt = []; lmm = []
        for v in dfsub2['GT Answer'].values:
            gt.append(list(v.values())[0])
        gt = np.array(gt)
        for v in dfsub2['LMM Answer'].values: # v = {'mean': 5.0}
            l = list(v.values())[0]
            if l is None:
                l = np.nan
            lmm.append(l)
        lmm = np.array(lmm)
        gt = np.array(gt)
    elif type == 'string list' or type == 'binary string list':
        gt = []; lmm = []
        # have to do at same time to match lists
        for vgt,vlmm in zip(dfsub2['GT Answer'].values, dfsub2['LMM Answer'].values):
            k = list(vgt.keys())[0]
            g = vgt[k]
            l = vlmm[k]
            try:
                # same lenghts?
                if len(g) > len(l):
                    lmapped,gmapped = map_lg_gt(deepcopy(l),deepcopy(g), verbose=verbose)
                elif len(g) < len(l):
                    lmapped,gmapped = map_lg_lt(deepcopy(l),deepcopy(g), verbose=verbose)
                elif len(g) == len(l):
                    lmapped = deepcopy(l)
                    gmapped = deepcopy(g)  
            except:
                if np.isnan(l):
                    lmapped = np.repeat('', len(g))
                    gmapped = deepcopy(g)
                else:
                    print('cannot figure this out!')
                    lakdsjl

            for gg,ll in zip(gmapped,lmapped): # lower
                if '<EMPTY>' in gg: 
                    print("!!!!!!!!!!!!!! ERROR ERROR ERROR !!!!!!!!!!!!!")
                    import sys; sys.exit()
                gt.append(gg)
                lmm.append(ll)      

        # print('NO IMPLEMENTATION', type)
        # import sys; sys.exit()

    return gt, lmm