# This file is used to automatically 
# add a 'quantity > 0' condition to 
# each unit code in 
# a gold tree database

import pandas as pd
import json
import xlsxwriter as xl
import PySimpleGUI as sg
import datetime as dt
import os

def main():
    sg.theme('DarkTeal2')

    layout = [[sg.T("")],
                [sg.Text("Upload the JSON version of the Interpretation File: "), sg.Input(key="file_path"), sg.FileBrowse(key="file_path_browse")],
                [sg.Text('Please enter the name of this tree: '), sg.Input(key='tree_name')],
                [sg.T("")],
                [sg.Button("Submit", bind_return_key=True), sg.Button('Cancel')]]

    window = sg.Window('Main Menu', layout, size=(800, 180))

    while True:
        event, values = window.Read()
        if event == sg.WIN_CLOSED or event == 'Cancel':
            break
        elif event == 'Submit':
            json_file = values['file_path']
            tree_name = values['tree_name']
            window.close()

    interp_data = json.load(open(json_file))
    new_json_file, dirname = create_files(tree_name)
    new_outcome_data = add_zero_condition(interp_data, tree_name, dirname)
    new_outcome_data_json = new_outcome_data.to_json(orient='records')
    interp_data['outcomes'] = json.loads(new_outcome_data_json)

    for p in range(0, len(interp_data['outcomes'])):
        outcome_clean = cleanNullTerms(interp_data['outcomes'][p])
        interp_data['outcomes'][p] = outcome_clean

    interp_data_json = json.dumps(interp_data)

    with open(new_json_file, 'w') as f:
        f.write(interp_data_json)

