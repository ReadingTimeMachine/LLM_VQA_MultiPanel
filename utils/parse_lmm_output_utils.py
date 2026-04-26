import pandas as pd
import json
import pickle
import numpy as np
from copy import deepcopy
import re
import ast

PLACEHOLDER = "PARSE_ERROR"

def parse_llm_dual_json(
    output: str,
    expected_keys: list[str] | None = None
) -> tuple[str | None, dict | None]:
    """
    Parse LLM output containing an answer JSON and optional explanation JSON.

    Args:
        output: Raw LLM output string
        expected_keys: Optional list of keys the answer dict should contain.
                       If provided and answer doesn't match, returns PLACEHOLDER.

    Returns:
        (answer_str, explanation_dict)
        answer_str is PLACEHOLDER if parsing fails or schema doesn't match.
    """
    output = output.strip()

    def extract_json_objects(text):
        objects = []
        depth = 0
        start = None
        in_string = False
        escape_next = False

        for i, ch in enumerate(text):
            if escape_next:
                escape_next = False
                continue
            if ch == '\\' and in_string:
                escape_next = True
                continue
            if ch == '"' and not escape_next:
                in_string = not in_string
            if in_string:
                continue
            if ch == '{':
                if depth == 0:
                    start = i
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and start is not None:
                    objects.append(text[start:i+1])
                    start = None
        return objects

    def fix_mismatched_braces(obj_str: str) -> str:
        """Replace mismatched closing braces/brackets."""
        # Count opens vs closes for each type
        open_curly = obj_str.count('{')
        close_curly = obj_str.count('}')
        open_square = obj_str.count('[')
        close_square = obj_str.count(']')

        # Build a corrected string by walking and tracking a stack
        stack = []
        result = []
        in_string = False
        escape_next = False

        for ch in obj_str:
            if escape_next:
                escape_next = False
                result.append(ch)
                continue
            if ch == '\\' and in_string:
                escape_next = True
                result.append(ch)
                continue
            if ch == '"' and not escape_next:
                in_string = not in_string
                result.append(ch)
                continue
            if in_string:
                result.append(ch)
                continue

            if ch == '{':
                stack.append('}')
                result.append(ch)
            elif ch == '[':
                stack.append(']')
                result.append(ch)
            elif ch in ('}', ']'):
                if stack and stack[-1] == ch:
                    stack.pop()
                    result.append(ch)
                elif stack and stack[-1] != ch:
                    # Wrong closer — use the expected one instead
                    result.append(stack.pop())
                # else: extra closer with empty stack, drop it
            else:
                result.append(ch)

        # Close anything left open
        while stack:
            result.append(stack.pop())

        return ''.join(result)

    def try_parse(obj_str: str) -> dict | None:
        # 1. Strict parse
        try:
            return json.loads(obj_str)
        except json.JSONDecodeError:
            pass

        # 2. Fix mismatched braces/brackets then retry
        try:
            fixed = fix_mismatched_braces(obj_str)
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

        # 3. Strip trailing commas
        try:
            fixed = re.sub(r',\s*([}\]])', r'\1', obj_str)
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

        # 4. Single quotes only (when no double quotes present)
        if '"' not in obj_str:
            try:
                fixed = re.sub(r"'", '"', obj_str)
                return json.loads(fixed)
            except json.JSONDecodeError:
                pass

        # 5. Stray mid-token quotes
        try:
            fixed = re.sub(r'(?<=[^\s,:\[{])\"(?=[^\s,:\]}\:])', '', obj_str)
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

        # 6. ast.literal_eval fallback
        try:
            result = ast.literal_eval(obj_str)
            if isinstance(result, dict):
                return result
        except (ValueError, SyntaxError):
            pass

        return None

    def split_combined(obj: dict, explanation_keys: set) -> tuple[dict | None, dict | None]:
        expl = {k: v for k, v in obj.items() if k in explanation_keys}
        ans = {k: v for k, v in obj.items() if k not in explanation_keys}
        return (ans if ans else None), (expl if expl else None)

    def validate_answer(ans: dict | None, expected_keys: list[str] | None) -> bool:
        """Check answer has expected keys and non-empty values."""
        if ans is None:
            return False
        if expected_keys is None:
            return True  # No schema to check against
        return all(k in ans and ans[k] not in (None, "", [], {}) for k in expected_keys)

    explanation_keys = {"explanation", "reason", "reasoning", "rationale"}
    raw_objects = extract_json_objects(output)

    parsed = []
    for obj_str in raw_objects:
        candidate = try_parse(obj_str)
        if candidate is not None:
            parsed.append(candidate)

    answer, explanation = None, None

    if len(parsed) == 0:
        pass

    elif len(parsed) == 1:
        obj = parsed[0]
        has_explanation = any(k in obj for k in explanation_keys)
        has_answer = any(k not in explanation_keys for k in obj)

        if has_explanation and has_answer:
            answer, explanation = split_combined(obj, explanation_keys)
        elif has_explanation:
            explanation = obj
        else:
            answer = obj

    else:
        for obj in parsed:
            if any(k in obj for k in explanation_keys):
                explanation = obj
            else:
                answer = obj

    # Validate answer against expected schema
    if not validate_answer(answer, expected_keys):
        answer_str = PLACEHOLDER
    else:
        answer_str = json.dumps(answer)

    return answer_str, explanation






