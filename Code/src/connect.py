## Author: Wu Bolun
## email: bowenwu@sjtu.edu.cn
## date: 2020.5.20

import argparse
import json
import os

import networkx as nx
import numpy as np

from py2neo import Graph, Node, Relationship
from py2neo.matching import *

GENE_JSON_PATH = '/home/ISCOM/code/src/apt_500_gene/data/'

if __name__ == '__main__':

    # args:
    parser = argparse.ArgumentParser()
    # store format: 'networkx' | 'neo4j'
    parser.add_argument('-f', '--format', type=str, default='networkx')
    args = parser.parse_args()

    if args.format == 'networkx':    
        Apt_G = nx.Graph()
    elif args.format == 'neo4j':
        Apt_G = Graph("http://localhost:7474", auth=('neo4j', 'nmj@12345'))
    else:
        print('Store format not found.')
        exit()

    # Get all samples and their genes

    # every item is a dict containing keys:
    # md5 - `str` sample name
    # gene - `list`
    # family - `str` 

    with open(os.path.join(GENE_JSON_PATH, 'train.json'), 'r') as f:
        data = json.load(f)
    with open(os.path.join(GENE_JSON_PATH, 'test.json'), 'r') as f:
        test = json.load(f)

    # print(len(data))

    for item in data:
        apt_family = item['family']
        md5 = item['md5']

        if args.format == 'networkx':
            Apt_G.add_node(md5, family=apt_family)
        elif args.format == 'neo4j':
            Apt_G.create(
                Node('Sample', md5=md5, family=apt_family, type='old'))

    for item in test:
        apt_family = item['family']
        md5 = item['md5']

        if args.format == 'networkx':
            Apt_G.add_node(md5, family=apt_family)
        elif args.format == 'neo4j':
            Apt_G.create(
                Node('Sample', md5=md5, family=apt_family, type='new'))

    data += test
    sample_num = len(data)
    print('Number of samples: {}.'.format(sample_num))

    # Construct similarity matrix
    Sim_Matrix = np.zeros((sample_num, sample_num))
    
    # Calculate shared genes num between every sample
    # and store to networkx or neo4j
    for i in range(sample_num):
        for j in range(i+1, sample_num):
            shared_gene_num = len(set(data[i]['gene']) & set(data[j]['gene']))
            Sim_Matrix[i][j] = shared_gene_num
            if shared_gene_num > 100:
                if args.format == 'networkx':
                    Apt_G.add_edge(data[i]['md5'],
                            data[j]['md5'],
                            weight=shared_gene_num)
                elif args.format == 'neo4j':
                    sample_node1 = NodeMatcher(Apt_G).match(
                        'Sample', md5=data[i]['md5']).first()
                    sample_node2 = NodeMatcher(Apt_G).match(
                        'Sample', md5=data[j]['md5']).first()
                    Apt_G.create(
                        Relationship(sample_node1, 'SHARE_GENES', sample_node2, 
                                     share=shared_gene_num))
                    

    if args.format == 'networkx':
        nx.write_gexf(Apt_G, 'Apt_graph_120.gexf')
