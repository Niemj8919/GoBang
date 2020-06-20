import json
import os
import shutil
import subprocess

import numpy as np

import joblib
from gene_new import MalwareGeneExtractor
from py2neo import Graph, Node, Relationship
from py2neo.matching import *

UNPACK_PATH = '/home/ISCOM/result'


def vector(gene_list):

    with open('/home/ISCOM/code/src/Clustered_Genes_thres_8.json', 'r') as f:
        Gene_Clusters = json.load(f)

    vector = list()

    for cluster_index in range(467):
        gene_set = set(gene_list)
        cluster_set = set(Gene_Clusters['Cluster_{}'.format(cluster_index)])
        if len(gene_set & cluster_set) == 0:
            vector.append(0)
        else:
            vector.append(1)
            
    return vector


def knn(gene_list):
    k = 10

    def _shared_genes(gene_1, gene_2):
        return len(set(gene_1) & set(gene_2))

    with open('/home/ISCOM/code/src/apt_500_gene/data/train.json', 'r') as f:
        apt_dataset = json.load(f)
    
    shared_genes_list = []
    for sample in apt_dataset:
        info = {}
        info['share'] = _shared_genes(gene_list, sample['gene'])
        info['family'] = sample['family']
        shared_genes_list.append(info)
    
    def _sort_key_func(item):
        return item['share']
    
    shared_genes_list.sort(key=_sort_key_func, reverse=True)
    first_k_family = []
    for j in range(k):
        first_k_family.append(shared_genes_list[k]['family'])
    
    prob_dict = {}
    for fam in set(first_k_family):
        prob_dict[fam] = first_k_family.count(fam) / k
    
    return prob_dict


def connect_neo4j(sample_info):
    # neo4j
    g = Graph('http://localhost:7474', auth=('neo4j', 'nmj@12345'))

    with open('/home/ISCOM/code/src/apt_500_gene/data/train.json', 'r') as f:
        data = json.load(f)
    sample_num = len(data)

    # create sample node
    g.create(
        Node('Sample', md5=sample_info['md5'], family=sample_info['family'], type='new'))
    
    for i in range(sample_num):
        shared_gene_num = len(set(data[i]['gene']) & set(sample_info['gene']))
        if shared_gene_num > 100:
            old_node = NodeMatcher(g).match(
                'Sample', md5=data[i]['md5']).first()
            new_node = NodeMatcher(g).match(
                'Sample', md5=sample_info['md5']).first()
            g.create(
                Relationship(old_node, 'SHARE_GENES', new_node,
                             share=shared_gene_num))


def getNewSample(path, store=False):
    '''
    Args:
        path - absolute path of a file
    '''
    # unpack in docker
    subprocess.call('bash /home/ISCOM/code/unpack/docker_unpack.sh {}'.format(path), shell=True)

    # unpack error, file may be packed
    if len(os.listdir(UNPACK_PATH)) != 1:
        return {'err': 'File may be packed.'}
    
    # extract genes
    extractor = MalwareGeneExtractor(family_csv=None)
    extractor.extract(UNPACK_PATH, dump_to_json=False)
    # extract error
    if len(extractor.Gene) != 1:
        return {'err': 'Gene Extracting failed.'}
    
    sample_info = extractor.Gene[0]
    
    # construct vector
    sample_vector = vector(sample_info['gene'])

    # load random forest model
    rfc = joblib.load('/home/ISCOM/code/src/rfc_apt_detector.m')

    return_dict = {}

    # predict
    predict = rfc.predict([sample_vector])
    if predict[0] == 1:
        return_dict['detect'] = 'apt'
    elif predict[0] == 0:
        return_dict['detect'] = 'napt'

    # apt sample, try knn
    if predict[0] == 1:
        prob_dict = knn(sample_info['gene'])
        return_dict['classify'] = prob_dict

    # store
    if store == True:
        connect_neo4j(sample_info)
    
    return return_dict
    
'''
if __name__ == '__main__':
    test_path = '/home/data_disk/iscom_data/unpacked_sample/apt_unpacked/Donot/6e444898cc7cbfc6aad429ce37d2b263'
    print(getNewSample(test_path, store=False))
'''
