## Author: Wu Bolun
## email: bowenwu@sjtu.edu.cn
## date: 2020.5.22

import os
import json

GENE_JSON_PATH = '/home/ISCOM/code/src/apt_500_gene/'

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

if __name__ == '__main__':

    # store vectors
    Apt_Vectors = []

    # read gene clusters (467)
    with open(os.path.join(CURRENT_DIR, 'Clustered_Genes_thres_8.json'), 'r') as f:
        Gene_Clusters = json.load(f)

    # read genes from json
    for filename in os.listdir(GENE_JSON_PATH):

        sample_num = filename.split('.')[0].split('_')[1]
        apt_family = filename.split('.')[0].split('_')[0]

        if int(sample_num) == 0:
            continue

        with open(os.path.join(GENE_JSON_PATH, filename), 'r') as f:
            current_apt_dict = json.load(f)
        
        for md5 in current_apt_dict:
            vector = list()
            for cluster_index in range(467):
                sample_gene_set = set(current_apt_dict[md5])
                cluster_set = set(Gene_Clusters['Cluster_{}'.format(cluster_index)])
                if len(sample_gene_set & cluster_set) == 0:
                    vector.append(0)
                else:
                    vector.append(1)
                
            # store
            Info = {}
            Info['md5'] = md5
            Info['type'] = 'apt'
            Info['family'] = apt_family
            Info['vector'] = vector

            Apt_Vectors.append(Info)

    print('Dumping to json...')
    with open('APT_Vector.json', 'w') as f:
        json.dump(Apt_Vectors, f)

    print('Create sample vectors done.')

            


        

        

