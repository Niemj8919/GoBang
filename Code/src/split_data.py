import json
import os


PATH = '/home/ISCOM/code/src/apt_500_gene'
STORE = '/home/ISCOM/code/src/apt_500_gene/data'

def split(family, train_num, apt_dict):
    train = []
    test = []

    md5s = list(apt_dict.keys())
    md5s_train = md5s[:train_num]
    md5s_test = md5s[train_num:]

    print('{} train:{}, test{}.'.format(family, len(md5s_train), len(md5s_test)))
    for md5 in md5s_train:
        info = {}
        info['md5'] = md5
        info['family'] = family
        info['gene'] = apt_dict[md5]
        train.append(info)
    
    for md5 in md5s_test:
        info = {}
        info['md5'] = md5
        info['family'] = family
        info['gene'] = apt_dict[md5]
        test.append(info)
    
    return train, test


if __name__ == '__main__':

    train_data = []
    test_data = []

    for filename in os.listdir(PATH):
        if '.json' not in filename:
            continue
        num = filename.split('.')[0].split('_')[1]
        if int(num) < 5:
            continue

        family = filename.split('.')[0].split('_')[0]    
        with open(os.path.join(PATH, filename), 'r') as f:
            apt_dict = json.load(f)
        
        if family == 'Donot':
            train, test = split(family, 110, apt_dict)
        elif family == '双尾蝎':
            train, test = split(family, 10, apt_dict)
        elif family == '毒云藤':
            train, test = split(family, 47, apt_dict)
        elif family == '海莲花':
            train, test = split(family, 13, apt_dict)
        elif family == '盲眼鹰':
            train, test = split(family, 26, apt_dict)
        elif family == '黑凤梨':
            train, test = split(family, 31, apt_dict)
        else:
            train = []
            test = []
            for md5 in apt_dict:
                info = {}
                info['md5'] = md5
                info['family'] = family
                info['gene'] = apt_dict[md5]
                train.append(info)
            print('{} train:{}.'.format(family, len(train)))
        
        train_data += train
        test_data += test
    
    print('train: {}, test: {}.'.format(len(train_data), len(test_data)))
    with open(os.path.join(STORE, 'train.json'), 'w') as f:
        json.dump(train_data, f)
    with open(os.path.join(STORE, 'test.json'), 'w') as f:
        json.dump(test_data, f)       



        

        
        
        
