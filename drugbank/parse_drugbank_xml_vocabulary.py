# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 11:56:18 2020

Parse full_database.xml file from DrugBank.ca

@author: Tianqi
"""
#%%
xml_file = '../data/full database.xml'
import collections
import xml.etree.ElementTree as etree
import pandas as pd
import os    

import json
#%%

rows = list()
ns = '{http://www.drugbank.ca}'
protein_rows = list()
inchikey_template = "{ns}calculated-properties/{ns}property[{ns}kind='InChIKey']/{ns}value"
inchi_template = "{ns}calculated-properties/{ns}property[{ns}kind='InChI']/{ns}value"
for event, elem in etree.iterparse(xml_file, events=('start','end')): ### iterate all elements
    ##### find </drug type='biotech'> element, event='end' is corresponding to event ='start', but elemnt size is
    #### mostly dependent on 'end'
    if event == 'end' and '{http://www.drugbank.ca}drug' == elem.tag and 'type' in elem.attrib:   
        row = collections.OrderedDict()

        assert elem.tag == ns + 'drug'
        drugbank_id = elem.findtext(ns + "drugbank-id[@primary='true']")
        row['drugbank_id'] = drugbank_id
        row['type'] = elem.get('type')        
        row['name'] = elem.findtext(ns + "name")
        row['description'] = elem.findtext(ns + "description")
        row['indication'] = elem.findtext(ns + 'indication')
        row['pharmacology'] = elem.findtext(ns + 'pharmacodynamics')
        row['groups'] = [group.text for group in
            elem.findall("{ns}groups/{ns}group".format(ns = ns))]
        row['atc_codes'] = [code.get('code') for code in            elem.findall("{ns}atc-codes/{ns}atc-code".format(ns = ns))]
        row['atc_level_code'] = [code.get('code') for code in
            elem.findall("{ns}atc-codes/{ns}atc-code/{ns}level".format(ns = ns))]
        row['categories'] = [x.findtext(ns + 'category') for x in
            elem.findall("{ns}categories/{ns}category".format(ns = ns))]
        row['inchi'] = elem.findtext(inchi_template.format(ns = ns))
        row['inchikey'] = elem.findtext(inchikey_template.format(ns = ns))
        
        # Add drug aliases
        aliases = {
            elem.text for elem in 
            elem.findall("{ns}international-brands/{ns}international-brand".format(ns = ns)) +
            elem.findall("{ns}synonyms/{ns}synonym[@language='English']".format(ns = ns)) +
            elem.findall("{ns}international-brands/{ns}international-brand".format(ns = ns)) +
            elem.findall("{ns}products/{ns}product/{ns}name".format(ns = ns))
    
        }
        aliases.add(row['name'])
        row['aliases'] = sorted(aliases)
    
        rows.append(row)
        elem.clear()
        
#%%        
alias_dict = {row['drugbank_id']: row['aliases'] for row in rows}
with open(os.path.join(os.getcwd(), 'aliases.json'), 'w+') as fp:
    json.dump(alias_dict, fp, indent=2, sort_keys=True)    
#%%
def collapse_list_values(row):
    for key, value in row.items():
        if isinstance(value, list):
            row[key] = '|'.join(value)
    return row

rows = list(map(collapse_list_values, rows))        

#%%

columns = ['drugbank_id', 'name', 'type', 'groups', 'atc_codes','atc_level_code', 'categories', 'inchikey', 'inchi',\
           'indication','pharmacology','description']
drugbank_df = pd.DataFrame.from_dict(rows)[columns]
##%% remove some non-small molecule
#drugbank_slim_df = drugbank_df[
#    drugbank_df.groups.map(lambda x: 'approved' in x) &
#    drugbank_df.inchi.map(lambda x: x is not None) &
#    drugbank_df.type.map(lambda x: x == 'small molecule')
#]
#drugbank_slim_df.head()

# write drugbank tsv
drugbank_df.to_csv('../data/drugbank_full_Drugs.tsv', sep='\t', index=False)