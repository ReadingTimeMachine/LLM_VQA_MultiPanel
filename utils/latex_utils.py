def table_iConf_format(df_figure, label, caption, column_format):
    df_fout = df_figure.copy()

    #df.rename(columns={'old_col_a': 'new_col_x'}, inplace=True)
    names = {}
    for n in df_figure.columns:
        names[n] = '\\color{white} ' + n

    df_fout.rename(columns=names, inplace=True)

    latex_table = df_fout.to_latex(index=False, 
                                    column_format=column_format, caption=caption)

    latex_table = latex_table.replace('\\caption{'+caption+'}\n', '')
    latex_table = latex_table.replace('\\begin{table}', '\\begin{table}[h!]')
    latex_table = latex_table.replace('\\toprule', '\\hline\n\\rowcolor{black}')
    latex_table = latex_table.replace('\\bottomrule\n','') 
    #latex_table = latex_table.replace('\\end{tabular}\n','\\end{tabular}\n\\centering\n\\caption*{'+caption+"}\n\\label{"+label+'}\n') # replace with label and caption
    latex_table = latex_table.replace('\\end{tabular}\n','\\end{tabular}\n\\centering\n\\caption{'+caption+"}\n\\label{"+label+'}\n') # replace with label and caption
    latex_table = latex_table.replace('\\midrule', '\\hline')
    latex_table = latex_table.replace('\\\\\n', '\\\\ \\hline\n')
    latex_table = latex_table.replace('\\hline\n\\hline\n', '\n\\hline\n')
    return latex_table