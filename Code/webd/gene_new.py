## Author: Wu Bolun
## email: bowenwu@sjtu.edu.cn
## date: 2020.5.19

import json
import os

import pandas as pd

import r2pipe
from py2neo import Graph, Node, Relationship
from py2neo.matching import *



class GeneExtractor():
    ''' Basic class of gene extractor '''
    def __init__(self):
        pass

    def extract(self, dir):
        pass

    def _get_raw_genes(self, file):
        ''' extract genes by radare2 '''

        # return a `list`
        return_gene_set = []

        r2 = r2pipe.open(file, flags=['-2']) # disable stderr message
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

        # split block with calling user function
        for index in range(len(basic_blocks)):
            gene = []
            for code in basic_blocks[index]:
                op_type = code['type']
                if op_type == 'invalid' or op_type == 'ill' or op_type == 'null':
                    continue

                if 'call' in op_type: # call or ucall
                    call_usr_func = False
                    for func in functions:
                        if func in code['disasm']:
                            call_usr_func = True
                            break
                    if call_usr_func:
                        gene.append(code)
                        if len(gene) > 3 and len(gene) <= 50:
                            return_gene_set.append(gene)
                        gene = []
                        continue

                gene.append(code)

            if len(gene) > 3 and len(gene) <= 30:
                return_gene_set.append(gene)

        if len(return_gene_set) < 10:
            print('File may be packed.')
            return None

        return return_gene_set


    def _opcode(self, gene):
        ''' translate raw gene to opcode format '''
        opcode_gene = []
        for code in gene:
            opcode_gene.append(code['type'])
        return opcode_gene

    def _opcode_to_str(self, op_gene):
        ''' translate opcode format gene to `str` `'''
        return "/".join(op_gene)

    def _str_to_opcode(self, str_op_gene):
        ''' translate `str` format gene to opcode format '''
        return str_op_gene.split('/')



class APTFamilyGeneExtractor(GeneExtractor):
    ''' Extract/Convert/Store Genes of a given APT sample '''
    def __init__(self, family=None):

        # store all genes of a family to count frequency
        self.Gene_set = []

        # key: sample's md5  value: `list` of genes
        self.Gene_dict = {}

        self.family = family
  
    def extract(self, dir):
        ''' Extract Genes of files in a dir
        Args:
            dir - path of given dir
        
        1. get raw genes
        2. denoise according to gene frequency in this family 
        3. store as json file

        '''

        # extract genes of the whole family
        for filename in os.listdir(dir):
            fullpath = os.path.join(dir, filename)
            print('[Extracting]: {}'.format(fullpath))
            raw_genes = self._get_raw_genes(fullpath)
            if raw_genes is not None:
                self.Gene_set += raw_genes

                # convert raw genes to opcode genes
                opcode_genes = []
                for gene in raw_genes:
                    opcode_genes.append(self._opcode_to_str(self._opcode(gene)))
                self.Gene_dict[filename] = list(set(opcode_genes))
            else:
                continue
            
                
        OpcodeGene_freq_dict = self._calc_frequency()

        def _sort_key_func(gene):
            return OpcodeGene_freq_dict[gene]

        for sample in self.Gene_dict:
            self.Gene_dict[sample].sort(key=_sort_key_func, reverse=True)
            self.Gene_dict[sample] = self.Gene_dict[sample][:400]
            print('{}: {}'.format(sample, len(self.Gene_dict[sample])))

        with open('{}_{}.json'.format(self.family, len(self.Gene_dict)), 'w') as f:
            json.dump(self.Gene_dict, f, indent=1)


    def _calc_frequency(self):
        ''' Return a frequency dict of every opcode gene '''
        OpcodeGene_set = []
        OpcodeGene_freq_dict = {}

        # get opcode-str format
        for gene in self.Gene_set:
            OpcodeGene_set.append(self._opcode_to_str(self._opcode(gene)))
        
        # calculate frequency
        for op_gene in set(OpcodeGene_set):
            OpcodeGene_freq_dict[op_gene] = OpcodeGene_set.count(op_gene)
        
        return OpcodeGene_freq_dict



class MalwareGeneExtractor(GeneExtractor):
    ''' Extract/Convert/Store Genes of a given malware(not APT) sample '''
    def __init__(self, family_csv=None):

        # every item is a dict
        # 'md5', 'family', 'gene'
        self.Gene = []

        if family_csv is not None:
            self.family_dict = self._get_family_dict(family_csv)
        else:
            self.family_dict = None


    def extract(self, dir, dump_to_json=False):
        ''' Extract Genes and store as json file '''
        for filename in os.listdir(dir):
            fullpath = os.path.join(dir, filename)
            print('[Extracting]: {}'.format(fullpath))
            raw_genes = self._get_raw_genes(fullpath)

            if raw_genes is None:
                continue
            
            # convert raw to opcode format
            opcode_genes = list()
            for gene in raw_genes:
                opcode_genes.append(self._opcode_to_str(self._opcode(gene)))
            
            # calculate frequency
            freq_dict = dict()
            for op_gene in set(opcode_genes):
                freq_dict[op_gene] = opcode_genes.count(op_gene)
            
            # sort by freqency
            opcode_genes = list(set(opcode_genes))

            def _sort_key_func(gene):
                return freq_dict[gene]
            
            opcode_genes.sort(key=_sort_key_func, reverse=True)
            opcode_genes = opcode_genes[:400]

            info = {}
            info['md5'] = filename
            info['family'] = self.family_dict[filename] if self.family_dict is not None else ''
            info['gene'] = opcode_genes

            self.Gene.append(info)
        
        if dump_to_json: 
            print('Dumping to json file...')
            with open('{}.json'.format(dir.split('/')[-1]), 'w') as f:
                json.dump(self.Gene, f, indent=1)


    def _get_family_dict(self, csv_path):
        df = pd.read_excel(csv_path)
        family_dict = {}

        # some excel don't have column names
        family_dict[df.columns.values[3]] = df.columns.values[0]
        for index in range(len(df)):
            family_dict[df.iloc[index, 3]] = df.iloc[index, 0]

        return family_dict
