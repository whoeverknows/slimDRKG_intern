"""
Created on Wed Jul 22 15:39:20 2020
Parse drugs info for disease name and MeSH ID

@author: Tianqi
"""

xml_file = '../data/full database.xml'
import collections
import xml.etree.ElementTree as etree
import pandas as pd
import os    

import json
import csv
# import spacy
# from scispacy.abbreviation import AbbreviationDetector
# # nlp = spacy.load("en_core_sci_sm")
# nlp = spacy.load("en_ner_bc5cdr_md")
import requests

def query_raw(text, url="https://bern.korea.ac.kr/plain"):
    return requests.post(url, data={'sample_text': text}).json()
#%%
cnt = 0
rows = list()
ns = '{http://www.drugbank.ca}'
for event, elem in etree.iterparse(xml_file, events=('start','end')): ### iterate all elements
    ##### find </drug type='biotech'> element, event='end' is corresponding to event ='start', but elemnt size is
    #### mostly dependent on 'end'
    if event == 'end' and '{http://www.drugbank.ca}drug' == elem.tag and 'type' in elem.attrib:   
        
        cnt += 1 
        assert elem.tag == ns + 'drug'
        drugbank_id = elem.findtext(ns + "drugbank-id[@primary='true']")
        discription_text = elem.findtext(ns + 'indication')
        
        result = (query_raw(discription_text))
        if 'logits' in result:                
            
            disease = result['logits']['disease']
            text = result['text']
                           
            for idx in range(len(disease)):
                di_dict = disease[idx][0]
                if 'id' in di_dict:
                    meshId = di_dict['id'] # disease_id including MeSH ID and BERN-ID    
                else:
                    meshId = None                    

                disease_name = text[di_dict['start']:di_dict['end']] # disease_name
                disease_name = disease_name.casefold()

                row = collections.OrderedDict()
                row['disease'] = disease_name            
                row['drugbank_id'] = drugbank_id
                row['MeSHID'] = meshId
                row['cas_num'] = elem.findtext(ns + "cas-number") 
                row['type'] = elem.get('type')        
                row['name'] = elem.findtext(ns + "name")            
                rows.append(row)
                
        else:
            continue
        
        elem.clear()
        
#%%
columns = ['drugbank_id', 'name', 'cas_num', 'type', 'disease', 'MeSHID']
disease_df = pd.DataFrame.from_dict(rows)[columns]
#protein_df.to_csv(path, sep='\t', index=False)
disease_df.to_csv('drugbank_compound_disease_BERN.tsv', sep='\t', index=False, columns=columns)

#%%
meshid_df = pd.read_csv('./disease_mesh_ALL_updated.tsv',  sep="\t")
#
drugbank_disease_mesh_df = disease_df.merge(meshid_df, how = 'left', on = 'disease').drop_duplicates()
drugbank_disease_mesh_df.to_csv('./drugbank_CtD_vocabulary.tsv', sep = '\t', index = False)
drugbank_disease_mesh_df1 = drugbank_disease_mesh_df[['drugbank_id','name','disease' ,'mesh_id']].dropna()
drugbank_disease_mesh_df1 = drugbank_disease_mesh_df1.drop_duplicates()
# drugbank_disease_mesh_df1.to_csv('drugbank_CtD_vocabulary_slim.tsv', sep = '\t', index = False)
drugbank_disease_mesh_df2 = drugbank_disease_mesh_df1[['drugbank_id','mesh_id']]
dups = drugbank_disease_mesh_df2[drugbank_disease_mesh_df2.duplicated(keep=False)]
drugbank_disease_mesh_df2 = drugbank_disease_mesh_df2.drop_duplicates()
drugbank_disease_mesh_df2.to_csv('./drugbank_CtD.tsv', sep = '\t', index = False)

#%%
df = pd.read_csv('./drugbank_CtD.tsv', sep = '\t')
df =df.drop_duplicates()
# a1 = df[df.duplicated()]

ddi_df_new = df.assign(mesh_id=df['mesh_id'].str.split(',')).explode('mesh_id')
ddi_df_new = ddi_df_new.reset_index(drop=True)
ddi_df_new = ddi_df_new.drop_duplicates()

ddi_df_new['source'] = 'Compound::' + ddi_df_new[['drugbank_id']]
ddi_df_new['target'] = 'Disease::MESH:' + ddi_df_new[['mesh_id']]
ddi_df_new['edges'] = 'DRUGBANK::treats::Compound:Disease'
ddi_df_new.to_csv('../data/drugbank_triplets_CtreatD_mesh.tsv', sep = '\t', index = False)
# ddi_df_new = pd.concat([pd.Series(row['drugbank_id'], row['mesh_id'].split(',')) 
#                         for _, row in ddi_df.iterrows()]).reset_index()