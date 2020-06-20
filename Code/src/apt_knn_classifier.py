import os
import json
import argparse

GENE_JSON_PATH = '/home/ISCOM/code/src/apt_500_gene/data/'

def shared_genes(gene_1, gene_2):
    return len(set(gene_1) & set(gene_2))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--paramk', type=int, default=5)
    args = parser.parse_args()
    
    K = args.paramk

    # read genes from json
    with open(os.path.join(GENE_JSON_PATH, 'train.json'), 'r') as f:
        APT_Dataset = json.load(f)
    with open(os.path.join(GENE_JSON_PATH, 'test.json'), 'r') as f:
        TEST_Dataset = json.load(f)

    # knn
    predict_right_count = 0
    for test_sample in TEST_Dataset:
        shared_genes_list = []
        for sample in APT_Dataset:
            info = {}
            info['share'] = shared_genes(test_sample['gene'], sample['gene'])
            info['family'] = sample['family']
            shared_genes_list.append(info)

        def _sort_key_func(item):
            return item['share']
        shared_genes_list.sort(key=_sort_key_func, reverse=True)

        first_k_family = []
        for j in range(K):
            first_k_family.append(shared_genes_list[j]['family'])
        
        predicted_family = max(first_k_family, key=first_k_family.count)

        print('Real: {}, Predicted: {}'.format(test_sample['family'], predicted_family))
        if predicted_family == test_sample['family']:
            predict_right_count += 1

    print('Accuray: {}.'.format(predict_right_count/len(TEST_Dataset)))



