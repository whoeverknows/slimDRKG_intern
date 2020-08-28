# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 17:18:47 2020

@author: Tianqi
"""
import os
import pandas as pd
import numpy as np
import csv
#%%
###### read hetnet disease-related triplets file
hetnet_disease_df = pd.read_csv('./heotinet/hetnet_triplets_disease_mesh.tsv', sep = '\t')
hetnet_disease_df = hetnet_disease_df.drop_duplicates()
hetnet_other_df = pd.read_csv('./heotinet/hetnet_triplets_other.tsv', sep = '\t')
hetnet_other_df = hetnet_other_df.drop_duplicates()

hetnet_df = pd.concat([hetnet_other_df, hetnet_disease_df])
hetnet_df = hetnet_df.drop_duplicates().reset_index(drop=True)

# combine drugbank triplets which parsing from DrugBank full_database.xml
drugbank_CtD_df = pd.read_csv('./NER/drugbank_triplets_CtreatD_mesh.tsv', sep = '\t')
drugbank_CtD_df= drugbank_CtD_df[['source','edges', 'target']].rename(columns={'edges': 'metaedge'})
drugbank_CG_df = pd.read_csv('./ParseDrugBank/drugbank_triplets_CtargetG.tsv', sep = '\t')
drugbank_CG_df= drugbank_CG_df[['source','edges', 'target']].rename(columns={'edges': 'metaedge'})
drugbank_CiC_df = pd.read_csv('./ParseDrugBank/drugbank_triplets_CrelateC.tsv', sep = '\t')
drugbank_CiC_df= drugbank_CiC_df[['source','edges', 'target']].rename(columns={'edges': 'metaedge'})

drugbank_df = pd.concat([drugbank_CtD_df, drugbank_CG_df, drugbank_CiC_df])
drugbank_df = drugbank_df.drop_duplicates().reset_index(drop=True)


new_df = pd.merge(hetnet_df, drugbank_df, on = ['source','target'], suffixes=('_hetnet', '_db'), how = 'outer')
new_df = new_df.fillna('')        
new_df = new_df.drop_duplicates()
new_df['metaedge'] = new_df[['metaedge_hetnet','metaedge_db']].apply(
    lambda x: '{}'.format(x[1] if x[0]=='' else x[0]), axis=1)
df = new_df[['source', 'metaedge','target']]
df = df.drop_duplicates().reset_index(drop=True)
# duplicates = df[df.duplicated(keep=False)]
# df.to_csv('./triplets_all_updated.tsv', sep = '\t', index = False, header=False)

#%% combined with GNBR dataset from DRKG
gnbr_df = pd.read_csv('../data/GNBR_slim_triplets', sep = '\t', names = ['source','metaedge','target'] )
# df =  pd.read_csv('./triplets_all_updated.tsv', sep = '\t', names = ['source','metaedge','target'] )
new_df = pd.merge(df, gnbr_df, on = ['source','target'], suffixes=('_dbhet', '_gnbr'), how = 'outer')
new_df = new_df.fillna('')        
new_df = new_df.drop_duplicates()

new_df['metaedge'] = new_df[['metaedge_dbhet','metaedge_gnbr']].apply(
    lambda x: '{}'.format(x[1] if x[0]=='' else x[0]), axis=1)
triplet_df = new_df[['source', 'metaedge','target']]
triplet_df= triplet_df.drop_duplicates().reset_index(drop=True)
# triplet_df.to_csv('./triplets_all_gnbr.tsv', sep = '\t', index = False, header=False)

###### load extra compound-treat-disease pairs from Cheng Shi
df_diff = pd.read_csv('../data/slim_CtD.tsv', sep = '\t', names = ['source','metaedge','target'] )

new_df = pd.merge(triplet_df, df_diff, on = ['source','target'], suffixes=('_all', '_drkgdb'), how = 'outer')
new_df = new_df.fillna('')        
new_df = new_df.drop_duplicates()

new_df['metaedge'] = new_df[['metaedge_all','metaedge_drkgdb']].apply(
    lambda x: '{}'.format(x[1] if x[0]=='' else x[0]), axis=1)
df = new_df[['source', 'metaedge','target']]
duplicates = df[df.duplicated(keep=False)]
df = df.drop_duplicates().reset_index(drop=True)
df.to_csv('../data/triplets.tsv', sep = '\t', index = False, header=False) 
