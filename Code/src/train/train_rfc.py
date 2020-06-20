## Author: Wu Bolun
## email: bowenwu@sjtu.edu.cn
## date: 2020.5.23

import json
import os

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

import joblib

PATH = '/home/ISCOM/code/src/apt_500_gene/data'


if __name__ == '__main__':
    # load train, test md5
    with open(os.path.join(PATH, 'train.json'), 'r') as f:
        train = json.load(f)
    with open(os.path.join(PATH, 'test.json'), 'r') as f:
        test = json.load(f)

    train_md5 = []
    test_md5 = []
    for item in train:
        train_md5.append(item['md5'])
    for item in test:
        test_md5.append(item['md5'])
    
    # load vectors
    with open('APT_Vector.json', 'r') as f:
        apt_vector = json.load(f)
    
    with open('Malware_Vector.json', 'r') as f:
        malware_vector = json.load(f)
    # print('APT sample:{}, NotAPT sample:{}.'.format(len(apt_vector), len(malware_vector)))

    # construct apt train, test dataset
    apt_train_data = []
    apt_train_target = []
    apt_test_data = []
    apt_test_target = []
    for item in apt_vector:
        if item['md5'] in train_md5:
            apt_train_data.append(item['vector'])
            apt_train_target.append(1)
        elif item['md5'] in test_md5:
            apt_test_data.append(item['vector'])
            apt_test_target.append(1)
        else:
            continue

    print('APT train: {}, APT test: {}.'.format(
        len(apt_train_data), len(apt_test_data)))

    # napt train, test dataset
    napt_data = []
    napt_target = []

    for item in malware_vector:
        napt_data.append(item['vector'])
        napt_target.append(0)

    napt_train_data = napt_data[:745]
    napt_train_target = napt_target[:745]
    napt_test_data = napt_data[745:]
    napt_test_target = napt_target[745:]
    
    print('NAPT train: {}, NAPT test: {}.'.format(
        len(napt_train_data), len(napt_test_data)))

    # combine dataset
    Xtrain = apt_train_data + napt_train_data
    Ytrain = apt_train_target + napt_train_target
    Xtest = apt_test_data + napt_test_data
    Ytest = apt_test_target + napt_test_target

    # dtc = DecisionTreeClassifier(random_state=0)
    rfc = RandomForestClassifier(random_state=0)
    # lr = LogisticRegression()

    # dtc = dtc.fit(Xtrain, Ytrain)
    rfc = rfc.fit(Xtrain, Ytrain)
    # lr = lr.fit(Xtrain, Ytrain)
    joblib.dump(rfc, "rfc_apt_detector.m")
    # dtc_score = dtc.score(Xtest, Ytest)
    predict = rfc.predict(Xtest)
    # print(len(predict))
    # rfc_score = rfc.score(Xtest, Ytest)
    # lr_score = lr.score(Xtest, Ytest)
    accuracy = accuracy_score(predict, Ytest)
    precision = precision_score(predict, Ytest)
    recall_score = recall_score(predict, Ytest)
    print('accuracy:{}, precision:{}, recall:{}'.format(accuracy, precision, recall_score))
    
    # print('Decision Tree:{}, Random Forest: {}, Logistic Regression: {}'.format(
    #         dtc_score, rfc_score, lr_score))
