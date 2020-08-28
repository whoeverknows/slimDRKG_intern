# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 15:26:42 2020
Combine mesh-id/name from different sources
@author: Tianqi
"""

import pandas as pd
import os    

import json
import csv

#%% get hetnet disease terms (doid and name)
slim_disease_df = pd.read_csv('./slim-terms.tsv', delimiter='\t')
slim_disease_df = slim_disease_df[['doid','name']]
slim_disease_df['name_lower'] = [x.lower() for x in slim_disease_df.name]

do_slim_to_mesh_df = pd.read_csv('./DO-slim-to-mesh.tsv', delimiter='\t')
do_slim_to_mesh_df.rename(columns={'doid_code':'doid', 'doid_name':'name_lower'}, inplace=True)
#%% 
#merge with doid_to_mesh file (from Disease Oncology old version on https://github.com/dhimmel/disease-ontology)
xref_old_df = pd.read_csv('./xrefs.tsv', delimiter='\t')

xref_df = xref_old_df[   
    xref_old_df.resource.map(lambda x: x == 'MSH')
]
xref_df['name_lower'] = [x.lower() for x in xref_df.doid_name]
xref_df.rename(columns={'doid_code':'doid', 'resource_id':'mesh_id'}, inplace=True)
xref_df = xref_df[['doid','name_lower','mesh_id']]

df_merge2_old = pd.merge(slim_disease_df[['doid','name_lower']], xref_df, how = 'left', on = ['doid','name_lower'])
df_merge3_old = pd.merge(df_merge2_old, do_slim_to_mesh_df, how = 'outer',
                     on = ['doid','name_lower'])
df_merge3_old['mesh_id'] = df_merge3_old[df_merge3_old.columns[2:4]].apply(
    lambda x: ','.join(x.dropna().astype(str).drop_duplicates()), axis=1)

df_merge3_old.to_csv('hetnet_doid_to_mesh.tsv', index=False, sep='\t')