def add_zero_condition(json_data, treename, dirname):

    xlpath = dirname+"\\"+treename+'_Affected_CWIs.xlsx'
    workbook = xl.Workbook(xlpath)
    worksheet_0 = workbook.add_worksheet('MASTER')
    worksheet_1 = workbook.add_worksheet('Test 1')
    worksheet_2 = workbook.add_worksheet('Test 2')

    x = 1
    row_0 = 0
    row_1 = 0
    row_2 = 0
    column = 0

    df = pd.DataFrame(json_data['outcomes'])
    #print(df)
    cols = df.columns.to_list()

    for i in range(0, len(df.index)):
        condition_exists = False
        cwi_name = df.loc[i,'name']
        df.at[i, 'name'] = str(cwi_name)  # Conversion added here
        attributes = df.loc[i,'attributes']
        conditions = df.loc[i,'conditions']
        if type(attributes) != dict:
            continue
        else:
            if 'quantity' not in attributes.keys():
                continue
            else:
                if type(attributes['quantity']) != dict:
                    continue
                else:
                    if 'question' in attributes['quantity'].keys():
                        quantity_question_id = attributes['quantity']['question']
                        zero_condition = {'operation': '>', 'args': [{'question': quantity_question_id, 'type': 'number'}, 0]}
                        if type(conditions) != list:
                            conditions = [zero_condition]
                            df.loc[i, 'conditions'] = conditions
                            worksheet_0.write(row_0, column, cwi_name)
                            row_0 += 1
                            if (x % 2) == 0:
                                worksheet_1.write(row_1, column, cwi_name)
                                x += 1
                                row_1 += 1
                            else:
                                worksheet_2.write(row_2, column, cwi_name)
                                x += 1
                                row_2 += 1
                        else:
                            for j in range(0, len(conditions)):
                                if 'operation' in conditions[j].keys():
                                    if [conditions[j]['operation'] == '>' or 
                                        conditions[j]['operation'] == '==' or 
                                        conditions[j]['operation'] == '>=' or
                                        conditions[j]['operation'] == '<=' or
                                        conditions[j]['operation'] == '<' or
                                        conditions[j]['operation'] == '!=']:
                                        args_list = conditions[j]['args']
                                        for k in args_list:
                                            if type(k) != dict:
                                                continue
                                            else:
                                                if quantity_question_id in k.values():
                                                    condition_exists = True
                                                else:
                                                    continue
                                    elif conditions[j]['operation'] != '>':
                                        continue
                                else:
                                    continue
                            if condition_exists == True:
                                continue
                            else:
                                conditions.append(zero_condition)
                                df.loc[i, 'conditions'] = conditions
                                worksheet_0.write(row_0, column, cwi_name)
                                row_0 += 1
                                if (x % 2) == 0:
                                    worksheet_1.write(row_1, column, cwi_name)
                                    x += 1
                                    row_1 += 1
                                else:
                                    worksheet_2.write(row_2, column, cwi_name)
                                    x += 1
                                    row_2 += 1
                    elif 'operation' in attributes['quantity'].keys():
                        custom_quantity_logic = attributes['quantity']
                        zero_condition = {'operation': '>', 'args': [custom_quantity_logic, 0]}
                        if type(conditions) != list:
                            conditions = [zero_condition]
                            df.loc[i, 'conditions'] = conditions
                            worksheet_0.write(row_0, column, cwi_name)
                            row_0 += 1
                            if (x % 2) == 0:
                                worksheet_1.write(row_1, column, cwi_name)
                                x += 1
                                row_1 += 1
                            else:
                                worksheet_2.write(row_2, column, cwi_name)
                                x += 1
                                row_2 += 1
                        else:
                            for j in range(0, len(conditions)):
                                if 'operation' in conditions[j].keys():
                                    if conditions[j]['operation'] == '>':
                                        args_list = conditions[j]['args']
                                        for k in args_list:
                                            if type(k) != dict:
                                                continue
                                            else:
                                                if custom_quantity_logic == k:
                                                    condition_exists = True
                                                else:
                                                    continue
                                    elif conditions[j]['operation'] != '>':
                                        continue
                                else:
                                    continue
                            if condition_exists == True:
                                continue
                            else:
                                conditions.append(zero_condition)
                                df.loc[i, 'conditions'] = conditions
                                worksheet_0.write(row_0, column, cwi_name)
                                row_0 += 1
                                if (x % 2) == 0:
                                    worksheet_1.write(row_1, column, cwi_name)
                                    x += 1
                                    row_1 += 1
                                else:
                                    worksheet_2.write(row_2, column, cwi_name)
                                    x += 1
                                    row_2 += 1
                    else:
                        continue

    if 'definitions' in cols:
        for i in range(0, len(df.index)):
            cwi_name = df.loc[i, 'name']
            definitions = df.loc[i, 'definitions']
            if type(definitions) != list:
                continue
            else:
                for j in range(0, len(definitions)):
                    if 'attributes' in definitions[j].keys() and 'conditions' in definitions[j].keys():
                        d_attrs = definitions[j]['attributes']
                        d_conds = definitions[j]['conditions']
                        d_conds_new, worksheet_0, worksheet_1, worksheet_2, x, row_0, row_1, row_2, column = definition_parser(d_attrs, d_conds, cwi_name, worksheet_0, worksheet_1, worksheet_2, x, row_0, row_1, row_2, column)
                        definitions[j]['conditions'] = d_conds_new
                        df.loc[i, 'definitions'] = definitions
                    elif 'attributes' in definitions[j].keys() and 'conditions' not in definitions[j].keys():
                        definitions[j]['conditions'] = []
                        d_attrs = definitions[j]['attributes']
                        d_conds = definitions[j]['conditions']
                        d_conds_new, worksheet_0, worksheet_1, worksheet_2, x, row_0, row_1, row_2, column = definition_parser(d_attrs, d_conds, cwi_name, worksheet_0, worksheet_1, worksheet_2, x, row_0, row_1, row_2, column)
                        definitions[j]['conditions'] = d_conds_new
                        df.loc[i, 'definitions'] = definitions
                    else:
                        continue

    workbook.close()
            
    return df


