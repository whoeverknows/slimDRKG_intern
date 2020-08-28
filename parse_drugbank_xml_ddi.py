# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 14:28:37 2020

@author: Tianqi
"""

xml_file = '../data/full database.xml'
import collections
import xml.etree.ElementTree as etree
import pandas as pd 
import os    


ns = '{http://www.drugbank.ca}'
ddi_rows = list()
cnt =0 
for event, elem in etree.iterparse(xml_file, events=('start','end')): ### iterate all elements
    ##### find </drug type='biotech'> element, event='end' is corresponding to event ='start', but elemnt size is
    #### mostly dependent on 'end'
    if event == 'end' and '{http://www.drugbank.ca}drug' == elem.tag and 'type' in elem.attrib:   

        drugbank_id = elem.findtext(ns + "drugbank-id[@primary='true']")
        drug_interaction = elem.findall('{ns}{cat}s/{ns}{cat}'.format(ns=ns, cat='drug-interaction'))
        
        if len(drug_interaction):                
            for ddi in drug_interaction:
                row = collections.OrderedDict()
                row['drugbank_id'] = drugbank_id

                row['ddi_id'] = ddi.findtext('{}drugbank-id'.format(ns))

                ddi_rows.append(row)
        elem.clear()
        
drug_ddi_df = pd.DataFrame.from_dict(ddi_rows)  

#%%
#remove duplicated pairs
drug_ddi_newdf_2 = list()
for idx in range(len(drug_ddi_df)): #range(len(drug_ddi_df))
    pair = (drug_ddi_df.loc[idx][0], drug_ddi_df.loc[idx][1])
    drug_ddi_newdf_2.append(tuple(sorted(pair)))

drug_ddi_newdf_1 = list(set(drug_ddi_newdf_2))
df_update = pd.DataFrame(drug_ddi_newdf_1, columns = ['drugbank_id', 'drugbank_id'])
df_update.to_csv('../data/drugbank_compound_ddi.tsv', sep='\t', index=False)


#%%
####### get triplets of compound--compound pairs
ddi_df = pd.read_csv( '../data/drugbank_compound_ddi.tsv', delimiter='\t')

ddi_df['source'] = 'Compound::' + ddi_df[['drugbank_id']]
ddi_df['target'] = 'Compound::' + ddi_df[['drugbank_id.1']]
ddi_df['edges'] = 'DRUGBANK::ddi-interactor-in::Compound:Compound'

ddi_df.to_csv('drugbank_triplets_CrelateC.tsv', sep='\t', index=False)