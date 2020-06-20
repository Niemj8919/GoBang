## Author: Wu Bolun
## email: bowenwu@sjtu.edu.cn
## date: 2020.6.5

import numpy as np
import torch
from torch import nn, optim
from torch.utils import data


class MalwareDataset(data.Dataset):
    self.path = 'data'
    def __init__(self, mode):
        ''' 
        mode: 'train' or 'val'
        '''

        self.mode = mode
        if mode == 'val':
            self.mode = 'test'

        self.MalwareData = []

        with open(os.path.join(self.path, '{}.json'.format(self.mode)), 'r') as f:
            train_or_test = json.load(f)
        train_or_test_md5 = []
        for item in train_or_test:
            train_or_test_md5.append(item['md5'])
        
        # vectors
        with open('APT_Vector.json', 'r') as f:
            apt_vector = json.load(f)
        
        for item in apt_vector:
            if item['md5'] in train_or_test_md5:
                info = {}
                info['vector'] = item['vector']
                info['type'] = 1
                self.MalwareData.append(info)
        
        print('APT {}: {}.'.format(mode, len(self.MalwareData)))

        with open('Malware_Vector.json', 'r') as f:
            malware_vector = json.load(f)
        
        if self.mode == 'train':
            for index in range(745): # 0: 744
                info = {}
                info['vector'] = malware_vector[index]['vector']
                info['type'] = 0
                self.MalwareData.append(info)
        elif self.mode == 'test':
            for index in range(745, 945): # 745: 944
                info = {}
                info['vector'] = malware_vector[index]['vector']
                info['type'] = 0
                self.MalwareData.append(info)

        print('Total {}: {}.'.format(mode, len(self.MalwareData)))
    
    def __len__(self):
        return len(self.MalwareData)
    
    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        
        data = self.MalwareData[idx]
        return {
            'vector': torch.from_numpy(np.asarray(data['vector'])),
            'type': torch.tensor(data['type'])
        }
