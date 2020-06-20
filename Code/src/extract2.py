import os

from gene_new import APTFamilyGeneExtractor, MalwareGeneExtractor
from utils import *


APTS = ['APT28', 'DarkHotel', 'FIN7', 'Hangover', 'Lazarus', 'MuddyWater', '军刀狮', '响尾蛇', '拍拍熊',\
           '海莲花', '蔓灵花', '黑凤梨', 'APT34', 'Donot', 'Gorgon', 'Hermit', 'Mallu_Cyber_Soldiers', '人面马',\
           '双尾蝎', '奇幻熊', '毒云藤', '盲眼鹰', '黄金鼠']        
# APTS = ['双尾蝎', '奇幻熊', '毒云藤', '盲眼鹰', '黄金鼠']     

SOURCE = [
    [
        '/home/data_disk/iscom_data/sample/20190725/c2_info.xlsx',
        '/home/data_disk/iscom_data/unpacked_sample/20190725_unpacked'
    ],
    [
        '/home/data_disk/iscom_data/sample/20190801/c2_info.xlsx',
        '/home/data_disk/iscom_data/unpacked_sample/20190801_unpacked'
    ],
    [
        '/home/data_disk/iscom_data/sample/20190808/c2_info.xlsx',
        '/home/data_disk/iscom_data/unpacked_sample/20190808_unpacked'
    ],
    [
        '/home/data_disk/iscom_data/sample/20190822/c2_info.xlsx',
        '/home/data_disk/iscom_data/unpacked_sample/20190822_unpacked'
    ],
    [
        '/home/data_disk/iscom_data/sample/20190829/c2_info.xlsx',
        '/home/data_disk/iscom_data/unpacked_sample/20190829_unpacked'
    ],
]
if __name__ == '__main__':

    '''
    for apt in APTS:
        apt_dir = '/home/data_disk/iscom_data/unpacked_sample/apt_unpacked/{}'.format(apt)

        extractor = APTFamilyGeneExtractor(family=apt)
        extractor.extract(apt_dir)
    
    '''
    for data in SOURCE:
        extractor = MalwareGeneExtractor(family_csv=data[0])
        extractor.extract(data[1])
