# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 09:37:30 2020

@author: Tianqi
"""
import pandas as pd
import numpy as np
import os

hetnet_triplet_df = pd.read_csv('../data/hetionet-v1.0-edges.sif', sep="\t",
                        names = ['source','metaedge','target'])

triplets = hetnet_triplet_df.values.tolist()
num_triplets = len(triplets)

#%% get hetionet relation type
rel_type = {}
for idx in range(1, len(triplets)):
    rel_key = triplets[idx][1]
    if rel_type.get(rel_key, None) is None:
        rel_type[rel_key] = []
    rel_type[rel_key].append(idx) 

#%%
# required_metaedge = ['CbG', 'CcSE', 'CdG', 'CpD', 'CrC', 'CtD', 'CuG', 'DaG', 'DdG', 'DpS',
#                      'DrD', 'DuG', 'GcG', 'GiG', 'Gr>G']
required_metaedge = ['CbG', 'CcSE', 'CdG', 'CrC', 'CuG', 'GcG', 'GiG', 'Gr>G']
rows_df = hetnet_triplet_df[
    hetnet_triplet_df.metaedge.map(lambda x: x in required_metaedge)]
rows_df1 = rows_df.drop_duplicates()
# rows_df.to_csv('hetnet_triplets_slim.tsv', sep = '\t', index = False)
rows_df.to_csv('../data/hetnet_triplets_other.tsv', sep = '\t', index = False)
#%% load hetnet disease meshid to doid file
path = '../NER/hetnet_doid_to_mesh_1.tsv'
doid_mesh_df = pd.read_csv(path, delimiter='\t')
doid_mesh_df = doid_mesh_df[['doid','mesh_id']]
doid_mesh_df['mesh_id'] = 'MESH:' + doid_mesh_df['mesh_id']  # change disease DO-id to Mesh ID
doid_mesh_df['mesh_id'] = doid_mesh_df['mesh_id'].astype(str)

#%% get disease-related triplets, and convert doid to meshid
disease_metaedge = ['CpD', 'CtD',  'DaG', 'DdG', 'DpS', 'DrD', 'DuG']
rows_df = hetnet_triplet_df[
    hetnet_triplet_df.metaedge.map(lambda x: x in disease_metaedge)]

rows_df.to_csv('hetnet_triplets_disease.tsv', sep = '\t', index = False)
        
for idx in range(len(rows_df)):
    key1 = rows_df.loc[idx][0].split('::')
    key2 = rows_df.loc[idx][2].split('::')
    if 'Disease' in key1:        
        idx1 =  doid_mesh_df.doid.isin([key1[1]])
        new_key = doid_mesh_df.mesh_id[idx1].values.tolist()        
        if new_key[0] != 'nan': 
            rows_df.loc[idx][0] = 'Disease::' + new_key[0]
        
    if 'Disease' in key2:
        idx1 =  doid_mesh_df.doid.isin([key2[1]])
        new_key = doid_mesh_df.mesh_id[idx1].values.tolist()        
        if new_key[0] != 'nan': 
            rows_df.loc[idx][2] = 'Disease::' + new_key[0]   
        
rows_df.to_csv('../data/hetnet_triplets_disease_mesh.tsv', sep = '\t', index = False)

rows_df1 = rows_df.drop_duplicates()
#%%
a = rows_df.duplicated()
for i in range(len(a)):
    if a[i] == True:
        print(i)
        print(rows_df.loc[i])
