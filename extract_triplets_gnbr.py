# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 13:00:26 2020

@author: Tianqi
"""
import pandas as pd
import numpy as np
#import sys
#sys.path.insert(1, '../utils')
#from utils import download_and_extract
#download_and_extract()
#%%

drkg_file = '../data/drkg.tsv'
df = pd.read_csv(drkg_file, sep="\t")
df.columns = ['source','metaedge','target']

triplets = df.values.tolist()
####### We get 5,869,293 triples, now we will split them into three files
num_triples = len(triplets)
num_triples
#%% get relation type
rel_type = {}
for idx in range(1, len(triplets)):
    rel_key = triplets[idx][1]
    if rel_type.get(rel_key, None) is None:
        rel_type[rel_key] = []
    rel_type[rel_key].append(idx) 

#%% extract GNBR dataset from DRKG
GNBR_df = df[   
    df.metaedge.map(lambda x: 'GNBR' in x.split('::') )
]

GNBR_new_df = GNBR_df[   
    GNBR_df.metaedge.map(lambda x: 'Gene:Tax' not in x.split('::') )
]
GNBR_new_df['source1'] = [x.split('::')[1] for x in GNBR_new_df.source]
GNBR_new_df['target1'] = [x.split('::')[1] for x in GNBR_new_df.target]


gnbr_df1 = GNBR_new_df.assign(target1 = GNBR_new_df['target1'].str.split(';')).explode('target1')
gnbr_df2 = gnbr_df1.assign(source1 = gnbr_df1['source1'].str.split(';')).explode('source1')

gnbr_df2 = gnbr_df2.drop_duplicates()
gnbr_df2 = gnbr_df2.reset_index(drop=True)

gnbr_df2['s-suffix'] = [x.split('::')[0] for x in gnbr_df2.source]
gnbr_df2['t-suffix'] = [x.split('::')[0] for x in gnbr_df2.target]
gnbr_df2['source1'] = gnbr_df2['s-suffix'] +'::' + gnbr_df2['source1'] 
gnbr_df2['target1'] = gnbr_df2['t-suffix'] +'::' + gnbr_df2['target1']
gnbr_df = gnbr_df2[['source1', 'metaedge', 'target1']].rename(columns={'source1': 'source', 'target1':'target'})
duplicates = gnbr_df[gnbr_df.duplicated(keep=False)]
gnbr_df = gnbr_df.drop_duplicates().reset_index(drop=True)
# gnbr_df.to_csv('./GNBR_triplets.tsv', sep = '\t', index = False, header=False)
#%% remove some compounds 
# gnbr_df = pd.read_csv('./GNBR_triplets.tsv', sep = '\t')
# gnbr_df.columns = ['source','metaedge','target']
triplets = gnbr_df.values.tolist()

entities = gnbr_df['source'].append(gnbr_df['target'], ignore_index = True).drop_duplicates()
compound_en = [x.split('::')[1] for x in entities if x.split('::')[0]=='Compound']
compound_mesh = [x for x in compound_en if x.split(':')[0]=='MESH']
compound_chebi = [x for x in compound_en if x.split(':')[0]=='CHEBI']
compound_db = [x for x in compound_en if len(x.split(':')) == 1]

disease_en = [x.split('::')[1] for x in entities if x.split('::')[0]=='Disease']
disease_omim = [x for x in disease_en if x.split(':')[0]=='OMIM']
disease_omim_df = pd.DataFrame()
disease_omim_df['omim_id'] = disease_omim

gene_en = [x.split('::')[1] for x in entities if x.split('::')[0]=='Gene']
entities_keep = compound_db + disease_en + gene_en

len(gene_en) + len(compound_en) + len(disease_en)
###########
rows = list()
for idx in range(len(triplets)):
    h = triplets[idx][0].split('::')[1]
    t = triplets[idx][2].split('::')[1]
    if (h in entities_keep) and (t in entities_keep):
        rows.append(triplets[idx])
        
gnbr_df_slim = pd.DataFrame.from_dict(rows)
gnbr_df_slim = gnbr_df_slim.drop_duplicates().reset_index(drop=True)
gnbr_df_slim.columns = ['source','metaedge','target']
gnbr_df_slim.to_csv('../data/GNBR_slim_triplets', sep = '\t', index = False, header = False)




