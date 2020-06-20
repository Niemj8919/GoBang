## Author: Wu Bolun
## email: bowenwu@sjtu.edu.cn
## date: 2020.5.21

import os
import json
import numpy as np


GENE_JSON_PATH = '/home/ISCOM/src/apt_500_gene/'
DIR = os.path.dirname(os.path.realpath(__file__))

def gene_distance(gene_1, gene_2):
    ''' Smith Waterman '''
    if not isinstance(gene_1, list):
        gene1 = gene_1.split('/')
    else:
        gene1 = gene_1
    
    if not isinstance(gene_2, list):
        gene2 = gene_2.split('/')
    else:
        gene2 = gene_2

    m = len(gene1)
    n = len(gene2)
    matrix = np.zeros((m+1, n+1))
    for i in range(1, m+1):
        for j in range(1, n+1):
            match_score = 1 if gene1[i-1] == gene2[j-1] else 0
            matrix[i][j] = max(matrix[i-1][j-1]+match_score, matrix[i][j-1], matrix[i-1][j])
    
    distance = max(m, n) - matrix[m][n]
    return distance


if __name__ == '__main__':

    # Get all genes -> GeneSet
    GeneSet = []
    for filename in os.listdir(GENE_JSON_PATH):
        sample_num = filename.split('.')[0].split('_')[1]
        if int(sample_num) == 0:
            continue
    
        with open(os.path.join(GENE_JSON_PATH, filename), 'r') as f:
            current_apt_dict = json.load(f)
        for md5 in current_apt_dict:
            GeneSet += current_apt_dict[md5]

    GeneSet = list(set(GeneSet))
    GeneSet_size = len(GeneSet)
    print('Size of gene set: {}.'.format(GeneSet_size))

    
    if 'DisMatrix.bin' not in os.listdir(DIR):
        print('DisMatrix.bin not found. Calculating DisMatrix.bin .')
        # Matrix of distance
        Distance_Matrix = np.zeros((GeneSet_size, GeneSet_size))
        for i in range(GeneSet_size):
            if i % 100 == 0:
                print(i)
            for j in range(i+1, GeneSet_size):
                Distance_Matrix[i][j] = gene_distance(GeneSet[i], GeneSet[j])
                # print(Distance_Matrix[i][j])
        print('Distance matrix constructed. Saving to DisMatrix.bin .')

        Distance_Matrix.tofile('DisMatrix.bin')
    else:
        print('DisMatrix.bin found.')
        Distance_Matrix = np.fromfile('DisMatrix.bin')
        Distance_Matrix.reshape((GeneSet_size, GeneSet_size))


    # Cluster
    GeneSet_Clustered = []
    distance_threshold = 8

    for index in range(GeneSet_size):
        if index % 1000 == 0:
            print(index)
            print('Number of clusters: {}.'.format(len(GeneSet_Clustered)))
        T = [] # average distance between current gene and every cluster

        for cluster in GeneSet_Clustered:
            average = 0
            larger_than_threshold = False

            for _index in cluster:
                distance = gene_distance(GeneSet[index], GeneSet[_index])
                if distance > distance_threshold:
                    T.append(-1)
                    larger_than_threshold = True
                    break
                average += distance

            if not larger_than_threshold:
                average /= len(cluster)
                T.append(average)
        
        if len(T) == 0:
            # no cluster now, add a new cluster
            GeneSet_Clustered.append([index])
        else:
            # get minimum
            minimum = 9999
            minimum_index = 0

            for average in T:
                if average == -1:
                    continue
                if average < minimum:
                    minimum = average
                    minimum_index = T.index(average)
            
            if minimum == 9999:
                # all -1 in T
                GeneSet_Clustered.append([index])
            else:
                GeneSet_Clustered[minimum_index].append(index)
    
    Clustered_store_dict = {}
    for index in range(len(GeneSet_Clustered)):
        Clustered_store_dict['Cluster_{}'.format(index)] = list()
        for gene_index in GeneSet_Clustered[index]:
            Clustered_store_dict['Cluster_{}'.format(index)].append(GeneSet[gene_index])
    
    with open('Clustered_Genes_thres_8.json', 'w') as f:
        json.dump(Clustered_store_dict, f, indent=1)

    print('Cluster finished. Number of clusters: {}.'.format(len(GeneSet_Clustered)))



