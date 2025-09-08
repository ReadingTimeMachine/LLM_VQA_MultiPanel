from .plot_qa_utils import get_nplots, persona, context, get_adder


# How many panels in the figure?
def figure_qa_how_many_panels(data, qa_pairs, return_qa=True, verbose=True,
                              #use_words=True, 
                               #single_figure_flag=True, 
                               text_persona = None):

    #nplots = get_nplots(data)

    ### persona of assistant
    text_persona = persona(text=text_persona)
    # context for question
    text_context = '' # full figure

    text_question = 'How many panels are in this figure?'
    text_format = 'Please format the output as a json as {"nrows":"", "ncols":""} to store the number of rows and columns.'
    a1 = {"nrows":data['figure']['nrows'], "ncols":data['figure']['ncols']}
    q = text_persona + " " + text_context + " " + text_question + " " + text_format
    if verbose:
        print('QUESTION:', text_question)
        print('ANSWER:', a1)
        print('')
    # add to pairs
    if return_qa: 
        qa_pairs['Level 1']['Figure-level questions']['rows/columns'] = {'Q':q, 'A':a1, 
                                                                         'persona':text_persona, 
                                                                         'context':text_context, # context nothing for full figure
                                                                         'question':text_question,
                                                                         'format':text_format}
        return qa_pairs
    


# plotting style
def figure_qa_plotting_style(data, qa_pairs, return_qa=True, verbose=True,
                              #use_words=True, 
                               #single_figure_flag=True, 
                               text_persona = None):

    ### persona of assistant
    text_persona = persona(text=text_persona)
    # context for question
    text_context = 'Assuming this is a figure made with matplotlib in Python, what is the plot style used?  Examples of plotting styles are "classic" or "ggplot". Examples of plotting styles are "classic" or "ggplot".' # full figure but context

    text_question = 'What is the plot style used?'
    text_format = 'Please format the output as a json as {"plot style":""} to store the matplotlib plotting style used in the figure.'
    answer = {"plot style":data['figure']['plot style']}
    q = text_persona + " " + text_context + " " + text_question + " " + text_format
    if verbose:
        print('QUESTION:', text_question)
        print('ANSWER:', answer)
        print('')
    # add to pairs
    if return_qa: 
        qa_pairs['Level 1']['Figure-level questions']['plot style'] = {'Q':q, 'A':answer, 
                                                                         'persona':text_persona, 
                                                                         'context':text_context, # context nothing for full figure
                                                                         'question':text_question,
                                                                         'format':text_format}
        return qa_pairs