def definition_parser(attributes, conditions, unit_name, wrksht_0, wrksht_1, wrksht_2, x, row_0, row_1, row_2, column):
    condition_exists = False

    if type(attributes) == dict:
        if 'quantity' in attributes.keys():
            if type(attributes['quantity']) == dict:
                if 'question' in attributes['quantity'].keys():
                    quantity_question_id = attributes['quantity']['question']
                    zero_condition = {'operation': '>', 'args': [{'question': quantity_question_id, 'type': 'number'}, 0]}
                    if type(conditions) == list:
                        for j in range(0, len(conditions)):
                            if 'operation' in conditions[j].keys():
                                if conditions[j]['operation'] == '>':
                                    args_list = conditions[j]['args']
                                    for k in args_list:
                                        if type(k) != dict:
                                            continue
                                        else:
                                            if quantity_question_id in k.values():
                                                condition_exists = True
                                            else:
                                                continue
                                elif conditions[j]['operation'] != '>':
                                    continue
                            else:
                                continue
                        if condition_exists != True:
                            conditions.append(zero_condition)
                            wrksht_0.write(row_0, column, unit_name)
                            row_0 += 1
                            if (x % 2) == 0:
                                wrksht_1.write(row_1, column, unit_name)
                                x += 1
                                row_1 += 1
                            else:
                                wrksht_2.write(row_2, column, unit_name)
                                x += 1
                                row_2 += 1
                    else:
                        conditions = [zero_condition]
                        wrksht_0.write(row_0, column, unit_name)
                        row_0 += 1
                        if (x % 2) == 0:
                            wrksht_1.write(row_1, column, unit_name)
                            x += 1
                            row_1 += 1
                        else:
                            wrksht_2.write(row_2, column, unit_name)
                            x += 1
                            row_2 += 1
                elif 'operation' in attributes['quantity'].keys():
                    custom_quantity_logic = attributes['quantity']
                    zero_condition = {'operation': '>', 'args': [custom_quantity_logic, 0]}
                    if type(conditions) == list:
                        for j in range(0, len(conditions)):
                            if 'operation' in conditions[j].keys():
                                if conditions[j]['operation'] == '>':
                                    args_list = conditions[j]['args']
                                    for k in args_list:
                                        if type(k) != dict:
                                            continue
                                        else:
                                            if custom_quantity_logic == k:
                                                condition_exists = True
                                            else:
                                                continue
                                elif conditions[j]['operation'] != '>':
                                    continue
                            else:
                                continue
                        if condition_exists != True:
                            conditions.append(zero_condition)
                            wrksht_0.write(row_0, column, unit_name)
                            row_0 += 1
                            if (x % 2) == 0:
                                wrksht_1.write(row_1, column, unit_name)
                                x += 1
                                row_1 += 1
                            else:
                                wrksht_2.write(row_2, column, unit_name)
                                x += 1
                                row_2 += 1
                    else:
                        conditions = [zero_condition]
                        wrksht_0.write(row_0, column, unit_name)
                        row_0 += 1
                        if (x % 2) == 0:
                            wrksht_1.write(row_1, column, unit_name)
                            x += 1
                            row_1 += 1
                        else:
                            wrksht_2.write(row_2, column, unit_name)
                            x += 1
                            row_2 += 1

    return conditions, wrksht_0, wrksht_1, wrksht_2, x, row_0, row_1, row_2, column

def cleanNullTerms(outcome_dict):
    clean = {}
    for k, v in outcome_dict.items():
        if isinstance(v, dict):
            nested = cleanNullTerms(v)
            if len(nested.keys()) > 0:
                clean[k] = nested
        elif v is not None:
            clean[k] = v
    return clean

def create_files(treename):
    dirname=".\\GENERATED_"+treename+"_ZEROCONDITION_"+dt.datetime.now().strftime("%d-%b-%Y-%H%M%S.%f")
    new_json_file = dirname+"\\"+treename+"_NEW.json"
    os.mkdir(dirname)

    return new_json_file, dirname



if __name__=='__main__':
    main()