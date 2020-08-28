# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 15:39:20 2020
Parse drugs info for disease name and MeSH ID

@author: Tianqi
"""
# xml_file = '../ParseDrugBank/part_drug.xml'
xml_file = 'C:/PhD-UMN/intern/Drugbank/full database.xml'
import collections
import xml.etree.ElementTree as etree
import pandas as pd
import os    

import json
import csv

import spacy
from scispacy.abbreviation import AbbreviationDetector
# nlp = spacy.load("en_core_sci_sm")
nlp = spacy.load("en_ner_bc5cdr_md")

#%%
cnt = 0
rows = list()
ns = '{http://www.drugbank.ca}'
protein_rows = list()
inchikey_template = "{ns}calculated-properties/{ns}property[{ns}kind='InChIKey']/{ns}value"
inchi_template = "{ns}calculated-properties/{ns}property[{ns}kind='InChI']/{ns}value"
for event, elem in etree.iterparse(xml_file, events=('start','end')): ### iterate all elements
    ##### find </drug type='biotech'> element, event='end' is corresponding to event ='start', but elemnt size is
    #### mostly dependent on 'end'
    if event == 'end' and '{http://www.drugbank.ca}drug' == elem.tag and 'type' in elem.attrib:   
        
        cnt += 1 
        assert elem.tag == ns + 'drug'
        drugbank_id = elem.findtext(ns + "drugbank-id[@primary='true']")
        discription_text = elem.findtext(ns + 'indication')
        
        disease_doc = nlp(discription_text)
        ents = list(disease_doc.ents)
        disease = []
        for ent in disease_doc.ents:
            if ent.label_ == "DISEASE":
                assert ent.label_ == "DISEASE"
                dis_text = ent.text.lower()
                disease.append(dis_text)
                # print(ent.text, ent.start_char, ent.end_char, ent.label_)
        disease = list(set(disease))
        for idx in range(len(disease)):      
            row = collections.OrderedDict()
            row['disease'] = disease[idx]            
            row['drugbank_id'] = drugbank_id
            row['cas_num'] = elem.findtext(ns + "cas-number") 
            row['type'] = elem.get('type')        
            row['name'] = elem.findtext(ns + "name")            
            row['indication'] = discription_text
            rows.append(row)
        # elem.clear()
    if cnt == 200:
        break
    
# for child in elem:            
#     print(child.tag)
#     print(child.text)

#%%
columns = ['drugbank_id', 'name', 'cas_num', 'type', 'disease','indication']
disease_df = pd.DataFrame.from_dict(rows)[columns]
path = os.path.join(os.getcwd(), 'drugbank_compound_disease_my1.csv')
#protein_df.to_csv(path, sep='\t', index=False)
disease_df.to_csv(path, sep='\t', index=False)
#%% get MeshID file from CTD_disease vocabulary
MeshID_file = './CTD_diseases.tsv'
MeshID_df = pd.read_csv(MeshID_file, sep="\t", skiprows = 29, 
                        names = ['DiseaseName','DiseaseID','AltDiseaseIDs','Definition', 'ParentIDs',\
                                 'TreeNumbers','ParentTreeNumbers','Synonyms','SlimMappings'])
#
# Mesh_D_list = MeshID_df.values.tolist()
MeshID_df1 = MeshID_df[['DiseaseName', 'DiseaseID']] 
MeshID_df1.rename(columns={'DiseaseID': 'MeSHID', 'DiseaseName': 'disease'}, inplace=True)
MeshID_df1['disease'] = MeshID_df1['disease'].str.lower() 

#%%
MeshID_df = pd.read_csv('./disease_id.tsv', sep="\t", 
                        names = ['disease','MeSHID'])
# merge uniprot mapping with protein_df
disease_Mesh_df = disease_df.merge(MeshID_df, how='inner')

path = os.path.join(os.getcwd(), 'drugbank_compound_disease_my2.tsv')
disease_Mesh_df.to_csv(path, sep='\t', index=False)
#%%
path = os.path.join(os.getcwd(), 'disease_id.csv')
MeshID_df1.to_csv(path, sep='\t', index=False)
#%%
path = os.path.join(os.getcwd(), 'drugbank_compound_disease_my1.tsv')
disease_df_read = pd.read_csv(path, sep="\t", names = columns)

#%%
Chemical_disease_file = './CTD_chemicals_diseases.tsv'
Chem_disease_df = pd.read_csv(Chemical_disease_file, sep="\t", skiprows = 29, 
                        names = ['ChemicalName','ChemicalID','CasRN','DiseaseName','DiseaseID',\
                                 'DirectEvidence','InferenceGeneSymbol','InferenceScore',\
                                'OmimIDs','PubMedIDs'])
#%%
# Mesh_D_list = MeshID_df.values.tolist()
Chem_disease_df_new = Chem_disease_df[['CasRN', 'DiseaseName', 'DiseaseID']] 
Chem_disease_df_new.rename(columns={'CasRN': 'cas_num', 'DiseaseName': 'disease', 'DiseaseID': 'MeshID'}, inplace=True)
Chem_disease_df_new['disease'] = Chem_disease_df_new['disease'].str.lower()
path = os.path.join(os.getcwd(), 'chem_disease_id.csv')
Chem_disease_df_new.to_csv(path, sep='\t', index=False)

#%%
disease_Mesh_df_3 = disease_df.merge(Chem_disease_df_new, how='inner')

path = os.path.join(os.getcwd(), 'drugbank_compound_disease_my3.tsv')
disease_Mesh_df_3.to_csv(path, sep='\t', index=False)