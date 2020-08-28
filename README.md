### Summer Intern project @ Novartis
# Slim Drug Repurposing Knowledge Graph
Drug repurposing holds the potential to bring medications with known safety profiles to new patient populations. Knowledge graphs encode structured information of entities and relations, and knowledge graph completion aims to perform link prediction between entities. Therefore, Drug Repurposing Knowledge Graph (DRKG) provides a comprehensive biological knowledge graph to realize drug repurposing. 

Our slim DRKG includes compounds, diseases, genes, side effects and symptoms from three existing databases, which are [DrugBank](https://www.drugbank.ca/releases/latest), [Hetionet](https://het.io/) and [GNBR](https://pubmed.ncbi.nlm.nih.gov/29490008/). It includes 56,021 entities belonging to 5 entity-types; and 2,307,048 triplets belonging to 57 edge-types. These 57 edge-types show a type of interaction between one of the 8 entity-type pairs (multiple types of interactions are possible between the same entity-pair), as depicted in the figure below. It also includes a bunch of notebooks about how to explore and analysis the DRKG using statistical methodologies or using machine learning methodologies such as knowledge graph embedding.

![](knowledge%20graph.png)

__Figure:__ Interactions in the slim DRKG. The number next to an edge indicates the number of relation-types for that entity-pair.

## Statistics of knowledge graph
The type-wise distribution of the entities in DRKG and their original data-source(s) is shown in following table.
|entity-type | Drugbank |	GNBR | Hetionet | Total entities|
|:---:|:---:|:---:|:---:|:---:|
|Compound |	9053 | 3180	| 1536 | 9559|
|Disease|	1749|	4565 | 136 | 4933|
|Gene	| 4247 | 25042 | 18270 | 35413|
|Side Effect|	-| - | 5701 |	5701|
|Symptom	| -	|-	|415	| 415|
|Total	|15049	| 26492 |	21866 |	56021|

The following table shows the number of triplets between different entity-type pairs in DRKG and from various data sources.

| Entity-type pair        | Drugbank | GNBR   | Hetionet | Total interactions |
| :---------------------: | :------: | :----: | :------: | :----------------: |
| (Gene, Gene)           | -                 |          62,956|       474,526    |                     537,482    |
| (Compound, Gene)       |             18,527|          39,564|          51,429  |                     109,520    |
| (Disease, Gene)        | -                 |          95,591|          27,977  |                     123,568    |
| (Compound, Compound)   |       1,332,717   | -              |            6,486 |                  1,339,203     |
| (Compound, Disease)    |             10,209|          43,077|            1,145 |                        54,431  |
| (Disease, Symptom)     | -                 | -              |            3,357 |                          3,357 |
| (Disease, Disease)     | -                 | -              |               543|                             543|
| (Compound, Side Effect)| -                 | -              |       138,944    |                     138,944    |
| Total                  |       1,361,453   |       241,188  |       704,407    |                  2,307,048     |

## Dataset and codes
The dataset under the [./data](/data/) folder contains the following part:
* all the raw data where we extracted triplets from, including drugbank full_database.xml, and hetionet edges
* ./data/embedding, a subfolder including pre-trained embeddings
* triplets.tsv, all triplets we finalized in the form of (h, r, t) triplet
* relation_glossary.tsv, a file containing glossary of the relations in our slim DRKG, and other associated information with sources (if available).

The codes component contains the following part:
* [./drugbank](/drugbank/),  a folder containing the codes how we extracted triplets from DrugBank public database
* [./hetionet](/hetionet/),  a folder containing the codes how we extracted triplets and uniform the entities in hetionet 
* [./disease_normalize](/disease_normalize/), a folder containing the codes to extract disease-relevant triplets and normalized the disease name into MESH id 
* extract_triplets_gnbr.py , the code to extract GNBR triplets from the other user-friendly dataset
* triplets_clean_up.py , the code the clean-up duplicated triplets across different databases
## Pretrained DRKG embedding
The DRKG embedding is trained using ComplEx model with dimension size of 400, there are four files:
* triple_ComplEx_entity.npy, NumPy binary data, storing the entity embedding
*	triple_ComplEx _relation.npy, NumPy binary data, storing the relation embedding
*	entities.tsv, mapping from entity_name to entity_id.
*	relations.tsv, mapping from relation_name to relation_id
To use the pretrained embedding, one can use np.load to load the entity embeddings and relation embeddings separately:
```
import numpy as np
entity_emb = np.load('./embed/DRKG_TransE_l2_entity.npy')
rel_emb = np.load('./embed/DRKG_TransE_l2_relation.npy')
```
## Tools to analyze DRKG
We analyze DRKG with some deep learning frameworks, including DGL (a framework for graph neural networks) and DGL-KE (a library for computing knowledge graph embeddings). Please follow the instructions below to install the deep learning frameworks in the platform.

### Activate environment in AWS EC2
We train the embedding with AWS EC2 p2.xlarge instance (Deep Learning AMI Ubuntu 16.04 platform), and choose conda-based PyTorch environment. We use PuTTY and WinSCP to get access to the linux instance ([AWS EC2 User Guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/putty.html)). Use the following command to activate the environment. Following the [user guide](https://docs.aws.amazon.com/dlami/latest/devguide/dlami-dg.pdf) (p.20 – p.27) to setup Jupyter server.

```
source activate pytorch_latest_p36
```

### Install PyTorch
Currently all notebooks use PyTorch as Deep Learning backend. Currently, the [dglke_predict](https://dglke.dgl.ai/doc/predict.html) command only support torchvision<=0.6.0, so please install PyTorch with the following command. 

```
conda install pytorch torchvision cudatoolkit=10.1 -c pytorch
pip install torch==1.5.0+cu101 torchvision==0.6.0+cu101 -f https://download.pytorch.org/whl/torch_stable.html
```

To install other versions of PyTorch, please go to [Install PyTorch](https://pytorch.org/).
### Install DGL
Please install [DGL](https://github.com/dmlc/dgl) (a framework for graph neural networks) with the following command. It installs DGL with CUDA support.

```
conda install -c dglteam dgl-cuda10.1     # For CUDA 10.1 Build 
```

To install other versions of DGL, please go to [Install DGL](https://docs.dgl.ai/en/latest/install/index.html).
### Install DGL-KE
If you want to train the model with notebooks and perform link prediction with [DGL-KE](https://github.com/awslabs/dgl-ke), you need to install both DGL and DGL-KE package, and follow the command below.

```
git clone https://github.com/awslabs/dgl-ke.git
cd dgl-ke/python
python3 setup.py install
```

To install DGL-KE for different CUDA build, please go to [install DGL-KE](https://dglke.dgl.ai/doc/install.html)

## Knowledge graph embedding analysis
We split the edge triplets in training, validation and test sets as follows 90%, 5%, and 5% and train the KGE model as shown in following notebook.

[train_triplets_embedding.ipynb](https://github.com/whoeverknows/slimDRKG_intern/blob/master/train_triplets_embeddings.ipynb)

## Drug Repurposing Examples Using Pretrained Model
We use dglke_predict command (in DGLKE library) to perform link prediction, which aims to predict the missing h or t for a relation fact triplet (h,r,t). We present a drug repurposing example of using pretrained DRKG model. In the example, we used two of Novartis AG's top 10 drugs based on revenue in 2019, Entresto and Gilenya. For each drug, we predict the missing compound_treat_disease tails; and get the top ranked disease. Link prediction details are shown in the following notebook. 

[Entity Prediction for Drug Re-purpose.ipynb](https://github.com/whoeverknows/slimDRKG_intern/blob/master/Entity%20Prediction%20for%20Drug%20Re-purpose.ipynb)

### Link Prediction Result
For [Entresto](https://www.drugbank.ca/unearth/q?utf8=%E2%9C%93&searcher=drugs&query=Entresto), [Sacubitril](https://www.drugbank.ca/drugs/DB09292) is used in combination with [Valsartan](https://www.drugbank.ca/drugs/DB00177), serving as a prodrug neprilysin inhibitor to reduce the risk of cardiovascular events in patients with chronic heart failure (NYHA Class II-IV) and reduced ejection fraction. The top ranked diseases that we predicted are listed as: 
- Sacubitril: congenital pain insensitivity, congenital, Hypothermia, Retinal Diseases, Overactive Urinary Bladder, Kidney Diseases, Diabetes Mellitus.
- Valsartan: hypertension, abdominal aortic aneurysm, diabetes mellitus. 

For [Gilenya](https://www.drugbank.ca/drugs/DB08868), Fingolimod is a sphingosine 1-phosphate receptor modulator for the treatment of relapsing-remitting multiple sclerosis. It was developed by Novartis and initially approved by the FDA in 2010. The top ranked diseases that we predicted are listed as:

- Fingolimod: Muscular Diseases, Nausea, Van der Woude syndrome, Parkinson Disease, Neoplasms , Optic Nerve Diseases, Metabolic Diseases, Cholestasis
