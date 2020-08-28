# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 11:37:37 2020

@author: Tianqi
"""
#%% 
# load packages
import collections
import xml.etree.ElementTree as etree
import pandas     
import os    
import requests  
import csv
import gzip

import re
import io
#%%
xml_file = '../data/full database.xml'
ns = '{http://www.drugbank.ca}'
protein_rows = list()

for event, elem in etree.iterparse(xml_file, events=('start','end')): ### iterate all elements
    ##### find </drug type='biotech'> element, event='end' is corresponding to event ='start', but elemnt size is
    #### mostly dependent on 'end'
    if event == 'end' and '{http://www.drugbank.ca}drug' == elem.tag and 'type' in elem.attrib:   

        drugbank_id = elem.findtext(ns + "drugbank-id[@primary='true']")
        for category in ['target', 'enzyme', 'carrier', 'transporter']:
            proteins = elem.findall('{ns}{cat}s/{ns}{cat}'.format(ns=ns, cat=category))
            if len(proteins):                
                for protein in proteins:
                    row = {'drugbank_id': drugbank_id, 'category': category}
                    row['organism'] = protein.findtext('{}organism'.format(ns))
                    row['known_action'] = protein.findtext('{}known-action'.format(ns))
                    actions = protein.findall('{ns}actions/{ns}action'.format(ns=ns))
                    row['actions'] = '|'.join(action.text for action in actions)
                    uniprot_ids = [polypep.text for polypep in protein.findall(
                        "{ns}polypeptide/{ns}external-identifiers/{ns}external-identifier[{ns}resource='UniProtKB']/{ns}identifier".format(ns=ns))]            
                    if len(uniprot_ids) != 1:
#                        row['drugbank_gene_id'] = protein.findtext('{ns}id'.format(ns=ns))
#                        protein_rows.append(row)
                        continue
                    row['uniprot_id'] = uniprot_ids[0]
                    ref_text = protein.findall("{ns}references/{ns}articles/{ns}article/{ns}pubmed-id".format(ns=ns))
                    row['pubmed_ids'] = '|'.join(ref.text for ref in ref_text if ref.text is not None)
#                    ref_text = protein.findtext("{ns}references[@format='textile']".format(ns=ns))
#                    pmids = re.findall(r'pubmed/([0-9]+)', ref_text)
#                    row['pubmed_ids'] = '|'.join(pmids)
                    protein_rows.append(row)
        elem.clear()

        
protein_df = pandas.DataFrame.from_dict(protein_rows)          
#%%
### get GeneID mapping
response = requests.get('http://git.dhimmel.com/uniprot/data/map/GeneID.tsv.gz', stream=True)
text = io.TextIOWrapper(gzip.GzipFile(fileobj=response.raw))
uniprot_df = pandas.read_table(text, engine='python')
uniprot_df.rename(columns={'uniprot': 'uniprot_id', 'GeneID': 'entrez_gene_id'}, inplace=True)

# merge uniprot mapping with protein_df
entrez_df = protein_df.merge(uniprot_df, how='inner')       
#%%
columns = ['drugbank_id', 'category', 'uniprot_id', 'entrez_gene_id', 'organism',
           'known_action', 'actions', 'pubmed_ids']
entrez_df = entrez_df[columns]


entrez_df.to_csv('../data/drugbank_proteins_gene_compound.tsv', sep='\t', index=False)

# Number of unique genes with an interaction
len(set(entrez_df.entrez_gene_id))
# Number of unique drugs  with an interaction
len(set(entrez_df.drugbank_id))   
#%% 
####### get triplets of compound--gene pairs

entrez_df = pandas.read_csv('../data/drugbank_proteins_gene_compound.tsv', delimiter='\t')
entrez_df = entrez_df[['drugbank_id', 'category', 'entrez_gene_id']]

entrez_df['source'] = 'Compound::' + entrez_df[['drugbank_id']]
entrez_df[['entrez_gene_id']] = entrez_df[['entrez_gene_id']].astype(str)
entrez_df['target'] = 'Gene::' + entrez_df[['entrez_gene_id']]
entrez_df['edges'] = 'DRUGBANK::' + entrez_df['category'] + '::Compound:Gene'

entrez_df.to_csv('../data/drugbank_triplets_CtargetG.tsv', sep='\t', index=False)