########### HERE #############

def parse_first_json(text):
    decoder = json.JSONDecoder()
    obj, idx = decoder.raw_decode(text)
    return obj

# claude suggestions for fixing slashes
# Replace single backslashes with double backslashes in JSON strings
def fix_json_escapes(json_str):
    # This pattern finds backslashes that aren't already properly escaped
    return re.sub(r'(?<!\\)\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r'\\\\', json_str)

def fix_raw_strings(json_str):
    # Remove r" prefixes and escape backslashes in the content
    def replace_raw_string(match):
        content = match.group(1)
        # Escape backslashes
        escaped_content = content.replace('\\', '\\\\')
        return f'"{escaped_content}"'
    
    # Find r"..." patterns and replace them
    return re.sub(r'r"([^"]*)"', replace_raw_string, json_str)

# Or more comprehensive - escape all single backslashes before letters
def fix_all_latex(json_str):
    return re.sub(r'(?<!\\)\\(?=[a-zA-Z])', r'\\\\', json_str)

def fix_latex_math(json_str):
    # Add quotes around $...$ expressions
    return re.sub(r'\$([^$]+)\$', r'"\$\1\$"', json_str)


def parse_json_files(dirnames, dirs, files_parsed, dir_jsons, 
                     verbose=True, use_explanation=False, ignore_please_choose=True):
    dfdict = {}
    for flag in ['image id', 'plot number', 'plot type', 'question', 
                'use list', 'model', 'model id', 'LMM Answer', 'GT Answer', 
                'Level', 'Level Type']: #, 'plot types']:
        dfdict[flag] = []
    if use_explanation:
        dfdict['Explanation'] = []
    for ifile,(dn,dr) in enumerate(zip(dirnames, dirs)):
        if verbose:
            print('')
            print('****************************************')
            print('***********', dn, '****************')
            print('****************************************')
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
                question = qa['question']
                if ignore_please_choose:
                    question = question.split('Please choose from ')[0].rstrip().lstrip()
                dfdict['question'].append(question)
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
                raw_ans_in = qa['raw answer']
                # print("RAW ANS")
                # print(raw_ans_in)
                if use_explanation: # has explaination and needs to be stripped
                    answer, explanation = parse_llm_dual_json(raw_ans_in)
                    raw_ans_in = answer #str(answer)
                    
                # print("OUTPUT")
                # print(raw_ans_in)#, type(raw_ans_in))
                # print('exp')
                # print(explanation)
                # import sys; sys.exit()
                jllm = {}
                raw_ans = raw_ans_in.replace('^', 'e') # math notation
                raw_ans = raw_ans.replace('**','e')
                raw_ans = re.sub(r'(\d*\.?\d+e)\s*\(\s*-\s*(\d+)\s*\)', r'\1-\2', raw_ans)
                raw_ans = raw_ans.replace('True', 'true').replace('False', 'false')
                raw_ans = raw_ans.replace('\u2212', '-')
                #print('raw_ans', raw_ans)
                if '`' not in raw_ans:
                    try:
                        jllm = json.loads(raw_ans)
                    except:
                        # try splitting
                        if '{' in raw_ans and '}' in raw_ans:
                            a = '{' + raw_ans.split('{')[-1].split('}')[0] + '}'
                            try:
                                jllm = json.loads(a)
                            except Exception as esplit:
                                if verbose: 
                                    print('[ERROR]: could not load answer for this json :', a)
                                    print('  full exception:', str(esplit))
                                #fslkfjs
                                if verbose: print('')
                                jllm[list(jgt.keys())[0]] = np.nan
                elif '```json\n' in raw_ans:
                    try:
                        a = raw_ans.split('```json\n')[-1].split('```')[0]
                        jllm = json.loads(a)
                    except Exception as e:
                        if "Expecting ',' delimiter" in str(e):
                            if verbose: 
                                print('[ERROR]: json decode error (delimiter) -- ', str(e))
                                print('   json:', a)
                            jllm[list(jgt.keys())[0]] = np.nan
                            if verbose: print('')
                        elif 'Unterminated string' in str(e):
                            if verbose: 
                                print('[ERROR]: json decode error (unterminated string) -- ', str(e))
                                print('   json:', a)
                            jllm[list(jgt.keys())[0]] = np.nan
                            if verbose: print('')
                        elif 'Expecting value:' in str(e):
                            try:
                                a = raw_ans.split('```json\n')[-1].split('```')[0]
                                a = fix_raw_strings(a)
                                jllm = json.loads(a)
                            except Exception as e2:
                                try:
                                    a = raw_ans.split('```json\n')[-1].split('```')[0]
                                    a = fix_raw_strings(a)
                                    a = fix_all_latex(a)
                                    jllm = json.loads(a)
                                except Exception as e22:
                                    try:
                                        a = raw_ans.split('```json\n')[-1].split('```')[0]
                                        a = fix_raw_strings(a)
                                        a = fix_latex_math(a)
                                        jllm = json.loads(a)
                                    except Exception as e222:
                                        if verbose: 
                                            print('[ERROR]: json decode error (expecting value, t22) -- ', str(e222))
                                            print('   json:', a)
                                        jllm[list(jgt.keys())[0]] = np.nan
                                        if verbose: print('')
                        elif 'Invalid \\escape' in str(e):
                            try:
                                a = raw_ans.split('```json\n')[-1].split('```')[0]
                                a = a.replace('\\\\', '\\')
                                jllm = json.loads(a)
                            except Exception as e2:
                                try:
                                    a = raw_ans.split('```json\n')[-1].split('```')[0]
                                    a = a.replace('\\\\', '\\')
                                    a = fix_json_escapes(a)
                                    jllm = json.loads(a)
                                except Exception as e22:
                                    if verbose: 
                                        print('[ERROR]: json decode error, t3 -- ', str(e22))
                                        print('   json:', a)
                                # if 'Invalid \\escape' in str(e2):
                                #     jllm[list(jgt.keys())[0]] = np.nan
                                # else:
                                #     fjffj
                        elif 'Extra data:' in str(e):
                            try:
                                jllm = parse_first_json(raw_ans.split('```json\n')[-1].split('```')[0])
                            except Exception as e2:
                                if verbose: 
                                    print('[ERROR]: json decode error (extra data) --', str(e2))
                                    print('   json:', a)
                                jllm[list(jgt.keys())[0]] = np.nan
                        elif 'Expecting property name enclosed in double quotes:' in str(e):
                            if verbose: 
                                print('[ERROR]: json decode error (double quotes) --', str(e))
                                print('   json:', a)
                            jllm[list(jgt.keys())[0]] = np.nan
                        elif 'Invalid control character at:' in str(e):
                            if verbose: 
                                print('[ERROR]: json decode error (invalid control char) --', str(e))
                                print('   json:', a)
                            jllm[list(jgt.keys())[0]] = np.nan
                        else:
                            print('could not load answer, 2:', raw_ans)
                            sljfsl
                else:
                    print('not sure:')
                    print(raw_ans)
                    import sys; sys.exit()

                # known issues
                # if 'titles' in jllm:
                #     j2 = {'title':jllm['titles']}
                #     jllm = deepcopy(j2)
                # if 'title' in jllm and 'titles' in list(jgt.keys):
                #     print('[WARNING]: gt is "titles" but return from LMM is "title", doing a sub')
                
                if 'aspect ratio' in jllm:
                    if "(" in jllm['aspect ratio']:
                        jllm['aspect ratio'] = jllm['aspect ratio'].split('(')[0]
                    if ':' in jllm['aspect ratio']:
                        ar = float(jllm['aspect ratio'].split(':')[0])/float(jllm['aspect ratio'].split(':')[1])
                        jllm['aspect ratio'] = ar

                # specific errors for keys that have lists
                replace_keys = []
                hasList = False
                for kllm,vllm in jllm.items():
                    for kgt, vgt in jgt.items():
                        if ' (list)' in kgt:
                            hasList = True
                            if kgt.replace(' (list)','') == kllm:
                                replace_keys.append({kgt:vllm})
                if hasList:
                    #print("HAS LIST")
                    #import sys; sys.exit()
                    replace_keys2 = []
                    for r in replace_keys:
                        if r not in replace_keys2:
                            replace_keys2.append(r)
                    if len(replace_keys2) != 1: # not sure what to do!
                        print('replace_keys2:', replace_keys2)
                        print('replace_keys:', replace_keys)
                        print('jgt:',jgt)
                        print('jllm:',jllm)
                        import sys; sys.exit()
                    replace_keys = replace_keys2[0]
                    jllm = deepcopy(replace_keys)

                # test for matching keys
                for k,v in jgt.items():
                    if k not in jllm:
                        if verbose:
                            print('[ERROR]: missing key:', k)
                            print('  question format:', qa['format'])
                            print('  GT:', jgt)
                            print('  LMM:', jllm)
                            print('  raw LMM:', raw_ans_in.split('\n')[0])
                            print('')
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
                                    # try for floats
                                    try:
                                        if type(v) == type(1.0) and type(jllm[k]) == type('string'):
                                            if '/' in jllm[k]:
                                                tofloat = float(jllm[k].split('/')[0])*1.0/float(jllm[k].split('/')[-1])
                                            else:
                                                tofloat = None
                                        else:
                                            tofloat = None
                                        if type(v) == type(1.0) and '~' in str(jllm[k]) and type(jllm[k]) == type('string') and tofloat is None:
                                            try:
                                                tofloat = float(jllm[k].replace('~',''))
                                            except:
                                                tofloat = None
                                        if tofloat is None:
                                            print('[ERROR]: different types of values, could not fix:')
                                            print('  GT:', v, type(v))
                                            print('  LLM:', jllm[k], type(jllm[k]))
                                            print('  raw LLM:', raw_ans_in.split('\n')[0])
                                            print('')
                                        jllm[k] = tofloat
                                    except:
                                        if verbose:
                                            print('[ERROR]: different types of values:')
                                            print('  GT:', v, type(v))
                                            print('  LLM:', jllm[k], type(jllm[k]))
                                            print('  raw LLM:', raw_ans_in.split('\n')[0])
                                            print('')
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
                if use_explanation:
                    dfdict['Explanation'].append(explanation)
                    
                
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


def align_arrays_safe(arr1, arr2):
    n, m = len(arr1), len(arr2)
    assert m <= n, "arr2 cannot be longer than arr1 (can only insert, not delete)"

    INF = float('inf')
    dp = np.full((n + 1, m + 1), INF)
    choice = np.zeros((n + 1, m + 1), dtype=int)  # 0=match, 1=insert NaN
    
    for i in range(n + 1):
        dp[i][0] = 0.0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost_match = dp[i-1][j-1] + abs(arr1[i-1] - arr2[j-1])
            cost_insert = dp[i-1][j]
            if cost_match <= cost_insert:
                dp[i][j] = cost_match
                choice[i][j] = 0  # match
            else:
                dp[i][j] = cost_insert
                choice[i][j] = 1  # insert NaN

    # Traceback
    aligned = []
    i, j = n, m
    while i > 0:
        if j > 0 and choice[i][j] == 0:
            aligned.append(arr2[j-1])
            i -= 1; j -= 1
        else:
            aligned.append(np.nan)
            i -= 1

    aligned.reverse()
    return np.array(aligned)


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
            g = list(v.values())[0]
            if isinstance(g,list):
                gt.extend(g)
            else:
                gt.append(g)
        #print('GT:',gt)
        gt = np.array(gt)
        for v in dfsub2['LMM Answer'].values: # v = {'mean': 5.0}
            l = list(v.values())[0]
            if l is None:
                l = np.nan
            if isinstance(l,list):
                lmm.extend(l)
            else:
                lmm.append(l)
        #print('LMM:', lmm)
        lmm = np.array(lmm)
        gt = np.array(gt)
        if len(lmm) < len(gt):
            lmm = align_arrays_safe(gt, lmm)
        else:
            #print('WONT WORK')
            if verbose:
                print('[WARNING]: have to delete GT to align')
            gt = align_arrays_safe(lmm,gt)
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