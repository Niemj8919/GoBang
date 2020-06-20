import argparse
import json
import os
import sys

import pandas as pd

import r2pipe
from py2neo import Graph, Node, Relationship
from py2neo.matching import *


class APTFamilyGeneExtractor():
    ''' Extract/Convert/Store Genes of a given file '''
    def __init__(self, database=False, username='', password='', family=None):
        self.gene_set = []
        self.database = None
        self.family = family

        if database == True:
            self.login_database(username, password)

    
    def login_database(self, username, password):
        ''' connect to neo4j graph database '''
        try:
            self.database = Graph("http://localhost:7474", auth=(username, password))
        except:
            raise Exception('Authentication Failed.')

        
    def extract(self, path):
        ''' Extract Genes of a file
        Args:
            path - path of given file
        '''
        print('[Extracting]: {}'.format(path))
        self.file_path = path
        self.gene_set.clear()

        filename = self.file_path.split('/')[-1]
        gene_matched = NodeMatcher(self.database).match('Sample', md5=filename).first()
        if gene_matched:
            print('This sample has been extracted into database already.')
            return None

        r2 = r2pipe.open(path, flags=['-2']) # disable stderr message
        r2.cmd('aaaa')
        
        # get basic blocks
        basic_blocks = []
        functions = []
        afl_list = r2.cmdj('aflj')
        if afl_list is None:
            print('Get function list error.')
            return None

        for func in afl_list:
            functions.append(func['name'])
        
        for func in functions:
            r2.cmd('s {}'.format(func))
            bbs = r2.cmd('pdbj @@b').split('\n')
            for index in range(0, len(bbs)-1):
                bb = json.loads(bbs[index]) # basic block in json
                if bb not in basic_blocks:
                    basic_blocks.append(bb)

        # TYPE 2
        # select functions flag
        # r2.cmd('fs functions')
        # get basic blocks from all functions
        # results = r2.cmd('pdbj @@ *').split('\n')
        # results.remove('')

        # remove the same basic block
        # blocks = set()
        # for bb in basic_blocks:
        #     blocks.add(bb)
        # blocks = list(blocks)

        # split block with calling user function
        for index in range(len(basic_blocks)):
            gene = []
            for code in basic_blocks[index]:
                op_type = code['type']
                if op_type == 'invalid' or op_type == 'ill':
                    continue

                if 'call' in op_type: # call or ucall ?
                    call_usr_func = False
                    for func in functions:
                        if func in code['disasm']:
                            call_usr_func = True
                            break
                    if call_usr_func:
                        gene.append(code)
                        if len(gene) > 1:
                            self.gene_set.append(gene)
                        gene = []
                        continue

                gene.append(code)

            if len(gene) > 1:
                self.gene_set.append(gene)
        
        print('[Gene set size]: {}'.format(len(self.gene_set)))
        return True
    

    def store(self, mode='opc'):
        ''' store genes to neo4j database
        Args:
            mode   'opc'       - opcode
                   'api'       - api
                   'sopc'    - simple opcode
        '''

        if self.database is None:
            print('Neo4j database not connected.')
            return
        if mode not in ['opc', 'api', 'sopc']:
            print('Mode must be in opc/api/sopc .')
            return
        if len(self.gene_set) < 10:
            print('[Store failed]: The file may be packed, not stored.')
            return

        filename = self.file_path.split('/')[-1]
        sample_node = Node(
            'Sample', 
            md5=filename, 
            family=self.family_dict[filename])

        # opcode format
        if mode == 'opc':
            
            self.database.create(sample_node)

            gene_op_set = []
            for gene in self.gene_set:
                gene_op = []
                for ins in gene:
                    if ins['type'] == 'null':
                        continue
                    gene_op.append(ins['type'])
                if gene_op not in gene_op_set:
                    gene_op_set.append(gene_op)
            
            print('[Storing]: geneop_set size {}.'.format(len(gene_op_set)))
            # establish relationships between sample_node and gene_node
            for gene in gene_op_set:
                gene_str = '/'.join(gene)
                # print(gene_str)
                self._establish_relationship(sample_node, gene_str)

        # simple opcode format
        elif mode == 'sopc':
            self.databse.create(sample_node)

            gene_sop_set = []
            for gene in self.gene_set:
                gene_sop = []
                for ins in gene:
                    if ins['type'] == 'null':
                        continue
                    if ins['type'] != 'mov' and ins['type'] != 'lea':
                        gene_sop.append(ins['type'])
                if len(gene_sop) == 0:
                    continue
                if gene_sop not in gene_sop_set:
                    gene_sop_set.append(gene_sop)
            
            # establish relationships between sample_node and gene_node
            for gene in gene_sop_set:
                gene_str = '/'.join(gene)
                self._establish_relationship(sample_node, gene_str)

        # api format
        elif mode == 'api':
            # TODO API FORMAT
            pass


    def _establish_relationship(self, sample_node, gene_str):
        gene_matched = NodeMatcher(self.database).match('Gene', content=gene_str).first()
        if gene_matched == None:
            gene_node = Node('Gene', content=gene_str)
            self.database.create(gene_node)
            rel = Relationship(sample_node, 'CONTAINS', gene_node)
            self.database.create(rel)
        else:
            rel = Relationship(sample_node, 'CONTAINS', gene_matched)
            self.database.create(rel)


    

